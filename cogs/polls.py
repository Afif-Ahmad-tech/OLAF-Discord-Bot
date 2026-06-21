from __future__ import annotations

import asyncio

import discord
from discord.ext import commands

from config import Settings
from utils import embeds


POLL_EMOJIS = ["1??", "2??", "3??", "4??", "5??", "6??", "7??", "8??", "9??", "??"]


class Polls(commands.Cog):
    """Quick reactions-based polls."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings

    def _parse_options(self, raw: str) -> list[str] | None:
        if "|" not in raw:
            return None
        options = [opt.strip() for opt in raw.split("|") if opt.strip()]
        if not 2 <= len(options) <= 10:
            return None
        return options

    @commands.command(name="poll")
    @commands.has_permissions(manage_messages=True)
    async def poll(self, ctx: commands.Context, *, body: str) -> None:
        if "|" not in body:
            await ctx.send(embed=embeds.error(self.settings, "Format: !poll Question? | Option A | Option B | ..."))
            return
        question, _, options_raw = body.partition("|")
        question = question.strip() or "Quick poll"
        options = [opt.strip() for opt in options_raw.split("|") if opt.strip()]
        if not 2 <= len(options) <= 10:
            await ctx.send(embed=embeds.error(self.settings, "Provide between 2 and 10 options separated by |."))
            return

        description = "\n".join(f"{POLL_EMOJIS[idx]} **{opt}**" for idx, opt in enumerate(options))
        embed = embeds.info(self.settings, description, title=question)
        embed.set_author(name=f"Poll by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.message.delete()
        message = await ctx.send(embed=embed)
        for idx in range(len(options)):
            await message.add_reaction(POLL_EMOJIS[idx])
        await ctx.send(embed=embeds.success(self.settings, f"Poll posted: {message.jump_url}"), delete_after=6)

    @commands.command(name="quickpoll")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quickpoll(self, ctx: commands.Context, *, question: str) -> None:
        embed = embeds.info(
            self.settings,
            "React with ? for **Yes**, ? for **No**, ?? for **Maybe**.",
            title=question,
        )
        message = await ctx.send(embed=embed)
        for emoji in ("?", "?", "??"):
            await message.add_reaction(emoji)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=embeds.error(self.settings, "You need the Manage Messages permission for that."))
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed=embeds.error(self.settings, "Provide poll content. Try !poll Question? | Option A | Option B."))
            return
        await ctx.send(embed=embeds.error(self.settings, f"Something went wrong: {error}"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Polls(bot))
