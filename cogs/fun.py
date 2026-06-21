from __future__ import annotations

import random

import discord
from discord.ext import commands

from config import Settings
from data.manager import DataManager
from utils import embeds, helpers


JOKES = [
    "Why don't scientists trust atoms? Because they make up everything.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I told my computer I needed a break, and it said \"No problem — I'll go to sleep.\"",
    "Why do programmers prefer dark mode? Because light attracts bugs.",
    "What do you call fake spaghetti? An impasta.",
    "Why was the math book sad? It had too many problems.",
]

EIGHT_BALL_RESPONSES = [
    "It is certain.", "Without a doubt.", "Yes, definitely.", "You may rely on it.",
    "Signs point to yes.", "Most likely.", "Outlook good.", "Yes.",
    "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
    "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.",
    "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful.",
]


class Fun(commands.Cog):
    """Light entertainment commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.settings: Settings = bot.settings
        self.data: DataManager = bot.data

    @commands.command(name="8ball")
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def eight_ball(self, ctx: commands.Context, *, question: str | None = None) -> None:
        if not question:
            await ctx.send(embed=embeds.error(self.settings, "Ask the magic 8-ball a question."))
            return
        response = random.choice(EIGHT_BALL_RESPONSES)
        embed = embeds.info(self.settings, f"**Question:** {question}\n**Answer:** {response}", title="Magic 8-ball")
        await ctx.send(embed=embed)

    @commands.command(name="roll")
    async def roll(self, ctx: commands.Context, dice: str = "1d6") -> None:
        try:
            count_str, sides_str = dice.lower().split("d")
            count = int(count_str or "1")
            sides = int(sides_str)
        except ValueError:
            await ctx.send(embed=embeds.error(self.settings, "Use the format NdM, e.g. 2d20."))
            return
        if not (1 <= count <= 25 and 2 <= sides <= 1000):
            await ctx.send(embed=embeds.error(self.settings, "Roll between 1 and 25 dice with 2 to 1000 sides."))
            return
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls)
        description = f"Rolling {dice}\nResults: {', '.join(map(str, rolls))}\nTotal: **{total}**"
        await ctx.send(embed=embeds.info(self.settings, description, title="Dice roll"))

    @commands.command(name="coinflip", aliases=["flip"])
    async def coinflip(self, ctx: commands.Context) -> None:
        side = random.choice(["Heads", "Tails"])
        await ctx.send(embed=embeds.info(self.settings, f"The coin landed on **{side}**.", title="Coin flip"))

    @commands.command(name="choose")
    async def choose(self, ctx: commands.Context, *, options: str) -> None:
        choices = [opt.strip() for opt in options.split("|") if opt.strip()]
        if len(choices) < 2:
            await ctx.send(embed=embeds.error(self.settings, "Provide at least two options separated by |."))
            return
        pick = random.choice(choices)
        await ctx.send(embed=embeds.info(self.settings, f"I pick **{pick}**", title="Choose"))

    @commands.command(name="rps")
    async def rps(self, ctx: commands.Context, choice: str | None = None) -> None:
        valid = {"rock": "rock", "paper": "paper", "scissors": "scissors", "r": "rock", "p": "paper", "s": "scissors"}
        if not choice or choice.lower() not in valid:
            await ctx.send(embed=embeds.error(self.settings, "Pick rock, paper, or scissors."))
            return
        user_pick = valid[choice.lower()]
        bot_pick = random.choice(["rock", "paper", "scissors"])
        beats = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
        if user_pick == bot_pick:
            verdict = "It's a tie."
        elif beats[user_pick] == bot_pick:
            verdict = "You win!"
        else:
            verdict = "I win!"
        description = f"You: **{user_pick}**\nMe: **{bot_pick}**\n{verdict}"
        await ctx.send(embed=embeds.info(self.settings, description, title="Rock · Paper · Scissors"))

    @commands.command(name="joke")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def joke(self, ctx: commands.Context) -> None:
        await ctx.send(embed=embeds.info(self.settings, random.choice(JOKES), title="Joke"))

    @commands.command(name="rate")
    async def rate(self, ctx: commands.Context, *, thing: str | None = None) -> None:
        target = thing or ctx.author.display_name
        score = random.randint(0, 100)
        bar = helpers.progress_bar(score, 100)
        await ctx.send(embed=embeds.info(self.settings, f"I rate **{target}** a {score}/100.\n{bar}", title="Rate"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
