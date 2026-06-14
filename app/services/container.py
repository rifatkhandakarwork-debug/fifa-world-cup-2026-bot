from __future__ import annotations

from dataclasses import dataclass

from app.cache import Cache
from app.config import Settings
from app.database import Database
from app.services.ai_service import AiService
from app.services.http_client import HttpClient
from app.services.matches_service import MatchesService
from app.services.news_service import NewsService
from app.services.notifications_service import NotificationsService
from app.services.players_service import PlayersService
from app.services.standings_service import StandingsService
from app.services.teams_service import TeamsService
from app.services.venues_service import VenuesService


@dataclass(frozen=True)
class Services:
    db: Database
    matches: MatchesService
    standings: StandingsService
    players: PlayersService
    teams: TeamsService
    venues: VenuesService
    news: NewsService
    notifications: NotificationsService
    ai: AiService


def build_services(settings: Settings) -> Services:
    db = Database(settings.database_path)
    cache = Cache(db)
    http = HttpClient()
    matches = MatchesService(settings, cache, http)
    standings = StandingsService(matches)
    return Services(
        db=db,
        matches=matches,
        standings=standings,
        players=PlayersService(cache, http),
        teams=TeamsService(matches),
        venues=VenuesService(matches),
        news=NewsService(settings, cache, http),
        notifications=NotificationsService(db),
        ai=AiService(matches, standings),
    )
