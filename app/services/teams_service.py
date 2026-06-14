from __future__ import annotations

from app.services.matches_service import MatchesService


class TeamsService:
    def __init__(self, matches_service: MatchesService) -> None:
        self.matches_service = matches_service

    async def search(self, team_name: str) -> dict:
        matches = await self.matches_service.by_team(team_name)
        if not matches:
            return {}
        names = {matches[0].home, matches[0].away}
        exact = next((name for name in names if team_name.lower() in name.lower()), team_name)
        return {
            "name": exact,
            "recent_matches": [m for m in matches if m.status == "Finished"][-5:],
            "upcoming_matches": [m for m in matches if m.status != "Finished"][:5],
        }
