from __future__ import annotations

from collections import defaultdict

from app.models.entities import Match, StandingRow
from app.services.matches_service import MatchesService


class StandingsService:
    def __init__(self, matches_service: MatchesService) -> None:
        self.matches_service = matches_service

    async def all_groups(self, sort_by: str = "points") -> dict[str, list[StandingRow]]:
        matches = await self.matches_service.all_matches()
        groups: dict[str, dict[str, dict[str, int]]] = defaultdict(dict)
        for match in matches:
            group = match.group or "Unknown Group"
            for team in (match.home, match.away):
                groups[group].setdefault(team, {"p": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0, "pts": 0})
            if match.status == "Finished" and match.home_score is not None and match.away_score is not None:
                self._apply_result(groups[group], match)

        output: dict[str, list[StandingRow]] = {}
        for group, table in groups.items():
            rows = [
                StandingRow(
                    team=team,
                    group=group,
                    played=data["p"],
                    wins=data["w"],
                    draws=data["d"],
                    losses=data["l"],
                    goals_for=data["gf"],
                    goals_against=data["ga"],
                    goal_difference=data["gf"] - data["ga"],
                    points=data["pts"],
                )
                for team, data in table.items()
            ]
            key = {"gd": "goal_difference", "goals": "goals_for"}.get(sort_by, "points")
            output[group] = sorted(rows, key=lambda r: (getattr(r, key), r.goal_difference, r.goals_for), reverse=True)
        return output

    async def group(self, group_letter: str, sort_by: str = "points") -> list[StandingRow]:
        groups = await self.all_groups(sort_by)
        wanted = f"Group {group_letter.upper()}"
        return groups.get(wanted, [])

    def _apply_result(self, table: dict[str, dict[str, int]], match: Match) -> None:
        home = table[match.home]
        away = table[match.away]
        home_score = int(match.home_score or 0)
        away_score = int(match.away_score or 0)
        home["p"] += 1
        away["p"] += 1
        home["gf"] += home_score
        home["ga"] += away_score
        away["gf"] += away_score
        away["ga"] += home_score
        if home_score > away_score:
            home["w"] += 1
            away["l"] += 1
            home["pts"] += 3
        elif home_score < away_score:
            away["w"] += 1
            home["l"] += 1
            away["pts"] += 3
        else:
            home["d"] += 1
            away["d"] += 1
            home["pts"] += 1
            away["pts"] += 1
