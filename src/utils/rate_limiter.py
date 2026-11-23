"""Async Rate Limiting and Token Bucket Implementation with Jitter."""

import asyncio
import random
import time


class AsyncRateLimiter:
    """Thread-safe and async-safe token bucket rate limiter with randomized polite jitter."""

    def __init__(
        self,
        rate_limit: float,
        time_period: float = 1.0,
        min_jitter_ms: int = 100,
        max_jitter_ms: int = 400
    ) -> None:
        """Initialize the rate limiter.

        Args:
            rate_limit: Maximum number of operations permitted within time_period.
            time_period: Window duration in seconds.
            min_jitter_ms: Minimum randomized sleep added between calls in milliseconds.
            max_jitter_ms: Maximum randomized sleep added between calls in milliseconds.
        """
        self.rate_limit = rate_limit
        self.time_period = time_period
        self.min_jitter_ms = min_jitter_ms
        self.max_jitter_ms = max_jitter_ms

        self.tokens = rate_limit
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until a token is available, consume it, and add polite randomized jitter."""
        async with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_refill

                # Refill tokens proportional to elapsed time
                self.tokens = min(self.rate_limit, self.tokens + elapsed * (self.rate_limit / self.time_period))
                self.last_refill = now

                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    break

                # Sleep until at least one token is replenished
                needed = 1.0 - self.tokens
                wait_time = needed * (self.time_period / self.rate_limit)
                await asyncio.sleep(max(wait_time, 0.05))

        # Add courteous jitter
        if self.max_jitter_ms > 0:
            jitter = random.uniform(self.min_jitter_ms / 1000.0, self.max_jitter_ms / 1000.0)
            await asyncio.sleep(jitter)
