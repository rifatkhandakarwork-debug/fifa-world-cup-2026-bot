from __future__ import annotations

import html
import re

from app.models.entities import Match, NewsItem, StandingRow
from app.utils.time import to_local_time


def clean_text(value: str, limit: int | None = None) -> str:
    text = re.sub(r"<[^>]+>", " ", value or "")
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        text = text[: limit - 3].rstrip() + "..."
    return html.escape(text)


def bn_status(status: str) -> str:
    return {
        "Scheduled": "নির্ধারিত",
        "Live": "লাইভ",
        "Finished": "শেষ",
        "Unknown": "অজানা",
    }.get(status, status)


def match_line(match: Match, timezone: str) -> str:
    score = "বনাম"
    if match.home_score is not None and match.away_score is not None and match.status != "Scheduled":
        score = f"{match.home_score} - {match.away_score}"
    venue = ", ".join(part for part in [match.venue, match.city, match.country] if part)
    return (
        f"<b>{html.escape(match.home)} {score} {html.escape(match.away)}</b>\n"
        f"সময়: {to_local_time(match.kickoff_utc, timezone)}\n"
        f"অবস্থা: {html.escape(bn_status(match.status))}{(' - ' + html.escape(match.minute)) if match.minute else ''}\n"
        f"ভেন্যু: {html.escape(venue or 'জানা যায়নি')}"
    )


def live_match_card(match: Match, timezone: str, stats: dict[str, str] | None = None) -> str:
    home_score = match.home_score if match.home_score is not None else 0
    away_score = match.away_score if match.away_score is not None else 0
    base = (
        f"<b>🔴 লাইভ ম্যাচ</b>\n\n"
        f"<b>{html.escape(match.home)} {home_score} - {away_score} {html.escape(match.away)}</b>\n\n"
        f"⏱ মিনিট: {html.escape(match.minute or 'লাইভ')}\n"
        f"সময়: {to_local_time(match.kickoff_utc, timezone)}"
    )
    if not stats:
        return base
    labels = {
        "Possession": "বল দখল",
        "Shots": "শট",
        "Shots On Target": "লক্ষ্যে শট",
        "Corners": "কর্নার",
        "Fouls": "ফাউল",
        "Assists": "অ্যাসিস্ট",
    }
    return base + "\n\n" + "\n".join(f"{labels.get(key, key)}: {html.escape(value)}" for key, value in stats.items())


def standings_table(rows: list[StandingRow]) -> str:
    if not rows:
        return "⚠️ পয়েন্ট টেবিল পাওয়া যায়নি।"
    border = "+------------+---+----+----+"
    lines = [
        border,
        "| দল        | খে | গোল | পয় |",
        border,
    ]
    for row in rows:
        name = row.team[:10].ljust(10)
        goals = f"{row.goals_for}-{row.goals_against}".rjust(4)
        lines.append(f"| {name} | {row.played:>1} | {goals} | {row.points:>2} |")
    lines.append(border)
    detail = "বিস্তারিত: খে=খেলা, গোল=পক্ষে-বিপক্ষে, পয়=পয়েন্ট"
    return "<pre>" + html.escape("\n".join(lines)) + "</pre>\n" + detail


def news_card(item: NewsItem) -> str:
    return (
        f"<b>📰 {clean_text(item.title, 120)}</b>\n"
        f"{clean_text(item.summary, 260)}\n\n"
        f"প্রকাশিত: {clean_text(item.published, 80)}\n"
        f"সূত্র: {clean_text(item.source, 80)}"
    )
