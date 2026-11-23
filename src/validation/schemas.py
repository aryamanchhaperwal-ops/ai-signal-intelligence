"""Pydantic Schema Definitions for AI Signal Intelligence Pipeline.

All models adhere strictly to assignment data schemas, preserving source traceability,
ISO-8601 timestamps, explicit typing, and strict validation.
No values are invented; missing fields default to None.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
import re
from typing import Any, Dict, List, Literal, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class RecordType(str, Enum):
    """Enumeration of ingestion record categories."""
    STARTUP = "startup"
    PRODUCT = "product"
    RESEARCH_PAPER = "research_paper"
    JOB = "job"
    NEWS = "news"


class PricingModel(str, Enum):
    """Normalized pricing models for AI products."""
    FREE = "FREE"
    FREEMIUM = "FREEMIUM"
    PAID = "PAID"
    ENTERPRISE = "ENTERPRISE"


class RoleFamily(str, Enum):
    """Normalized role families for AI job postings."""
    RESEARCH = "RESEARCH"
    ENGINEERING = "ENGINEERING"
    PRODUCT = "PRODUCT"
    OPERATIONS = "OPERATIONS"
    SALES = "SALES"
    OTHER = "OTHER"


class SourceMetadata(BaseModel):
    """Metadata describing the origin of a collected record for absolute traceability."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., min_length=1, description="Originating source name (e.g., Arxiv, YCombinator)")
    url: str = Field(..., min_length=1, description="Source URL where record was discovered")


# ==============================================================================
# 1. STARTUP SCHEMA
# Target: schemaVersion, recordType, source.name, source.url,
#         content.entityName, content.data.employeeCount, collectedAt
# ==============================================================================

class StartupData(BaseModel):
    """Granular nested data payload for startup entities."""
    model_config = ConfigDict(extra="ignore")

    employeeCount: Optional[int] = Field(None, ge=1, description="Verified employee headcount if available")
    description: Optional[str] = Field(None, description="Company overview / summary")
    websiteUrl: Optional[str] = Field(None, description="Official company website URL")


class StartupContent(BaseModel):
    """Content wrapper for startup records."""
    model_config = ConfigDict(extra="ignore")

    startup_id: Optional[str] = Field(None, description="Unique startup identifier")
    entityName: str = Field(..., min_length=1, description="Raw entity name")
    company_name: Optional[str] = Field(None, description="Canonical company name alias")
    canonicalName: Optional[str] = Field(None, description="Resolved canonical entity name from resolution engine")
    description: Optional[str] = Field(None, description="Company description / overview")
    official_website: Optional[str] = Field(None, description="Official company website")
    source_url: Optional[str] = Field(None, description="Source profile URL")
    founding_year: Optional[int] = Field(None, ge=1900, le=2030, description="Year founded")
    headquarters: Optional[str] = Field(None, description="Headquarters city/state/region")
    country: Optional[str] = Field(None, description="Operating country")
    industry: Optional[str] = Field("Artificial Intelligence", description="Primary industry")
    AI_category: Optional[str] = Field(None, description="Specific AI subcategory")
    products_or_services: Optional[str] = Field(None, description="Primary products or services")
    founders: Optional[str] = Field(None, description="Company founders")
    funding_stage: Optional[str] = Field(None, description="Funding stage (e.g., Seed, Series A, Growth)")
    funding_stage_source: Optional[str] = Field(None, description="Verifiable provenance source for funding stage")
    funding_stage_verification_status: Optional[str] = Field(None, description="Verification status: SOURCED, INFERRED, UNAVAILABLE")
    total_funding: Optional[str] = Field(None, description="Total capital raised")
    latest_funding_round: Optional[str] = Field(None, description="Latest funding round details")
    employee_count_range: Optional[str] = Field(None, description="Employee count range or headcount")
    accelerator_or_investor: Optional[str] = Field(None, description="Associated accelerator or key investor")
    LinkedIn_URL: Optional[str] = Field(None, description="Official LinkedIn page")
    GitHub_URL: Optional[str] = Field(None, description="Official GitHub organization")
    company_status: Optional[str] = Field("Active", description="Operating status (Active, Acquired, Closed)")
    last_verified_at: Optional[str] = Field(None, description="ISO-8601 last verification timestamp")
    data: StartupData = Field(default_factory=StartupData, description="Nested startup metrics")


class StartupRecord(BaseModel):
    """Top-level validated startup record."""
    model_config = ConfigDict(extra="ignore")

    schemaVersion: str = Field("1.0.0", description="Semantic schema version")
    recordType: Literal[RecordType.STARTUP] = Field(RecordType.STARTUP)
    source: SourceMetadata
    content: StartupContent
    collectedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO-8601 collection timestamp"
    )

    def to_export_dict(self) -> Dict[str, Any]:
        """Flatten record for Excel / CSV export."""
        cid = self.content.canonicalName or self.content.entityName
        slug = re.sub(r'[^a-zA-Z0-9]', '_', cid.lower()).strip('_')
        sid = self.content.startup_id or f"startup_{slug}"
        emp = self.content.data.employeeCount
        emp_range = self.content.employee_count_range or (f"{emp}" if emp else "")
        desc = self.content.description or self.content.data.description or ""
        web = self.content.official_website or self.content.data.websiteUrl or ""

        return {
            "startup_id": sid,
            "company_name": self.content.entityName,
            "canonical_name": cid,
            "description": desc,
            "official_website": web,
            "source_url": self.content.source_url or self.source.url,
            "founding_year": self.content.founding_year or "",
            "headquarters": self.content.headquarters or "",
            "country": self.content.country or "",
            "industry": self.content.industry or "Artificial Intelligence",
            "AI_category": self.content.AI_category or "",
            "products_or_services": self.content.products_or_services or "",
            "founders": self.content.founders or "",
            "funding_stage": self.content.funding_stage or "",
            "funding_stage_source": self.content.funding_stage_source or "",
            "funding_stage_verification_status": self.content.funding_stage_verification_status or "",
            "total_funding": self.content.total_funding or "",
            "latest_funding_round": self.content.latest_funding_round or "",
            "employee_count_range": emp_range,
            "accelerator_or_investor": self.content.accelerator_or_investor or "",
            "LinkedIn_URL": self.content.LinkedIn_URL or "",
            "GitHub_URL": self.content.GitHub_URL or "",
            "company_status": self.content.company_status or "Active",
            "last_verified_at": self.content.last_verified_at or self.collectedAt.isoformat(),
            "collected_at": self.collectedAt.isoformat(),
            "collectedAt": self.collectedAt.isoformat(),
            # Legacy fields for backward compatibility
            "entityName": self.content.entityName,
            "canonicalName": cid,
            "employeeCount": emp,
            "websiteUrl": web,
            "source_name": self.source.name,
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType.value,
        }


# ==============================================================================
# 2. PRODUCT SCHEMA
# Target: schemaVersion, recordType, source.name, source.url,
#         content.startupName, content.pricingModel, collectedAt
# ==============================================================================

class ProductContent(BaseModel):
    """Content wrapper for AI product records."""
    model_config = ConfigDict(extra="ignore")

    productName: str = Field(..., min_length=1, description="Official product name")
    startupName: str = Field(..., min_length=1, description="Associated startup or organization name")
    canonicalStartupName: Optional[str] = Field(None, description="Resolved canonical company name")
    pricingModel: PricingModel = Field(..., description="Normalized pricing model (FREE, FREEMIUM, PAID, ENTERPRISE)")
    description: Optional[str] = Field(None, description="Product summary / functionality")
    productUrl: Optional[str] = Field(None, description="Product landing or access URL")


class ProductRecord(BaseModel):
    """Top-level validated AI product record."""
    model_config = ConfigDict(extra="ignore")

    schemaVersion: str = Field("1.0.0", description="Semantic schema version")
    recordType: Literal[RecordType.PRODUCT] = Field(RecordType.PRODUCT)
    source: SourceMetadata
    content: ProductContent
    collectedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO-8601 collection timestamp"
    )

    def to_export_dict(self) -> Dict[str, Any]:
        """Flatten record for Excel / CSV export."""
        return {
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType.value,
            "source_name": self.source.name,
            "source_url": self.source.url,
            "productName": self.content.productName,
            "startupName": self.content.startupName,
            "canonicalStartupName": self.content.canonicalStartupName or self.content.startupName,
            "pricingModel": self.content.pricingModel.value,
            "productUrl": self.content.productUrl,
            "description": self.content.description,
            "collectedAt": self.collectedAt.isoformat(),
        }


# ==============================================================================
# 3. RESEARCH PAPER SCHEMA
# Target: schemaVersion, recordType, content.title, content.authors,
#         content.paper_url, content.github_url, content.github_stars, content.published_date
# ==============================================================================

class ResearchPaperContent(BaseModel):
    """Content wrapper for research paper records."""
    model_config = ConfigDict(extra="ignore")

    record_id: Optional[str] = Field(None, description="Unique record identifier")
    arxiv_id: Optional[str] = Field(None, description="arXiv accession ID (e.g., 2401.00001)")
    title: str = Field(..., min_length=1, description="Paper title")
    authors: List[str] = Field(default_factory=list, description="List of paper authors")
    paper_url: str = Field(..., min_length=1, description="Direct URL to research paper")
    pdf_url: Optional[str] = Field(None, description="Direct link to PDF document")
    primary_category: str = Field("cs.AI", description="Primary arXiv category code")
    categories: List[str] = Field(default_factory=list, description="All assigned categories")
    doi: Optional[str] = Field(None, description="Digital Object Identifier if available")
    github_url: Optional[str] = Field(None, description="Official or associated GitHub repository URL")
    github_stars: Optional[int] = Field(None, ge=0, description="Verified GitHub star count from REST API")
    github_forks: Optional[int] = Field(None, ge=0, description="Verified GitHub fork count from REST API")
    published_date: str = Field(..., description="ISO-8601 publication date string (YYYY-MM-DD or datetime)")
    abstract: Optional[str] = Field(None, description="Paper abstract / summary")
    comment: Optional[str] = Field(None, description="Author comments / notes")


class ResearchPaperRecord(BaseModel):
    """Top-level validated research paper record."""
    model_config = ConfigDict(extra="ignore")

    schemaVersion: str = Field("1.0.0", description="Semantic schema version")
    recordType: Literal[RecordType.RESEARCH_PAPER] = Field(RecordType.RESEARCH_PAPER)
    source: SourceMetadata
    content: ResearchPaperContent
    collectedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO-8601 collection timestamp"
    )

    def to_export_dict(self) -> Dict[str, Any]:
        """Flatten record for Excel / CSV export."""
        rec_id = self.content.record_id or (f"arxiv_{self.content.arxiv_id}" if self.content.arxiv_id else "")
        return {
            "record_id": rec_id,
            "arxiv_id": self.content.arxiv_id or "",
            "title": self.content.title,
            "authors": ", ".join(self.content.authors) if isinstance(self.content.authors, list) else str(self.content.authors),
            "primary_category": self.content.primary_category,
            "categories": ", ".join(self.content.categories) if isinstance(self.content.categories, list) else str(self.content.categories),
            "published_date": self.content.published_date,
            "paper_url": self.content.paper_url,
            "pdf_url": self.content.pdf_url or "",
            "doi": self.content.doi or "",
            "github_url": self.content.github_url or "",
            "github_stars": self.content.github_stars if self.content.github_stars is not None else "",
            "github_forks": self.content.github_forks if self.content.github_forks is not None else "",
            "abstract": self.content.abstract or "",
            "source_name": self.source.name,
            "source_url": self.source.url,
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType.value,
            "collectedAt": self.collectedAt.isoformat(),
        }


# ==============================================================================
# 4. JOB SCHEMA
# Target: schemaVersion, recordType, content.company, content.date,
#         content.is_remote, content.role_family
# ==============================================================================

class JobContent(BaseModel):
    """Content wrapper for AI job postings."""
    model_config = ConfigDict(extra="ignore")

    company: str = Field(..., min_length=1, description="Hiring organization name")
    canonicalCompany: Optional[str] = Field(None, description="Resolved canonical company name")
    role: str = Field(..., min_length=1, description="Job title / position")
    date: str = Field(..., description="ISO-8601 publication date of posting")
    is_remote: bool = Field(..., description="Whether position is remote-eligible")
    role_family: RoleFamily = Field(..., description="Normalized role category")
    location: Optional[str] = Field(None, description="Physical location or region")
    job_url: Optional[str] = Field(None, description="Application or job posting URL")


class JobRecord(BaseModel):
    """Top-level validated job record."""
    model_config = ConfigDict(extra="ignore")

    schemaVersion: str = Field("1.0.0", description="Semantic schema version")
    recordType: Literal[RecordType.JOB] = Field(RecordType.JOB)
    source: SourceMetadata
    content: JobContent
    collectedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO-8601 collection timestamp"
    )

    def to_export_dict(self) -> Dict[str, Any]:
        """Flatten record for Excel / CSV export."""
        return {
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType.value,
            "source_name": self.source.name,
            "source_url": self.source.url,
            "company": self.content.company,
            "canonicalCompany": self.content.canonicalCompany or self.content.company,
            "role": self.content.role,
            "date": self.content.date,
            "is_remote": self.content.is_remote,
            "role_family": self.content.role_family.value,
            "location": self.content.location or "",
            "job_url": self.content.job_url or "",
            "collectedAt": self.collectedAt.isoformat(),
        }


# ==============================================================================
# 5. NEWS SCHEMA
# Target: source info, title, URL, full-text content, publication timestamp,
#         collection timestamp
# ==============================================================================

class NewsContent(BaseModel):
    """Content wrapper for AI news articles."""
    model_config = ConfigDict(extra="ignore")

    title: str = Field(..., min_length=1, description="Headline / article title")
    url: str = Field(..., min_length=1, description="Direct URL to article")
    full_text: Optional[str] = Field(None, description="Full-text article body where permitted")
    summary: Optional[str] = Field(None, description="Brief synopsis / abstract")
    published_date: str = Field(..., description="ISO-8601 publication timestamp")


class NewsRecord(BaseModel):
    """Top-level validated news record."""
    model_config = ConfigDict(extra="ignore")

    schemaVersion: str = Field("1.0.0", description="Semantic schema version")
    recordType: Literal[RecordType.NEWS] = Field(RecordType.NEWS)
    source: SourceMetadata
    content: NewsContent
    collectedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO-8601 collection timestamp"
    )

    def to_export_dict(self) -> Dict[str, Any]:
        """Flatten record for Excel / CSV export."""
        return {
            "schemaVersion": self.schemaVersion,
            "recordType": self.recordType.value,
            "source_name": self.source.name,
            "source_url": self.source.url,
            "title": self.content.title,
            "url": self.content.url,
            "published_date": self.content.published_date,
            "summary": self.content.summary or "",
            "full_text_length": len(self.content.full_text) if self.content.full_text else 0,
            "collectedAt": self.collectedAt.isoformat(),
        }


# ==============================================================================
# 6. ENTITY RESOLUTION LOG SCHEMA (Export Tab 6)
# ==============================================================================

class EntityResolutionLog(BaseModel):
    """Traceable audit log entry for entity normalization and resolution."""
    model_config = ConfigDict(extra="ignore")

    rawName: str = Field(..., min_length=1, description="Raw entity name as scraped")
    canonicalName: str = Field(..., min_length=1, description="Assigned canonical entity name")
    matchMethod: str = Field(..., description="Resolution strategy: EXACT, SEED_EXACT, FUZZY_RAPIDFUZZ, MANUAL")
    confidenceScore: float = Field(..., ge=0.0, le=1.0, description="Match confidence score [0.0 - 1.0]")
    isAmbiguous: bool = Field(default=False, description="Whether entity match was flagged as ambiguous")
    resolvedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="ISO-8601 resolution timestamp"
    )

    def to_export_dict(self) -> Dict[str, Any]:
        """Flatten record for Excel / CSV export."""
        return {
            "rawName": self.rawName,
            "canonicalName": self.canonicalName,
            "matchMethod": self.matchMethod,
            "confidenceScore": round(self.confidenceScore, 4),
            "isAmbiguous": self.isAmbiguous,
            "resolvedAt": self.resolvedAt.isoformat(),
        }
