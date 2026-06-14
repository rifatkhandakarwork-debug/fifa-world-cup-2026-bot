from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from app.database import Database


class Cache:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def remember(self, table: str, key: str, ttl_seconds: int, loader: Callable[[], Awaitable[Any]]) -> Any:
        cached = await self.db.cache_get(table, key)
        if cached is not None:
            return cached

        payload = await loader()
        await self.db.cache_set(table, key, payload, ttl_seconds)
        return payload
