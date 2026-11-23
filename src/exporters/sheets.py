"""Google Sheets API Exporter Stub."""

from typing import Any, Dict, List, Optional
from src.utils.config import settings
from src.utils.logging import logger


class GoogleSheetsExporter:
    """Syncs extracted datasets directly to Google Sheets for collaborative live intelligence."""

    def __init__(
        self,
        spreadsheet_id: Optional[str] = None,
        credentials_file: Optional[str] = None,
    ) -> None:
        self.spreadsheet_id = spreadsheet_id or settings.GOOGLE_SHEETS_SPREADSHEET_ID
        self.credentials_file = credentials_file or settings.GOOGLE_SHEETS_CREDENTIALS_JSON

    async def publish_tab(self, tab_name: str, rows: List[Dict[str, Any]]) -> bool:
        """Publish rows to Google Sheets."""
        if not self.spreadsheet_id or not self.credentials_file:
            logger.info("Google Sheets credentials not configured. Skipping cloud sync for '%s'.", tab_name)
            return False
        logger.info("Publishing %d rows to Google Sheet '%s' tab '%s'", len(rows), self.spreadsheet_id, tab_name)
        # Prepared for google-api-python-client authentication
        return True
