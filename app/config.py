from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    bot_token: str
    database_path: str
    timezone: str
    fifa_calendar_url: str
    fifa_competition_id: str
    espn_scoreboard_url: str
    news_feeds: tuple[str, ...]

    @classmethod
    def from_env(cls) -> "Settings":
        feeds = os.getenv("NEWS_FEEDS", "").split(",")
        return cls(
            bot_token=os.getenv("BOT_TOKEN", "").strip(),
            database_path=os.getenv("DATABASE_PATH", "worldcup_bot.sqlite3").strip(),
            timezone=os.getenv("TIMEZONE", "Asia/Dhaka").strip(),
            fifa_calendar_url=os.getenv("FIFA_CALENDAR_URL", "https://api.fifa.com/api/v3/calendar/matches").strip(),
            fifa_competition_id=os.getenv("FIFA_COMPETITION_ID", "17").strip(),
            espn_scoreboard_url=os.getenv(
                "ESPN_SCOREBOARD_URL",
                "https://site.api.espn.com/apis/site/v2/sports/soccer/fifa.world/scoreboard",
            ).strip(),
            news_feeds=tuple(feed.strip() for feed in feeds if feed.strip()),
        )


BASE_DIR = Path(__file__).resolve().parents[1]
settings = Settings.from_env()
