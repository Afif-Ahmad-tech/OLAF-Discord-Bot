from __future__ import annotations

import discord

from config import Settings


def _base(settings: Settings) -> discord.Embed:
    embed = discord.Embed(color=settings.embed_color, timestamp=discord.utils.utcnow())
    embed.set_footer(text=f"{settings.bot_name} v{settings.version}")
    return embed


def success(settings: Settings, description: str, **kwargs) -> discord.Embed:
    embed = _base(settings)
    embed.color = 0x57F287
    embed.description = description
    embed.title = kwargs.pop("title", "Success")
    if "footer" in kwargs:
        embed.set_footer(text=kwargs.pop("footer"))
    for key, value in kwargs.items():
        setattr(embed, f"set_{key}", None)
        if hasattr(embed, f"set_{key}"):
            getattr(embed, f"set_{key}")(value)
    return embed


def info(settings: Settings, description: str, **kwargs) -> discord.Embed:
    embed = _base(settings)
    embed.title = kwargs.pop("title", "Info")
    embed.description = description
    for key, value in kwargs.items():
        if hasattr(embed, f"set_{key}"):
            getattr(embed, f"set_{key}")(value)
    return embed


def error(settings: Settings, description: str, title: str = "Error") -> discord.Embed:
    embed = _base(settings)
    embed.color = 0xED4245
    embed.title = title
    embed.description = description
    return embed


def warning(settings: Settings, description: str, title: str = "Heads up") -> discord.Embed:
    embed = _base(settings)
    embed.color = 0xFEE75C
    embed.title = title
    embed.description = description
    return embed
