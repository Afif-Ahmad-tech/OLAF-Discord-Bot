from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict


class DataManager:
    """Simple JSON-backed key/value store with per-guild config."""

    def __init__(self, path: str = "data/bot_data.json") -> None:
        self.path = path
        self._lock = threading.RLock()
        self._data: Dict[str, Any] = {"guilds": {}}
        self._load()

    def _load(self) -> None:
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path, "r", encoding="utf-8") as fp:
                loaded = json.load(fp)
            if isinstance(loaded, dict):
                self._data = loaded
                self._data.setdefault("guilds", {})
        except json.JSONDecodeError:
            # Corrupt file: keep empty in-memory state but don't overwrite until save
            self._data = {"guilds": {}}

    def _save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp_path = f"{self.path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as fp:
            json.dump(self._data, fp, indent=2, ensure_ascii=False)
        os.replace(tmp_path, self.path)

    def _guild(self, guild_id: int) -> Dict[str, Any]:
        key = str(guild_id)
        bucket = self._data["guilds"].setdefault(key, {})
        bucket.setdefault("settings", {})
        bucket.setdefault("warnings", {})
        bucket.setdefault("levels", {})
        bucket.setdefault("reminders", [])
        return bucket

    # ---- settings ----
    def get_setting(self, guild_id: int, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._guild(guild_id)["settings"].get(key, default)

    def set_setting(self, guild_id: int, key: str, value: Any) -> None:
        with self._lock:
            self._guild(guild_id)["settings"][key] = value
            self._save()

    def clear_guild(self, guild_id: int) -> None:
        with self._lock:
            self._data["guilds"].pop(str(guild_id), None)
            self._save()

    # ---- warnings ----
    def add_warning(self, guild_id: int, user_id: int, moderator_id: int, reason: str) -> int:
        with self._lock:
            bucket = self._guild(guild_id)
            warnings = bucket["warnings"].setdefault(str(user_id), [])
            warnings.append({"reason": reason, "moderator": moderator_id})
            bucket["settings"]["__touch__"] = bucket["settings"].get("__touch__", 0)
            self._save()
            return len(warnings)

    def get_warnings(self, guild_id: int, user_id: int) -> list[dict]:
        with self._lock:
            return list(self._guild(guild_id)["warnings"].get(str(user_id), []))

    def clear_warnings(self, guild_id: int, user_id: int) -> None:
        with self._lock:
            self._guild(guild_id)["warnings"].pop(str(user_id), None)
            self._save()

    # ---- levels ----
    def add_xp(self, guild_id: int, user_id: int, amount: int) -> tuple[int, int, bool]:
        with self._lock:
            bucket = self._guild(guild_id)["levels"].setdefault(str(user_id), {"xp": 0, "total": 0})
            bucket["xp"] = int(bucket.get("xp", 0)) + amount
            bucket["total"] = int(bucket.get("total", 0)) + amount
            leveled = False
            old_level = self.level_for_xp(bucket["xp"] - amount)
            new_level = self.level_for_xp(bucket["xp"])
            if new_level > old_level:
                leveled = True
            self._save()
            return bucket["xp"], new_level, leveled

    def get_xp(self, guild_id: int, user_id: int) -> tuple[int, int]:
        with self._lock:
            entry = self._guild(guild_id)["levels"].get(str(user_id), {"xp": 0, "total": 0})
            return int(entry.get("xp", 0)), int(entry.get("total", 0))

    def leaderboard(self, guild_id: int, limit: int = 10) -> list[tuple[int, int]]:
        with self._lock:
            levels = self._guild(guild_id)["levels"]
            scored: list[tuple[int, int]] = []
            for raw_uid, entry in levels.items():
                total = int(entry.get("total", 0))
                scored.append((int(raw_uid), total))
            scored.sort(key=lambda item: item[1], reverse=True)
            return scored[:limit]

    # ---- reminders ----
    def add_reminder(self, guild_id: int, user_id: int, channel_id: int, text: str, fire_at: float) -> int:
        with self._lock:
            reminders = self._guild(guild_id)["reminders"]
            reminder_id = (reminders[-1]["id"] + 1) if reminders else 1
            reminders.append(
                {
                    "id": reminder_id,
                    "user_id": user_id,
                    "channel_id": channel_id,
                    "text": text,
                    "fire_at": fire_at,
                }
            )
            self._save()
            return reminder_id

    def remove_reminder(self, guild_id: int, reminder_id: int) -> dict | None:
        with self._lock:
            reminders = self._guild(guild_id)["reminders"]
            for index, item in enumerate(reminders):
                if item["id"] == reminder_id:
                    removed = reminders.pop(index)
                    self._save()
                    return removed
            return None

    def due_reminders(self, now_ts: float) -> list[tuple[int, dict]]:
        with self._lock:
            due: list[tuple[int, dict]] = []
            for raw_gid, bucket in self._data["guilds"].items():
                reminders = bucket.get("reminders", [])
                for item in list(reminders):
                    if item["fire_at"] <= now_ts:
                        due.append((int(raw_gid), item))
            return due

    def consume_due(self, guild_id: int, reminder_id: int) -> None:
        with self._lock:
            reminders = self._guild(guild_id)["reminders"]
            self._guild(guild_id)["reminders"] = [
                item for item in reminders if item["id"] != reminder_id
            ]
            self._save()

    # ---- helpers ----
    @staticmethod
    def level_for_xp(xp: int) -> int:
        # Quadratic curve: level 0 at 0xp, +1 level per ~100 xp, accelerating slightly.
        if xp <= 0:
            return 0
        level = 0
        required = 100
        remaining = xp
        while remaining >= required:
            remaining -= required
            level += 1
            required = int(required * 1.25)
        return level

    @staticmethod
    def xp_for_level(level: int) -> int:
        required = 100
        total = 0
        for _ in range(level):
            total += required
            required = int(required * 1.25)
        return total
