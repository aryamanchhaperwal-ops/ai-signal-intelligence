"""Abstract Base Collector interface and shared telemetry tracking."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Dict, Generic, List, Optional, Set, TypeVar
from pydantic import BaseModel
from src.utils.http_client import ResilientHttpClient
from src.utils.logging import logger
from src.utils.rate_limiter import AsyncRateLimiter
from src.validation.schemas import RecordType

T = TypeVar("T", bound=BaseModel)


class CollectorMetrics(BaseModel):
    """Execution telemetry for collector runs."""
    collector_name: str
    record_type: RecordType
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_collected: int = 0
    records_failed: int = 0
    duplicates_filtered: int = 0
    pages_processed: int = 0


class BaseCollector(ABC, Generic[T]):
    """Standardized asynchronous data collector interface."""

    def __init__(
        self,
        name: str,
        source_name: str,
        source_base_url: str,
        record_type: RecordType,
        http_client: Optional[ResilientHttpClient] = None,
        rate_limiter: Optional[AsyncRateLimiter] = None,
    ) -> None:
        self.name = name
        self.source_name = source_name
        self.source_base_url = source_base_url
        self.record_type = record_type
        self.http_client = http_client or ResilientHttpClient()
        self.rate_limiter = rate_limiter
        self.seen_identifiers: Set[str] = set()
        self.metrics = CollectorMetrics(
            collector_name=name,
            record_type=record_type,
            started_at=datetime.now(timezone.utc),
        )

    def is_duplicate(self, unique_key: str) -> bool:
        """Check and record unique identifier for deduplication."""
        if unique_key in self.seen_identifiers:
            self.metrics.duplicates_filtered += 1
            return True
        self.seen_identifiers.add(unique_key)
        return False

    @abstractmethod
    async def collect(self, limit: Optional[int] = None) -> List[T]:
        """Execute end-to-end data collection workflow.

        Args:
            limit: Maximum number of unique records to collect.

        Returns:
            List of strictly validated Pydantic domain models.
        """
        pass

    async def close(self) -> None:
        """Release underlying HTTP client resources."""
        if self.http_client:
            await self.http_client.close()
