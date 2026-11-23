"""Per-category CSV exporter supporting downstream data warehouse loading."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from src.utils.logging import logger


class CsvExporter:
    """Exports structured domain records to standalone CSV files."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir or Path("data/exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, records: List[Dict[str, Any]], category: str) -> Path:
        """Export list of dictionaries to category CSV."""
        filepath = self.output_dir / f"{category}.csv"
        if not records:
            # Write empty dataframe with headers if known
            df = pd.DataFrame()
        else:
            df = pd.DataFrame(records)
        df.to_csv(filepath, index=False, encoding="utf-8")
        logger.info("Exported %d records to %s", len(df), str(filepath))
        return filepath
