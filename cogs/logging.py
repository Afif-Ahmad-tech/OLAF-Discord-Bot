from __future__ import annotations

import discord
from discord.ext import commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


class Logging(commands.Cog):
    """Message-edit/delete and join/leave logging driven by per-guild config."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    async def _resolve(self, guild_id: int) -> discord.TextChannel | None:
        channel_id = self.data.get_setting(guild_id, "log_channel")
        if not channel_id:
            return None
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return None
        return guild.get_channel(channel_id)

    async def _safe_send(self, channel: discord.TextChannel | None, embed: discord.Embed) -> None:
        if channel is None:
            return
        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        if before.author.bot or before.guild is None:
            return
        if before.content == after.content:
            return
        channel = await self._resolve(before.guild.id)
        embed = embeds.info(
            self.settings,
            f"**Author:** {before.author.mention}\n**Channel:** {before.channel.mention if before.channel else 'unknown'}\n**Before:** {helpers.truncate(before.content or '[empty]', 512)}\n**After:** {helpers.truncate(after.content or '[empty]', 512)}",
            title="Message edited",
        )
        embed.add_field(name="Jump", value=f"[Open]({after.jump_url})", inline=False)
        await self._safe_send(channel, embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None:
            return
        channel = await self._resolve(message.guild.id)
        embed = embeds.warning(
            self.settings,
            f"**Author:** {message.author.mention}\n**Channel:** {message.channel.mention if message.channel else 'unknown'}\n**Content:** {helpers.truncate(message.content or '[empty]', 512)}",
            title="Message deleted",
        )
        await self._safe_send(channel, embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        channel = await self._resolve(member.guild.id)
        embed = embeds.info(self.settings, f"{member.mention} ({member.id}) joined.", title="Member joined")
        embed.set_thumbnail(url=member.display_avatar.url)
        await self._safe_send(channel, embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        channel = await self._resolve(member.guild.id)
        embed = embeds.warning(self.settings, f"{member.mention} ({member.id}) left.", title="Member left")
        await self._safe_send(channel, embed)

    @commands.group(name="logs", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def logs(self, ctx: commands.Context) -> None:
        embed = embeds.info(
            self.settings,
            "Subcommands: channel, disable, show",
            title="Logging settings",
        )
        await ctx.send(embed=embed)

    @logs.command(name="channel")
    @commands.has_permissions(manage_guild=True)
    async def logs_channel(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        self.data.set_setting(ctx.guild.id, "log_channel", channel.id)
        await ctx.send(embed=embeds.success(self.settings, f"Logging events will now be sent to {channel.mention}."))

    @logs.command(name="disable")
    @commands.has_permissions(manage_guild=True)
    async def logs_disable(self, ctx: commands.Context) -> None:
        self.data.set_setting(ctx.guild.id, "log_channel", None)
        await ctx.send(embed=embeds.success(self.settings, "Logging channel disabled."))

    @logs.command(name="show")
    async def logs_show(self, ctx: commands.Context) -> None:
        channel_id = self.data.get_setting(ctx.guild.id, "log_channel")
        channel = ctx.guild.get_channel(channel_id) if channel_id else None
        description = f"Channel: {channel.mention if channel else 'not set'}"
        await ctx.send(embed=embeds.info(self.settings, description, title="Current logging setup"))

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=embeds.error(self.settings, "You need the Manage Server permission for that."))
            return
        await ctx.send(embed=embeds.error(self.settings, f"Something went wrong: {error}"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Logging(bot))
