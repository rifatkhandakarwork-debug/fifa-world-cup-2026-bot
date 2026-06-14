from __future__ import annotations

from app.services.matches_service import MatchesService
from app.services.standings_service import StandingsService


class AiService:
    def __init__(self, matches_service: MatchesService, standings_service: StandingsService) -> None:
        self.matches_service = matches_service
        self.standings_service = standings_service

    async def answer(self, question: str) -> str:
        q = question.lower()
        if "today" in q or "আজ" in q:
            matches = await self.matches_service.today()
            return "আজ কোনো ম্যাচ পাওয়া যায়নি।" if not matches else "\n\n".join(f"{m.home} vs {m.away} - {m.status}" for m in matches)
        if "live" in q or "লাইভ" in q:
            matches = await self.matches_service.live()
            return "এখন কোনো live match নেই।" if not matches else "\n\n".join(f"{m.home} {m.home_score}-{m.away_score} {m.away} ({m.minute})" for m in matches)
        if "standing" in q or "standings" in q or "পয়েন্ট" in q:
            groups = await self.standings_service.all_groups()
            return "Standing data এখনো পাওয়া যায়নি।" if not groups else "\n".join(groups.keys())
        if "next" in q or "পরের" in q:
            for word in question.split():
                matches = await self.matches_service.by_team(word)
                if matches:
                    upcoming = [m for m in matches if m.status == "Scheduled"]
                    if upcoming:
                        m = upcoming[0]
                        return f"{m.home} vs {m.away} - {m.kickoff_utc}"
        return "আমি local World Cup database থেকে উত্তর খুঁজেছি, কিন্তু নিশ্চিত তথ্য পাইনি। Schedule, live, standings বা team name দিয়ে আবার জিজ্ঞেস করুন।"
