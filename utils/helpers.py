from __future__ import annotations

import datetime as dt
import random
from typing import Iterable

import discord


def utcnow() -> dt.datetime:
    if dt.datetime is dt.datetime.utcnow:  # pragma: no cover - py<3.12 helper
        return dt.datetime.utcnow()
    return dt.datetime.now(dt.timezone.utc)


def format_dt(dt_obj: dt.datetime | None, style: str = "F") -> str:
    if dt_obj is None:
        return "n/a"
    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=dt.timezone.utc)
    return discord.utils.format_dt(dt_obj, style=style)


def chunk_lines(text: str, limit: int = 1024) -> list[str]:
    lines = text.splitlines() or [text]
    chunks: list[str] = []
    buffer = ""
    for line in lines:
        candidate = f"{buffer}\n{line}".strip() if buffer else line
        if len(candidate) <= limit:
            buffer = candidate
            continue
        if buffer:
            chunks.append(buffer)
        buffer = line
    if buffer:
        chunks.append(buffer)
    return chunks


def parse_duration(text: str) -> int | None:
    """Parse a duration string like 10m, 2h, 1d into seconds."""
    if not text:
        return None
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    num = ""
    unit = ""
    for char in text.strip():
        if char.isdigit() or char == ".":
            num += char
        elif char.lower() in units:
            unit = char.lower()
            break
    if not num or not unit:
        return None
    try:
        value = float(num)
    except ValueError:
        return None
    return int(value * units[unit])


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    days, hours = divmod(hours, 24)
    parts = [f"{days}d"]
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts)


def is_staff(member: discord.Member, owner_id: int) -> bool:
    if member.guild.owner_id == member.id:
        return True
    if member.id == owner_id:
        return True
    return member.guild.me.top_role < member.top_role and member.guild_permissions.manage_guild


def truncate(text: str, limit: int = 1024) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def progress_bar(current: int, total: int, length: int = 14) -> str:
    if total <= 0:
        return "?" * length
    filled = max(0, min(length, int(length * current / total)))
    return "?" * filled + "?" * (length - filled)


def sample_picker(pool: Iterable, k: int = 1) -> list:
    pool_list = list(pool)
    if not pool_list:
        return []
    return random.sample(pool_list, min(k, len(pool_list)))
