from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


def to_local_time(iso_utc: str, timezone: str = "Asia/Dhaka") -> str:
    if not iso_utc:
        return "TBA"
    dt = datetime.fromisoformat(iso_utc.replace("Z", "+00:00"))
    return dt.astimezone(ZoneInfo(timezone)).strftime("%d %b %Y, %I:%M %p")


def date_range_ymd(timezone: str = "Asia/Dhaka", days_before: int = 1, days_after: int = 1) -> tuple[str, str]:
    now = datetime.now(ZoneInfo(timezone))
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    from_dt = start.timestamp() - days_before * 86400
    to_dt = start.timestamp() + days_after * 86400
    return (
        datetime.fromtimestamp(from_dt, ZoneInfo(timezone)).strftime("%Y-%m-%d"),
        datetime.fromtimestamp(to_dt, ZoneInfo(timezone)).strftime("%Y-%m-%d"),
    )
