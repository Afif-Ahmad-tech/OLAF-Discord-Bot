from __future__ import annotations

import time

import discord
from discord.ext import commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


class Reminders(commands.Cog):
    """Personal reminders that ping the author after a chosen delay."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    @commands.command(name="remind")
    async def remind(self, ctx: commands.Context, duration: str, *, text: str | None = None) -> None:
        if not text:
            await ctx.send(embed=embeds.error(self.settings, "Tell me what to remind you. !remind 30m Take a break."))
            return
        seconds = helpers.parse_duration(duration)
        if seconds is None or seconds <= 0 or seconds > 60 * 60 * 24 * 30:
            await ctx.send(embed=embeds.error(self.settings, "Duration must be like 10m, 2h, 1d, and within 30 days."))
            return
        fire_at = time.time() + seconds
        rid = self.data.add_reminder(ctx.guild.id, ctx.author.id, ctx.channel.id if ctx.channel else 0, text, fire_at)
        embed = embeds.success(
            self.settings,
            f"I'll ping you in **{helpers.format_duration(seconds)}** with reminder **#{rid}**.",
            title="Reminder set",
        )
        await ctx.send(embed=embed)

    @commands.command(name="reminders")
    async def reminders(self, ctx: commands.Context) -> None:
        bucket = self.data._guild(ctx.guild.id)
        mine = [r for r in bucket["reminders"] if r["user_id"] == ctx.author.id]
        if not mine:
            await ctx.send(embed=embeds.info(self.settings, "You have no active reminders."))
            return
        lines = [
            f"#{r['id']} — {r['text']} (fires <t:{int(r['fire_at'])}:R>)" for r in sorted(mine, key=lambda r: r["fire_at"])
        ]
        await ctx.send(embed=embeds.info(self.settings, "\n".join(lines), title="Your reminders"))

    @commands.command(name="cancelremind")
    async def cancelremind(self, ctx: commands.Context, reminder_id: int) -> None:
        bucket = self.data._guild(ctx.guild.id)
        for reminder in bucket["reminders"]:
            if reminder["id"] == reminder_id and reminder["user_id"] == ctx.author.id:
                self.data.remove_reminder(ctx.guild.id, reminder_id)
                await ctx.send(embed=embeds.success(self.settings, f"Reminder **#{reminder_id}** cancelled."))
                return
        await ctx.send(embed=embeds.error(self.settings, "I couldn't find that reminder."))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Reminders(bot))
