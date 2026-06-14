from __future__ import annotations

import logging
from typing import Any

import aiohttp


logger = logging.getLogger(__name__)


class ApiError(RuntimeError):
    pass


class HttpClient:
    async def get_json(self, url: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {"Origin": "https://www.fifa.com", "Referer": "https://www.fifa.com/"}
        try:
            async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(url, params=params) as response:
                    text = await response.text()
                    if response.status >= 400:
                        raise ApiError(f"API returned {response.status}: {text[:200]}")
                    payload = await response.json(content_type=None)
                    return payload if isinstance(payload, dict) else {}
        except Exception as exc:
            logger.exception("Failed to fetch JSON from %s", url)
            raise ApiError(str(exc)) from exc

    async def get_any_json(self, url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None) -> Any:
        request_headers = {"Origin": "https://www.fifa.com", "Referer": "https://www.fifa.com/"}
        if headers:
            request_headers.update(headers)
        try:
            async with aiohttp.ClientSession(headers=request_headers, timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(url, params=params) as response:
                    text = await response.text()
                    if response.status >= 400:
                        raise ApiError(f"API returned {response.status}: {text[:200]}")
                    return await response.json(content_type=None)
        except Exception as exc:
            logger.exception("Failed to fetch JSON from %s", url)
            raise ApiError(str(exc)) from exc

    async def get_text(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=20)) as session:
                async with session.get(url) as response:
                    if response.status >= 400:
                        raise ApiError(f"API returned {response.status}")
                    return await response.text()
        except Exception as exc:
            logger.exception("Failed to fetch text from %s", url)
            raise ApiError(str(exc)) from exc
