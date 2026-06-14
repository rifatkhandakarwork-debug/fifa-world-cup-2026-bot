from __future__ import annotations

from app.database import Database


DEFAULT_PREFERENCES = {
    "goal": True,
    "match_start": True,
    "half_time": True,
    "full_time": True,
    "red_card": True,
    "penalty": True,
    "extra_time": True,
    "match_result": True,
    "favorite_team": True,
    "all_matches": False,
}


class NotificationsService:
    def __init__(self, db: Database) -> None:
        self.db = db

    async def preferences(self, user_id: int) -> dict[str, bool]:
        saved = await self.db.get_preferences(user_id)
        return DEFAULT_PREFERENCES | saved

    async def toggle(self, user_id: int, preference: str) -> bool:
        prefs = await self.preferences(user_id)
        new_value = not prefs.get(preference, False)
        await self.db.set_preference(user_id, preference, new_value)
        return new_value
