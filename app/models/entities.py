from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Match:
    id: str
    home: str
    away: str
    home_score: int | None
    away_score: int | None
    status: str
    minute: str
    kickoff_utc: str
    group: str
    stage: str
    venue: str
    city: str
    country: str


@dataclass(frozen=True)
class StandingRow:
    team: str
    group: str
    played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int


@dataclass(frozen=True)
class NewsItem:
    title: str
    summary: str
    published: str
    source: str
    url: str
