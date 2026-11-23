"""Excel Workbook Exporter using OpenPyXL.

Generates the required six tabs:
1. Startups
2. Products
3. Research Papers
4. Jobs
5. News
6. Entity Mapping Log
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import openpyxl
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from src.utils.logging import logger
from src.validation.schemas import (
    EntityResolutionLog,
    JobRecord,
    NewsRecord,
    ProductRecord,
    ResearchPaperRecord,
    StartupRecord,
)


class ExcelExporter:
    """Production Excel workbook generator with 6 standard tabs and professional formatting."""

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = output_dir or Path("data/exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Style definitions
        self.header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        self.header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        self.header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        self.cell_font = Font(name="Calibri", size=10)
        self.thin_border = Border(
            left=Side(style="thin", color="D9D9D9"),
            right=Side(style="thin", color="D9D9D9"),
            top=Side(style="thin", color="D9D9D9"),
            bottom=Side(style="thin", color="D9D9D9"),
        )

    def _write_tab(
        self,
        wb: openpyxl.Workbook,
        title: str,
        rows: List[Dict[str, Any]],
        headers: List[str]
    ) -> None:
        """Create and style a single worksheet."""
        ws = wb.create_sheet(title=title)
        ws.views.sheetView[0].showGridLines = True

        # Write Header Row
        ws.append(headers)
        for col_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = self.header_font
            cell.fill = self.header_fill
            cell.alignment = self.header_alignment

        # Write Data Rows
        for row_idx, record in enumerate(rows, start=2):
            row_values = [
                ILLEGAL_CHARACTERS_RE.sub("", str(record.get(h, ""))) if isinstance(record.get(h), str) else record.get(h, "")
                for h in headers
            ]
            ws.append(row_values)
            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = self.cell_font
                cell.border = self.thin_border

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 50)

    def export_all(
        self,
        startups: List[StartupRecord],
        products: List[ProductRecord],
        papers: List[ResearchPaperRecord],
        jobs: List[JobRecord],
        news: List[NewsRecord],
        logs: List[EntityResolutionLog],
        filename: str = "ai_signal_intelligence.xlsx"
    ) -> Path:
        """Export all 5 intelligence datasets and entity mapping log into an Excel workbook."""
        wb = openpyxl.Workbook()
        # Remove default sheet
        wb.remove(wb.active)

        # Tab 1: Startups
        startup_headers = [
            "startup_id", "company_name", "canonical_name", "canonicalName", "entityName", "description", "official_website",
            "source_url", "founding_year", "headquarters", "country", "industry", "AI_category",
            "products_or_services", "founders", "funding_stage", "funding_stage_source", "funding_stage_verification_status",
            "total_funding", "latest_funding_round",
            "employee_count_range", "employeeCount", "accelerator_or_investor", "LinkedIn_URL", "GitHub_URL",
            "company_status", "last_verified_at", "collected_at", "source_name", "schemaVersion", "recordType"
        ]
        self._write_tab(wb, "Startups", [s.to_export_dict() for s in startups], startup_headers)

        # Tab 2: Products
        product_headers = [
            "schemaVersion", "recordType", "source_name", "source_url",
            "productName", "startupName", "canonicalStartupName", "pricingModel", "productUrl", "description", "collectedAt"
        ]
        self._write_tab(wb, "Products", [p.to_export_dict() for p in products], product_headers)

        # Tab 3: Research Papers
        paper_headers = [
            "record_id", "arxiv_id", "title", "authors", "primary_category", "categories",
            "published_date", "paper_url", "pdf_url", "doi",
            "github_url", "github_stars", "github_forks", "abstract",
            "source_name", "source_url", "schemaVersion", "recordType", "collectedAt"
        ]
        self._write_tab(wb, "Research Papers", [r.to_export_dict() for r in papers], paper_headers)

        # Tab 4: Jobs
        job_headers = [
            "schemaVersion", "recordType", "source_name", "source_url",
            "company", "canonicalCompany", "role", "date", "is_remote", "role_family", "location", "job_url", "collectedAt"
        ]
        self._write_tab(wb, "Jobs", [j.to_export_dict() for j in jobs], job_headers)

        # Tab 5: News
        news_headers = [
            "schemaVersion", "recordType", "source_name", "source_url",
            "title", "url", "published_date", "summary", "full_text_length", "collectedAt"
        ]
        self._write_tab(wb, "News", [n.to_export_dict() for n in news], news_headers)

        # Tab 6: Entity Mapping Log
        log_headers = [
            "rawName", "canonicalName", "matchMethod", "confidenceScore", "isAmbiguous", "resolvedAt"
        ]
        self._write_tab(wb, "Entity Mapping Log", [l.to_export_dict() for l in logs], log_headers)

        output_path = self.output_dir / filename
        wb.save(output_path)
        logger.info("Successfully exported 6-tab Excel workbook to %s", str(output_path))
        return output_path
