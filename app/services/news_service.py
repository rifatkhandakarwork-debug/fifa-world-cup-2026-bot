from __future__ import annotations

from datetime import datetime
import html
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

from app.cache import Cache
from app.config import Settings
from app.models.entities import NewsItem
from app.services.http_client import HttpClient


FIFA_SEARCH_KEY = "2kD9zRYRT7xN6kSGs6EoHcvSyKOyK0B4YaKTf1Ygeaw8PM6bgfR6SQ=="


class NewsService:
    def __init__(self, settings: Settings, cache: Cache, http: HttpClient) -> None:
        self.settings = settings
        self.cache = cache
        self.http = http
        self.search_url = "https://cxm-api.fifa.com/fifacxmsearch/api/results"

    async def latest(self, limit: int = 5) -> list[NewsItem]:
        async def loader() -> list[dict]:
            google_items = await self._google_fifa_news(limit)
            if google_items:
                return google_items
            return await self._fifa_search_news(limit)

        raw = await self.cache.remember("cached_news", "fifa:official-news:bn:v3", 900, loader)
        return [NewsItem(**item) for item in raw]

    async def _google_fifa_news(self, limit: int) -> list[dict]:
        query = (
            'site:fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/articles '
            '"FIFA World Cup 2026"'
        )
        text = await self.http.get_text(
            "https://news.google.com/rss/search"
            f"?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        )
        root = ET.fromstring(text)
        items: list[dict] = []
        for node in root.findall("./channel/item"):
            source = node.findtext("source", "")
            title = html.unescape(node.findtext("title", "")).replace(" - FIFA", "").strip()
            link = node.findtext("link", "")
            if "FIFA" not in source and "fifa.com" not in link:
                continue
            description = html.unescape(
                ET.tostring(node.find("description"), encoding="unicode", method="text")
                if node.find("description") is not None
                else ""
            )
            items.append(
                {
                    "title": await self._bn(title),
                    "summary": await self._bn(description or "FIFA World Cup 2026 সম্পর্কিত সর্বশেষ অফিসিয়াল আপডেট।"),
                    "published": node.findtext("pubDate", "সাম্প্রতিক"),
                    "source": "FIFA.com",
                    "url": link,
                }
            )
            if len(items) >= limit:
                break
        return items

    async def _fifa_search_news(self, limit: int) -> list[dict]:
        payload = await self.http.get_any_json(
            self.search_url,
            {
                "locale": "en",
                "searchString": "FIFA World Cup 2026",
                "clientType": "fifaplus",
                "type": "search",
                "context": "default",
                "dateFrom": "2026-01-01",
                "size": 20,
                "from": 0,
            },
            {"X-Functions-Key": FIFA_SEARCH_KEY, "Content-Type": "application/json"},
        )
        hits = (((payload.get("hits") or {}).get("hits")) or [])
        items: list[dict] = []
        for hit in hits:
            source = hit.get("_source") or {}
            url = str(source.get("url") or "")
            title = str(source.get("title") or "")
            if "fifa.com" not in url or not title or "/watch/" in url:
                continue
            summary = str(source.get("description") or "FIFA World Cup 2026 সম্পর্কিত সর্বশেষ অফিসিয়াল আপডেট।")
            published = self._format_date(str(source.get("contentDate") or ""))
            items.append(
                {
                    "title": await self._bn(title),
                    "summary": await self._bn(summary),
                    "published": published,
                    "source": "FIFA.com",
                    "url": url,
                }
            )
            if len(items) >= limit:
                break
        return items

    async def _bn(self, text: str) -> str:
        if not text:
            return ""
        try:
            payload = await self.http.get_any_json(
                "https://translate.googleapis.com/translate_a/single",
                {"client": "gtx", "sl": "en", "tl": "bn", "dt": "t", "q": text},
                {"Origin": "https://translate.google.com", "Referer": "https://translate.google.com/"},
            )
            parts = payload[0] if isinstance(payload, list) and payload else []
            return "".join(part[0] for part in parts if isinstance(part, list) and part)
        except Exception:
            return text

    def _format_date(self, value: str) -> str:
        if not value:
            return "সাম্প্রতিক"
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%d %b %Y")
        except ValueError:
            return value
