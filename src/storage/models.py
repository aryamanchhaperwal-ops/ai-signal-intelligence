"""SQLAlchemy Declarative Models for PostgreSQL / SQLite storage."""

from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StartupDB(Base):
    __tablename__ = "startups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_version = Column(String(16), default="1.0.0")
    startup_id = Column(String(128), unique=True, nullable=True, index=True)
    source_name = Column(String(128), nullable=False)
    source_url = Column(String(512), nullable=False)
    entity_name = Column(String(256), nullable=False)
    canonical_name = Column(String(256), nullable=True, index=True)
    employee_count = Column(Integer, nullable=True)
    employee_count_range = Column(String(64), nullable=True)
    website_url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    founding_year = Column(Integer, nullable=True)
    headquarters = Column(String(256), nullable=True)
    country = Column(String(128), nullable=True)
    industry = Column(String(128), default="Artificial Intelligence")
    ai_category = Column(String(128), nullable=True)
    products_or_services = Column(Text, nullable=True)
    founders = Column(Text, nullable=True)
    funding_stage = Column(String(64), nullable=True)
    funding_stage_source = Column(String(128), nullable=True)
    funding_stage_verification_status = Column(String(64), nullable=True)
    total_funding = Column(String(128), nullable=True)
    latest_funding_round = Column(String(128), nullable=True)
    accelerator_or_investor = Column(String(256), nullable=True)
    linkedin_url = Column(String(512), nullable=True)
    github_url = Column(String(512), nullable=True)
    company_status = Column(String(64), default="Active")
    last_verified_at = Column(DateTime, nullable=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_version = Column(String(16), default="1.0.0")
    source_name = Column(String(128), nullable=False)
    source_url = Column(String(512), nullable=False)
    product_name = Column(String(256), nullable=False)
    startup_name = Column(String(256), nullable=False)
    canonical_startup_name = Column(String(256), nullable=True, index=True)
    pricing_model = Column(String(32), nullable=False)
    product_url = Column(String(512), nullable=True)
    description = Column(Text, nullable=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class ResearchPaperDB(Base):
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_version = Column(String(16), default="1.0.0")
    record_id = Column(String(128), unique=True, nullable=True, index=True)
    arxiv_id = Column(String(64), unique=True, nullable=True, index=True)
    source_name = Column(String(128), nullable=False)
    source_url = Column(String(512), nullable=False)
    title = Column(String(512), nullable=False, index=True)
    authors = Column(Text, nullable=False)
    primary_category = Column(String(64), nullable=True)
    categories = Column(Text, nullable=True)
    paper_url = Column(String(512), unique=True, nullable=False)
    pdf_url = Column(String(512), nullable=True)
    doi = Column(String(128), nullable=True)
    github_url = Column(String(512), nullable=True)
    github_stars = Column(Integer, nullable=True)
    github_forks = Column(Integer, nullable=True)
    published_date = Column(String(64), nullable=False, index=True)
    abstract = Column(Text, nullable=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class JobDB(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_version = Column(String(16), default="1.0.0")
    source_name = Column(String(128), nullable=False)
    source_url = Column(String(512), nullable=False)
    company = Column(String(256), nullable=False)
    canonical_company = Column(String(256), nullable=True, index=True)
    role = Column(String(256), nullable=False)
    date = Column(String(64), nullable=False, index=True)
    is_remote = Column(Boolean, nullable=False)
    role_family = Column(String(64), nullable=False, index=True)
    location = Column(String(256), nullable=True)
    job_url = Column(String(512), nullable=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class NewsDB(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, autoincrement=True)
    schema_version = Column(String(16), default="1.0.0")
    source_name = Column(String(128), nullable=False)
    source_url = Column(String(512), nullable=False)
    title = Column(String(512), nullable=False)
    url = Column(String(512), unique=True, nullable=False)
    published_date = Column(String(64), nullable=False, index=True)
    summary = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    collected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)


class EntityResolutionLogDB(Base):
    __tablename__ = "entity_resolution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_name = Column(String(256), nullable=False)
    canonical_name = Column(String(256), nullable=False)
    match_method = Column(String(64), nullable=False)
    confidence_score = Column(Float, nullable=False)
    is_ambiguous = Column(Boolean, default=False)
    resolved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
