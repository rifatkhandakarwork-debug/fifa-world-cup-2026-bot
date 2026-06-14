from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from app.cache import Cache
from app.config import Settings
from app.models.entities import Match
from app.services.http_client import HttpClient
from app.utils.time import date_range_ymd


def _desc(values: list[dict] | None) -> str:
    values = values or []
    for item in values:
        if item.get("Locale") == "en-GB" and item.get("Description"):
            return str(item["Description"])
    return str(values[0].get("Description", "")) if values else ""


class MatchesService:
    def __init__(self, settings: Settings, cache: Cache, http: HttpClient) -> None:
        self.settings = settings
        self.cache = cache
        self.http = http

    async def all_matches(self) -> list[Match]:
        async def loader() -> list[dict]:
            return await self._fetch_fifa_matches("2026-06-11", "2026-07-19")

        raw = await self.cache.remember("cached_matches", "matches:tournament:v2", 300, loader)
        return [self._parse_fifa_match(item) for item in raw]

    async def today(self) -> list[Match]:
        return self._by_day(await self.all_matches(), 0)

    async def tomorrow(self) -> list[Match]:
        return self._by_day(await self.all_matches(), 1)

    async def upcoming(self, limit: int = 10) -> list[Match]:
        now = datetime.now(ZoneInfo(self.settings.timezone))
        matches = [m for m in await self.all_matches() if self._local_dt(m) >= now and m.status == "Scheduled"]
        return sorted(matches, key=self._local_dt)[:limit]

    async def live(self) -> list[Match]:
        async def loader() -> list[dict]:
            start, end = date_range_ymd(self.settings.timezone, 1, 1)
            return await self._fetch_fifa_matches(start, end)

        raw = await self.cache.remember("cached_matches", "matches:live", 30, loader)
        return [self._parse_fifa_match(item) for item in raw if self._status(item) == "Live"]

    async def live_stats(self, match: Match) -> dict[str, str]:
        async def loader() -> dict:
            return await self.http.get_json(self.settings.espn_scoreboard_url, {"limit": 100})

        payload = await self.cache.remember("cached_matches", "espn:scoreboard:live-stats", 30, loader)
        events = payload.get("events", [])
        if not isinstance(events, list):
            return {}

        for event in events:
            competitions = event.get("competitions") or []
            competitors = (competitions[0].get("competitors") if competitions else []) or []
            names = [((item.get("team") or {}).get("displayName") or "").lower() for item in competitors]
            if self._same_match(match, names):
                return self._team_stats_summary(competitors)
        return {}

    async def by_team(self, query: str) -> list[Match]:
        query = query.lower()
        return [m for m in await self.all_matches() if query in m.home.lower() or query in m.away.lower()]

    async def by_group(self, group: str) -> list[Match]:
        group = group.upper().replace("GROUP ", "")
        return [m for m in await self.all_matches() if m.group.upper().endswith(group)]

    async def by_venue(self, venue: str) -> list[Match]:
        venue = venue.lower()
        return [m for m in await self.all_matches() if venue in m.venue.lower() or venue in m.city.lower()]

    async def by_date(self, yyyy_mm_dd: str) -> list[Match]:
        target = datetime.fromisoformat(yyyy_mm_dd).date()
        return [m for m in await self.all_matches() if self._local_dt(m).date() == target]

    async def _fetch_fifa_matches(self, start: str, end: str) -> list[dict]:
        payload = await self.http.get_json(
            self.settings.fifa_calendar_url,
            {
                "language": "en",
                "idCompetition": self.settings.fifa_competition_id,
                "count": 200,
                "from": start,
                "to": end,
            },
        )
        results = payload.get("Results", [])
        return results if isinstance(results, list) else []

    def _parse_fifa_match(self, item: dict) -> Match:
        home = item.get("Home") or {}
        away = item.get("Away") or {}
        stadium = item.get("Stadium") or {}
        return Match(
            id=str(item.get("IdMatch", "")),
            home=_desc(home.get("TeamName")) or str(home.get("ShortClubName", "Home")),
            away=_desc(away.get("TeamName")) or str(away.get("ShortClubName", "Away")),
            home_score=item.get("HomeTeamScore"),
            away_score=item.get("AwayTeamScore"),
            status=self._status(item),
            minute=str(item.get("MatchTime") or ""),
            kickoff_utc=str(item.get("Date") or ""),
            group=_desc(item.get("GroupName")),
            stage=_desc(item.get("StageName")),
            venue=_desc(stadium.get("Name")),
            city=_desc(stadium.get("CityName")),
            country=str(stadium.get("IdCountry") or ""),
        )

    def _status(self, item: dict) -> str:
        return {0: "Finished", 1: "Scheduled", 3: "Live"}.get(int(item.get("MatchStatus", -1)), "Unknown")

    def _by_day(self, matches: list[Match], offset: int) -> list[Match]:
        today = datetime.now(ZoneInfo(self.settings.timezone)).date()
        target = today + timedelta(days=offset)
        return [m for m in matches if self._local_dt(m).date() == target]

    def _local_dt(self, match: Match) -> datetime:
        return datetime.fromisoformat(match.kickoff_utc.replace("Z", "+00:00")).astimezone(ZoneInfo(self.settings.timezone))

    def _same_match(self, match: Match, names: list[str]) -> bool:
        home = match.home.lower()
        away = match.away.lower()
        return any(home in name or name in home for name in names) and any(away in name or name in away for name in names)

    def _team_stats_summary(self, competitors: list[dict]) -> dict[str, str]:
        if len(competitors) < 2:
            return {}
        teams = []
        for item in competitors:
            team = (item.get("team") or {}).get("displayName", "Team")
            stats = {stat.get("name"): stat.get("displayValue") for stat in item.get("statistics", [])}
            teams.append((team, stats))

        wanted = {
            "possessionPct": "Possession",
            "totalShots": "Shots",
            "shotsOnTarget": "Shots On Target",
            "wonCorners": "Corners",
            "foulsCommitted": "Fouls",
            "goalAssists": "Assists",
        }
        output: dict[str, str] = {}
        for key, label in wanted.items():
            left = teams[0][1].get(key)
            right = teams[1][1].get(key)
            if left is not None and right is not None:
                suffix = "%" if key == "possessionPct" else ""
                output[label] = f"{teams[0][0]} {left}{suffix} | {teams[1][0]} {right}{suffix}"
        return output
