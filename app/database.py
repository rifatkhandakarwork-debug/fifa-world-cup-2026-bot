from __future__ import annotations

import json
import time
from typing import Any

import aiosqlite


class Database:
    def __init__(self, path: str) -> None:
        self.path = path

    async def init(self) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    chat_id INTEGER NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    created_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS favorite_teams (
                    user_id INTEGER PRIMARY KEY,
                    team_name TEXT NOT NULL,
                    updated_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notification_preferences (
                    user_id INTEGER NOT NULL,
                    preference TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    PRIMARY KEY (user_id, preference)
                );

                CREATE TABLE IF NOT EXISTS cached_matches (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cached_standings (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cached_players (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cached_teams (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS cached_news (
                    cache_key TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sent_notifications (
                    user_id INTEGER NOT NULL,
                    event_key TEXT NOT NULL,
                    sent_at INTEGER NOT NULL,
                    PRIMARY KEY (user_id, event_key)
                );
                """
            )
            await db.commit()

    async def upsert_user(self, user_id: int, chat_id: int, username: str | None, first_name: str | None) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO users (user_id, chat_id, username, first_name, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    chat_id = excluded.chat_id,
                    username = excluded.username,
                    first_name = excluded.first_name
                """,
                (user_id, chat_id, username, first_name, int(time.time())),
            )
            await db.commit()

    async def set_favorite_team(self, user_id: int, team_name: str) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO favorite_teams (user_id, team_name, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    team_name = excluded.team_name,
                    updated_at = excluded.updated_at
                """,
                (user_id, team_name, int(time.time())),
            )
            await db.commit()

    async def get_favorite_team(self, user_id: int) -> str | None:
        async with aiosqlite.connect(self.path) as db:
            row = await (await db.execute("SELECT team_name FROM favorite_teams WHERE user_id = ?", (user_id,))).fetchone()
            return str(row[0]) if row else None

    async def set_preference(self, user_id: int, preference: str, enabled: bool) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                """
                INSERT INTO notification_preferences (user_id, preference, enabled)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, preference) DO UPDATE SET enabled = excluded.enabled
                """,
                (user_id, preference, int(enabled)),
            )
            await db.commit()

    async def get_preferences(self, user_id: int) -> dict[str, bool]:
        async with aiosqlite.connect(self.path) as db:
            rows = await (await db.execute(
                "SELECT preference, enabled FROM notification_preferences WHERE user_id = ?",
                (user_id,),
            )).fetchall()
            return {str(name): bool(enabled) for name, enabled in rows}

    async def cache_get(self, table: str, key: str) -> Any | None:
        async with aiosqlite.connect(self.path) as db:
            row = await (await db.execute(
                f"SELECT payload, expires_at FROM {table} WHERE cache_key = ?",
                (key,),
            )).fetchone()
            if not row or int(row[1]) < int(time.time()):
                return None
            return json.loads(str(row[0]))

    async def cache_set(self, table: str, key: str, payload: Any, ttl_seconds: int) -> None:
        async with aiosqlite.connect(self.path) as db:
            await db.execute(
                f"""
                INSERT INTO {table} (cache_key, payload, expires_at)
                VALUES (?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    payload = excluded.payload,
                    expires_at = excluded.expires_at
                """,
                (key, json.dumps(payload, ensure_ascii=False), int(time.time()) + ttl_seconds),
            )
            await db.commit()
