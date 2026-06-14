from __future__ import annotations

from collections import defaultdict

from app.services.matches_service import MatchesService


class VenuesService:
    def __init__(self, matches_service: MatchesService) -> None:
        self.matches_service = matches_service

    async def list_venues(self) -> list[dict]:
        venues: dict[str, dict] = {}
        for match in await self.matches_service.all_matches():
            if not match.venue:
                continue
            venues.setdefault(
                match.venue,
                {
                    "name": match.venue,
                    "city": match.city,
                    "country": match.country,
                    "matches": [],
                    "map": f"https://www.google.com/maps/search/{match.venue.replace(' ', '+')}+{match.city.replace(' ', '+')}",
                },
            )["matches"].append(match)
        return list(venues.values())
