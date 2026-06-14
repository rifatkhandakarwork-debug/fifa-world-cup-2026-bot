from __future__ import annotations

import html

from app.cache import Cache
from app.services.http_client import HttpClient


class PlayersService:
    def __init__(self, cache: Cache, http: HttpClient) -> None:
        self.cache = cache
        self.http = http
        self.url = "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/statistics"

    async def top_scorers(self) -> list[dict]:
        return await self._leaders("goalsLeaders")

    async def top_assists(self) -> list[dict]:
        return await self._leaders("assistsLeaders")

    async def unavailable_message(self) -> str:
        scorers = await self.top_scorers()
        assists = await self.top_assists()
        if not scorers and not assists:
            return "⚠️ Player statistics এখন পাওয়া যাচ্ছে না। পরে আবার চেষ্টা করুন।"
        return self.format_leaders("Top Scorers", scorers) + "\n\n" + self.format_leaders("Top Assists", assists)

    async def _leaders(self, name: str) -> list[dict]:
        async def loader() -> dict:
            return await self.http.get_json(self.url)

        payload = await self.cache.remember("cached_players", "espn:player-stats", 1800, loader)
        for stat in payload.get("stats", []):
            if stat.get("name") == name:
                leaders = stat.get("leaders", [])
                return leaders[:10] if isinstance(leaders, list) else []
        return []

    def format_leaders(self, title: str, leaders: list[dict]) -> str:
        if not leaders:
            return f"<b>{html.escape(title)}</b>\nডাটা পাওয়া যায়নি।"
        border = "+----+------------------+------+-----+"
        lines = [border, "| #  | Player           | Team | Val |", border]
        for index, item in enumerate(leaders[:10], start=1):
            athlete = item.get("athlete") or {}
            team = athlete.get("team") or {}
            name = str(athlete.get("displayName") or "Unknown")[:16].ljust(16)
            team_name = str(team.get("abbreviation") or team.get("displayName") or "")[:4].ljust(4)
            value = str(int(item.get("value", 0)))[:3].rjust(3)
            lines.append(f"| {index:<2} | {name} | {team_name} | {value} |")
        lines.append(border)
        return f"<b>{html.escape(title)}</b>\n<pre>{html.escape(chr(10).join(lines))}</pre>\nSource: ESPN"
