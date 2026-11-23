"""Resilient Async HTTP Client with Retries, Jitter, and Polite Header Management."""

import asyncio
from typing import Any, Dict, Optional
import aiohttp
from src.utils.config import settings
from src.utils.logging import logger
from src.utils.rate_limiter import AsyncRateLimiter


class ResilientHttpClient:
    """Async HTTP Client wrapping aiohttp.ClientSession with rate limiting, timeouts, and retries."""

    def __init__(
        self,
        concurrency_limit: int = 10,
        rate_limiter: Optional[AsyncRateLimiter] = None,
        default_headers: Optional[Dict[str, str]] = None,
    ) -> None:
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.rate_limiter = rate_limiter or AsyncRateLimiter(
            rate_limit=10.0,
            time_period=1.0,
            min_jitter_ms=settings.POLITE_DELAY_MIN_MS,
            max_jitter_ms=settings.POLITE_DELAY_MAX_MS,
        )
        self._session: Optional[aiohttp.ClientSession] = None
        self._default_headers = default_headers or {
            "User-Agent": settings.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
        }

    async def get_session(self) -> aiohttp.ClientSession:
        """Lazily initialize client session within current event loop."""
        if self._session is None or self._session.closed:
            import certifi
            import ssl
            ssl_ctx = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_ctx)
            timeout = aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT_SECONDS)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._default_headers,
                connector=connector,
            )
        return self._session

    async def fetch(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ) -> Optional[str]:
        """Fetch URL content with exponential backoff and rate limiting.

        Args:
            url: Target URL to retrieve.
            params: Query parameters.
            headers: Specific request headers to merge.
            max_retries: Retry attempts on transient network or 429/5xx errors.
            backoff_factor: Multiplier for exponential backoff.

        Returns:
            Decoded text content or None on unrecoverable failure.
        """
        session = await self.get_session()
        merged_headers = {**self._default_headers, **(headers or {})}

        for attempt in range(1, max_retries + 1):
            await self.rate_limiter.acquire()
            try:
                async with self.semaphore:
                    async with session.get(url, params=params, headers=merged_headers) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status in (429, 500, 502, 503, 504):
                            wait_time = backoff_factor ** attempt
                            logger.warning(
                                "HTTP status %d received for %s. Retrying in %.2fs (attempt %d/%d)",
                                response.status, url, wait_time, attempt, max_retries
                            )
                            await asyncio.sleep(wait_time)
                        elif response.status in (403, 401):
                            logger.error(
                                "Access denied (HTTP %d) for %s. Respecting access controls.",
                                response.status, url
                            )
                            return None
                        else:
                            logger.error("HTTP error %d for URL: %s", response.status, url)
                            return None
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                wait_time = backoff_factor ** attempt
                logger.warning(
                    "Network error (%s) on attempt %d/%d for %s. Retrying in %.2fs",
                    str(err), attempt, max_retries, url, wait_time
                )
                await asyncio.sleep(wait_time)

        logger.error("Exhausted %d retries fetching %s", max_retries, url)
        return None

    async def close(self) -> None:
        """Close client session and free connections."""
        if self._session and not self._session.closed:
            await self._session.close()
