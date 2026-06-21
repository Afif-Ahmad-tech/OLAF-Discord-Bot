from __future__ import annotations

import asyncio
import logging
import sys

import discord
from discord.ext import commands

from config import Settings, load_settings
from data.manager import DataManager


class OlafBot(commands.Bot):
    def __init__(self, settings: Settings, data: DataManager) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.messages = True

        super().__init__(
            command_prefix=self._resolve_prefix,
            intents=intents,
            help_command=None,
            case_insensitive=True,
        )
        self.settings = settings
        self.data = data
        self.logger = logging.getLogger("olaf")
        self.started_at = discord.utils.utcnow()

    async def _resolve_prefix(self, bot: "OlafBot", message: discord.Message) -> list[str]:
        if not message.guild:
            return [self.settings.prefix, f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "] if bot.user else [self.settings.prefix]
        prefix = self.data.get_setting(message.guild.id, "prefix", self.settings.prefix)
        if not isinstance(prefix, str) or not prefix:
            prefix = self.settings.prefix
        return [prefix, f"<@{bot.user.id}> ", f"<@!{bot.user.id}> "] if bot.user else [prefix]

    async def setup_hook(self) -> None:
        for ext in (
            "cogs.moderation",
            "cogs.welcome",
            "cogs.utility",
            "cogs.fun",
            "cogs.polls",
            "cogs.logging",
            "cogs.leveling",
            "cogs.reminders",
            "cogs.config_cog",
        ):
            try:
                await self.load_extension(ext)
                self.logger.info("Loaded extension %s", ext)
            except Exception as exc:  # surface but keep going
                self.logger.exception("Failed to load %s: %s", ext, exc)

        # Background reminder loop
        self.loop.create_task(self._reminder_loop())

    async def _reminder_loop(self) -> None:
        await self.wait_until_ready()
        import time

        while not self.is_closed():
            try:
                now = time.time()
                due = self.data.due_reminders(now)
                for guild_id, reminder in due:
                    guild = self.get_guild(guild_id)
                    if guild is None:
                        self.data.consume_due(guild_id, reminder["id"])
                        continue
                    channel = guild.get_channel(reminder["channel_id"])
                    user = guild.get_member(reminder["user_id"]) or await self.fetch_user(reminder["user_id"])
                    target = channel or (user and await user.create_dm())
                    if target is None:
                        self.data.consume_due(guild_id, reminder["id"])
                        continue
                    embed = discord.Embed(
                        title="Reminder",
                        description=reminder["text"],
                        color=self.settings.embed_color,
                    )
                    embed.set_footer(text=f"{self.settings.bot_name} v{self.settings.version}")
                    try:
                        await target.send(
                            content=user.mention if user else None,
                            embed=embed,
                            allowed_mentions=discord.AllowedMentions(users=True),
                        )
                    except discord.Forbidden:
                        pass
                    finally:
                        self.data.consume_due(guild_id, reminder["id"])
            except Exception as exc:  # pragma: no cover - safety net
                self.logger.exception("Reminder loop error: %s", exc)
            await asyncio.sleep(15)

async def on_ready(self) -> None:
    if self.user is None:
        return

    self.logger.info(
        "Logged in as %s (id=%s) in %d guild(s)",
        self.user,
        self.user.id,
        len(self.guilds),
    )

    try:
        synced = await self.tree.sync()
        self.logger.info("Synced %d slash command(s)", len(synced))
    except Exception as exc:
        self.logger.exception("Failed to sync slash commands: %s", exc)

    await self.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{self.settings.prefix}help",
        ),
        status=discord.Status.online,
    )

def main() -> int:
    configure_logging()
    try:
        settings = load_settings()
    except RuntimeError as exc:
        print(f"[olaf] {exc}", file=sys.stderr)
        return 1
    data = DataManager()
    bot = OlafBot(settings, data)
    try:
        bot.run(settings.token, log_handler=None)
    except discord.LoginFailure:
        print("[olaf] Invalid Discord token. Double check DISCORD_TOKEN in .env", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
