from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # dotenv is optional, fallback to raw env vars
    pass


@dataclass(frozen=True)
class Settings:
    token: str
    owner_id: int
    prefix: str
    bot_name: str
    version: str
    embed_color: int
    default_cooldown: float
    max_warnings: int


def load_settings() -> Settings:
    token = os.getenv("DISCORD_TOKEN", "").strip()
    owner_raw = os.getenv("BOT_OWNER_ID", "0").strip()
    prefix = os.getenv("BOT_PREFIX", "!").strip() or "!"
    if not token:
        raise RuntimeError(
            "DISCORD_TOKEN is not set. Copy .env.example to .env and add your bot token."
        )
    try:
        owner_id = int(owner_raw)
    except ValueError as exc:
        raise RuntimeError("BOT_OWNER_ID must be an integer Discord user id.") from exc

    return Settings(
        token=token,
        owner_id=owner_id,
        prefix=prefix,
        bot_name="OLAF",
        version="1.0.0",
        embed_color=0x5865F2,  # Discord blurple
        default_cooldown=3.0,
        max_warnings=3,
    )
