from __future__ import annotations

from typing import Optional

import discord
from discord.ext import commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


class Moderation(commands.Cog):
    """Kick, ban, mute, purge, warn, and lock utilities for server staff."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    async def cog_check(self, ctx: commands.Context) -> bool:
        if not ctx.guild:
            raise commands.NoPrivateMessage()
        if ctx.author.id == self.settings.owner_id:
            return True
        if not ctx.author.guild_permissions.manage_guild:
            raise commands.MissingPermissions(["manage_guild"])
        return True

    # ---------------- helpers ----------------
    async def _resolve_member(self, ctx: commands.Context, raw: str) -> Optional[discord.Member]:
        try:
            return await commands.MemberConverter().convert(ctx, raw)
        except commands.MemberNotFound:
            return None

    async def _log_action(self, ctx: commands.Context, title: str, member: discord.abc.User, reason: str | None) -> None:
        channel_id = self.data.get_setting(ctx.guild.id, "mod_log")
        if not channel_id:
            return
        channel = ctx.guild.get_channel(channel_id)
        if channel is None:
            return
        embed = embeds.info(
            self.settings,
            f"Target: {member.mention} ({member.id})\nReason: {reason or 'no reason provided'}",
            title=title,
        )
        embed.add_field(name="Moderator", value=f"{ctx.author.mention} ({ctx.author.id})", inline=False)
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

    # ---------------- kick ----------------
    @commands.command(name="kick")
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = "no reason provided") -> None:
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send(embed=embeds.error(self.settings, "That member's role is higher than mine."))
            return
        if member.id == ctx.author.id:
            await ctx.send(embed=embeds.error(self.settings, "You cannot kick yourself."))
            return
        try:
            await member.kick(reason=f"{ctx.author}: {reason}")
        except discord.Forbidden:
            await ctx.send(embed=embeds.error(self.settings, "I lack permission to kick that member."))
            return
        await ctx.send(embed=embeds.success(self.settings, f"{member.mention} was kicked. Reason: {reason}"))
        await self._log_action(ctx, "Member kicked", member, reason)

    # ---------------- ban ----------------
    @commands.command(name="ban")
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = "no reason provided") -> None:
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send(embed=embeds.error(self.settings, "That member's role is higher than mine."))
            return
        if member.id == ctx.author.id:
            await ctx.send(embed=embeds.error(self.settings, "You cannot ban yourself."))
            return
        try:
            await member.ban(reason=f"{ctx.author}: {reason}", delete_message_days=0)
        except discord.Forbidden:
            await ctx.send(embed=embeds.error(self.settings, "I lack permission to ban that member."))
            return
        await ctx.send(embed=embeds.success(self.settings, f"{member.mention} was banned. Reason: {reason}"))
        await self._log_action(ctx, "Member banned", member, reason)

    # ---------------- unban ----------------
    @commands.command(name="unban")
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, user_id: int, *, reason: str = "no reason provided") -> None:
        try:
            user = await self.bot.fetch_user(user_id)
        except discord.NotFound:
            await ctx.send(embed=embeds.error(self.settings, "No user with that ID exists."))
            return
        try:
            await ctx.guild.unban(user, reason=f"{ctx.author}: {reason}")
        except discord.NotFound:
            await ctx.send(embed=embeds.error(self.settings, "That user isn't banned here."))
            return
        except discord.Forbidden:
            await ctx.send(embed=embeds.error(self.settings, "I lack permission to unban users."))
            return
        await ctx.send(embed=embeds.success(self.settings, f"Unbanned {user.mention}."))
        await self._log_action(ctx, "Member unbanned", user, reason)

    # ---------------- mute ----------------
    @commands.command(name="mute")
    @commands.bot_has_permissions(moderate_members=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, duration: str = "1h", *, reason: str = "no reason provided") -> None:
        seconds = helpers.parse_duration(duration)
        if seconds is None or seconds <= 0:
            await ctx.send(embed=embeds.error(self.settings, "Duration must look like 10m, 2h, or 1d."))
            return
        if member.top_role >= ctx.guild.me.top_role:
            await ctx.send(embed=embeds.error(self.settings, "That member's role is higher than mine."))
            return
        until = discord.utils.utcnow() + discord.timedelta(seconds=seconds)
        try:
            await member.timeout(until, reason=f"{ctx.author}: {reason}")
        except discord.Forbidden:
            await ctx.send(embed=embeds.error(self.settings, "I can't timeout that member."))
            return
        await ctx.send(embed=embeds.success(self.settings, f"{member.mention} muted for {helpers.format_duration(seconds)}. Reason: {reason}"))
        await self._log_action(ctx, "Member muted", member, f"{reason} ({helpers.format_duration(seconds)})")

    # ---------------- unmute ----------------
    @commands.command(name="unmute")
    @commands.bot_has_permissions(moderate_members=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member) -> None:
        if member.is_timed_out():
            try:
                await member.timeout(None, reason=f"Unmuted by {ctx.author}")
            except discord.Forbidden:
                await ctx.send(embed=embeds.error(self.settings, "I can't lift that timeout."))
                return
        await ctx.send(embed=embeds.success(self.settings, f"{member.mention} is no longer muted."))
        await self._log_action(ctx, "Member unmuted", member, None)

    # ---------------- purge ----------------
    @commands.command(name="purge")
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int) -> None:
        if amount <= 0 or amount > 500:
            await ctx.send(embed=embeds.error(self.settings, "Pick an amount between 1 and 500."))
            return
        if not ctx.channel:
            return
        purged = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(embed=embeds.success(self.settings, f"Deleted {len(purged) - 1} messages."), delete_after=4)

    # ---------------- warn ----------------
    @commands.command(name="warn")
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = "no reason provided") -> None:
        count = self.data.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        await ctx.send(embed=embeds.warning(
            self.settings,
            f"{member.mention} now has {count} warning(s). Reason: {reason}",
            title="Warning issued",
        ))
        await self._log_action(ctx, "Member warned", member, reason)
        if count >= self.settings.max_warnings:
            try:
                await member.timeout(discord.utils.utcnow() + discord.timedelta(hours=24), reason="Too many warnings")
            except discord.Forbidden:
                pass
            await ctx.send(embed=embeds.warning(
                self.settings,
                f"{member.mention} hit {count} warnings and has been timed out for 24 hours.",
                title="Auto-moderation",
            ))

    @commands.command(name="warnings")
    async def warnings(self, ctx: commands.Context, member: discord.Member) -> None:
        records = self.data.get_warnings(ctx.guild.id, member.id)
        if not records:
            await ctx.send(embed=embeds.info(self.settings, f"{member.mention} has a clean record."))
            return
        description_lines = [
            f"{idx + 1}. {entry['reason']} (by <@{entry['moderator']}>)" for idx, entry in enumerate(records)
        ]
        embed = embeds.info(
            self.settings,
            "\n".join(description_lines),
            title=f"{len(records)} warning(s) for {member.display_name}",
        )
        await ctx.send(embed=embed)

    @commands.command(name="clearwarnings")
    async def clearwarnings(self, ctx: commands.Context, member: discord.Member) -> None:
        self.data.clear_warnings(ctx.guild.id, member.id)
        await ctx.send(embed=embeds.success(self.settings, f"Cleared warnings for {member.mention}."))

    # ---------------- lock / unlock ----------------
    @commands.command(name="lock")
    @commands.bot_has_permissions(manage_channels=True)
    async def lock(self, ctx: commands.Context, channel: discord.TextChannel | None = None) -> None:
        channel = channel or ctx.channel
        if not channel:
            return
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = False
        try:
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"Lock by {ctx.author}")
        except discord.Forbidden:
            await ctx.send(embed=embeds.error(self.settings, "I can't manage that channel."))
            return
        await ctx.send(embed=embeds.success(self.settings, f"Locked {channel.mention}."))

    @commands.command(name="unlock")
    @commands.bot_has_permissions(manage_channels=True)
    async def unlock(self, ctx: commands.Context, channel: discord.TextChannel | None = None) -> None:
        channel = channel or ctx.channel
        if not channel:
            return
        overwrite = channel.overwrites_for(ctx.guild.default_role)
        overwrite.send_messages = None
        try:
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite, reason=f"Unlock by {ctx.author}")
        except discord.Forbidden:
            await ctx.send(embed=embeds.error(self.settings, "I can't manage that channel."))
            return
        await ctx.send(embed=embeds.success(self.settings, f"Unlocked {channel.mention}."))

    # ---------------- error handling ----------------
    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=embeds.error(self.settings, "You need the Manage Server permission for that."))
            return
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send(embed=embeds.error(self.settings, "That command only works in servers."))
            return
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send(embed=embeds.error(self.settings, f"I'm missing permissions: {', '.join(error.missing_permissions)}."))
            return
        await ctx.send(embed=embeds.error(self.settings, f"Something went wrong: {error}"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot))
