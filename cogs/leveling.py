from __future__ import annotations

import random

import discord
from discord.ext import commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


class Leveling(commands.Cog):
    """Award XP for chatting, post level-up notifications, and rank members."""

    XP_MIN = 15
    XP_MAX = 25
    COOLDOWN_SECONDS = 60

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data
        self._cooldowns: dict[tuple[int, int], float] = {}

    def _is_on_cooldown(self, guild_id: int, user_id: int) -> bool:
        import time

        key = (guild_id, user_id)
        now = time.time()
        last = self._cooldowns.get(key, 0)
        if now - last < self.COOLDOWN_SECONDS:
            return True
        self._cooldowns[key] = now
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or message.guild is None:
            return
        if not message.content or len(message.content) < 4:
            return
        if not self.data.get_setting(message.guild.id, "leveling", True):
            return
        if self._is_on_cooldown(message.guild.id, message.author.id):
            return
        gain = random.randint(self.XP_MIN, self.XP_MAX)
        xp, level, leveled = self.data.add_xp(message.guild.id, message.author.id, gain)
        if leveled:
            channel_id = self.data.get_setting(message.guild.id, "level_channel")
            target = (
                message.guild.get_channel(channel_id) if channel_id else message.channel
            )
            embed = embeds.info(
                self.settings,
                f"{message.author.mention} reached **level {level}** in {message.guild.name}!",
                title="Level up",
            )
            embed.set_thumbnail(url=message.author.display_avatar.url)
            try:
                if target is not None:
                    await target.send(embed=embed)
            except discord.Forbidden:
                pass

    @commands.command(name="rank")
    async def rank(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        target = member or ctx.author
        xp, total = self.data.get_xp(ctx.guild.id, target.id)
        level = self.data.level_for_xp(total)
        next_level_xp = self.data.xp_for_level(level + 1)
        previous_level_xp = self.data.xp_for_level(level)
        progress = max(0, total - previous_level_xp)
        span = max(1, next_level_xp - previous_level_xp)
        bar = helpers.progress_bar(progress, span, length=18)
        description = (
            f"Level: **{level}**\n"
            f"Total XP: **{total}**\n"
            f"XP to next level: **{next_level_xp - total}**\n"
            f"{bar} {progress}/{span}"
        )
        embed = embeds.info(self.settings, description, title=f"{target.display_name}'s rank")
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def leaderboard(self, ctx: commands.Context, limit: int = 10) -> None:
        limit = max(1, min(25, limit))
        rows = self.data.leaderboard(ctx.guild.id, limit)
        if not rows:
            await ctx.send(embed=embeds.info(self.settings, "No chatter yet. Send some messages!"))
            return
        description_lines = []
        for index, (uid, total) in enumerate(rows, start=1):
            member = ctx.guild.get_member(uid)
            name = member.display_name if member else f"User {uid}"
            description_lines.append(f"{index}. **{name}** — {total} XP (level {self.data.level_for_xp(total)})")
        embed = embeds.info(self.settings, "\n".join(description_lines), title=f"Top {len(rows)} chatters")
        await ctx.send(embed=embed)

    @commands.group(name="leveling", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def leveling_group(self, ctx: commands.Context) -> None:
        embed = embeds.info(
            self.settings,
            "Subcommands: 	oggle, channel, show",
            title="Leveling settings",
        )
        await ctx.send(embed=embed)

    @leveling_group.command(name="toggle")
    @commands.has_permissions(manage_guild=True)
    async def leveling_toggle(self, ctx: commands.Context, enabled: bool | None = None) -> None:
        current = self.data.get_setting(ctx.guild.id, "leveling", True)
        new_state = not current if enabled is None else bool(enabled)
        self.data.set_setting(ctx.guild.id, "leveling", new_state)
        await ctx.send(embed=embeds.success(self.settings, f"Leveling is now {'on' if new_state else 'off'}."))

    @leveling_group.command(name="channel")
    @commands.has_permissions(manage_guild=True)
    async def leveling_channel(self, ctx: commands.Context, channel: discord.TextChannel | None = None) -> None:
        if channel is None:
            self.data.set_setting(ctx.guild.id, "level_channel", None)
            await ctx.send(embed=embeds.success(self.settings, "Level-up messages will now appear in the original channel."))
        else:
            self.data.set_setting(ctx.guild.id, "level_channel", channel.id)
            await ctx.send(embed=embeds.success(self.settings, f"Level-up messages will be sent to {channel.mention}."))

    @leveling_group.command(name="show")
    async def leveling_show(self, ctx: commands.Context) -> None:
        enabled = self.data.get_setting(ctx.guild.id, "leveling", True)
        channel_id = self.data.get_setting(ctx.guild.id, "level_channel")
        channel = ctx.guild.get_channel(channel_id) if channel_id else None
        description = (
            f"Enabled: **{'yes' if enabled else 'no'}**\n"
            f"Channel: {channel.mention if channel else 'fallback to original channel'}"
        )
        await ctx.send(embed=embeds.info(self.settings, description, title="Leveling settings"))

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=embeds.error(self.settings, "You need the Manage Server permission for that."))
            return
        await ctx.send(embed=embeds.error(self.settings, f"Something went wrong: {error}"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Leveling(bot))
