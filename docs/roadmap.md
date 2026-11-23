# AI Signal Intelligence Engine — Technical Implementation Roadmap

**Document Status:** Phased Engineering Plan  
**Target Milestone:** Full Production Ingestion & Delivery  

---

## Phase Overview

| Phase | Module / Capability | Status | Target Deliverables |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Foundation, Architecture & Schemas | **Completed** | Modular directories, Pydantic schemas, initial configs, 50-seed resolver, tests. |
| **Phase 2** | Startup & Product Ingestion | Pending | Live directory parsers, pagination, concurrency controls, pricing normalization. |
| **Phase 3** | Research Paper & GitHub Stars | Pending | Arxiv API client, regex repo discovery, authenticated GitHub REST API client. |
| **Phase 4** | Real-Time News & Jobs (24h Window) | Pending | 5 news RSS/HTML parsers, 5 job board parsers, 24h temporal filtering. |
| **Phase 5** | LLM Extraction & Provider Failover | Pending | Gemini Flash + Groq Llama + DeepSeek integration, chunking, backoff. |
| **Phase 6** | Entity Resolution Pipeline | Pending | Full dataset pass-through normalization, ambiguity reporting, mapping log export. |
| **Phase 7** | Storage & Database Upsert Engine | Pending | PostgreSQL/SQLite idempotent storage, async session management, schema migrations. |
| **Phase 8** | Workbook & Spreadsheet Publishing | Pending | OpenPyXL 6-tab workbook generation, CSV exports, Google Sheets sync. |
| **Phase 9** | End-to-End Orchestration & Testing | Pending | Full integration test suite, error simulation, CLI execution scripts. |
| **Phase 10** | 500k+ Scale Hardening | Future Roadmap| Distributed worker deployment (Celery/Temporal), Redis coordination, partitioning. |

---

## Detailed Phase Breakdown

### Phase 1: Foundation, Architecture & Project Initialization (Current)
- [x] Inspect workspace and verify Python 3.11+ environment.
- [x] Create modular project structure (`src/`, `tests/`, `data/`, `logs/`, `docs/`).
- [x] Define Pydantic v2 schemas for Startups, Products, Research Papers, Jobs, News, and Entity Logs.
- [x] Create centralized configuration management (`Settings` via `pydantic-settings`).
- [x] Implement structured logging, async rate limiter with token bucket & jitter, resilient HTTP client.
- [x] Curate seed database of 50 prominent AI startups with known aliases.
- [x] Implement `EntityResolver` with deterministic normalization, exact matching, and RapidFuzz scoring.
- [x] Write `architecture.md` and `docs/roadmap.md`.
- [x] Create unit tests for schemas, entity resolution, and configuration.

### Phase 2: Startup & Product Ingestion
- **Objective:** Collect $\ge 1,000$ unique startups and $\ge 1,000$ unique products with zero hallucinations.
- **Data Sources:** Authorized startup registries, Y Combinator directory, Hugging Face company feeds, Product Hunt AI directories.
- **Tasks:**
  - Implement async pagination with rate limiting.
  - Extract company name, website URL, description, employee count.
  - Extract product name, parent organization, normalized pricing model (`FREE`, `FREEMIUM`, `PAID`, `ENTERPRISE`).
  - Run entity resolution on company names during ingestion.

### Phase 3: Research Paper Collector & GitHub Metrics
- **Objective:** Collect $\ge 1,000$ AI research papers with verified GitHub repository stars.
- **Data Sources:** Arxiv API (`cs.AI`, `cs.LG`, `cs.CL`, `stat.ML`), Papers with Code API.
- **Tasks:**
  - Implement XML/Atom feed parser for Arxiv API query pagination (`export.arxiv.org/api/query`).
  - Parse publication dates, author lists, PDF/abs URLs.
  - Regex pattern matching for GitHub links within paper abstracts and commentary.
  - Query GitHub REST API (`/repos/{owner}/{repo}`) using `GITHUB_TOKEN` to retrieve `stargazers_count`.
  - Record `github_stars = null` when no repository exists.

### Phase 4: News & Job Feed Ingestion (Strict 24h Window)
- **Objective:** Ingest all qualifying news articles and jobs published within the preceding 24 hours.
- **Data Sources (News):** VentureBeat AI, TechCrunch AI, MIT Technology Review AI, The Verge AI, Ars Technica AI.
- **Data Sources (Jobs):** YC Work at a Startup, AIJobs Net, RemoteOK AI, WeWorkRemotely AI, Wellfound AI.
- **Tasks:**
  - Standardize timezone parsing to UTC (`datetime.now(timezone.utc)`).
  - Implement 24-hour cutoff gate: `(now - published_at) <= timedelta(hours=24)`.
  - Extract full-text content for news articles where permitted.
  - Classify jobs into role families (`RESEARCH`, `ENGINEERING`, `PRODUCT`, `OPERATIONS`, `SALES`, `OTHER`).
  - Flag remote eligibility (`is_remote: bool`).

### Phase 5: LLM Extraction & Provider Failover Integration
- **Objective:** Extract structured records from complex unstructured HTML snippets with high reliability.
- **Tasks:**
  - Complete live API client connections for Gemini Flash (`google-genai`), Groq Llama, and DeepSeek.
  - Implement HTTP 429 exponential backoff with randomized jitter.
  - Implement HTTP 413 dynamic chunking and token window reduction.
  - Add source-grounding validator to verify extracted attributes against raw source text.

### Phase 6: Entity Resolution & Audit Logging
- **Objective:** Ensure consistent canonical naming across startups, products, and jobs.
- **Tasks:**
  - Route all extracted organization names through `EntityResolver`.
  - Populate `EntityResolutionLog` table and export array.
  - Verify ambiguity thresholds prevent false-positive merges.

### Phase 7: Storage Persistence & Database Upsert Logic
- **Objective:** Store validated records in PostgreSQL/SQLite with idempotent upserts.
- **Tasks:**
  - Implement async SQLAlchemy repository pattern.
  - Execute PostgreSQL `ON CONFLICT (url) DO UPDATE` or `DO NOTHING`.
  - Create database indexes on `canonical_name`, `published_date`, and `collected_at`.

### Phase 8: Workbook & Spreadsheet Publishing
- **Objective:** Generate customer-facing deliverables.
- **Tasks:**
  - Execute `ExcelExporter` to generate formatted 6-tab `.xlsx` workbook.
  - Generate category CSV files in `data/exports/`.
  - Implement Google Sheets API batch update logic for real-time dashboard syncing.

### Phase 9: End-to-End Orchestration & Quality Assurance
- **Objective:** Validate complete pipeline execution and error handling.
- **Tasks:**
  - Execute full CLI pipeline with `--limit` options.
  - Verify zero unhandled exceptions on network drops or rate limits.
  - Confirm all mandatory targets are reached with 100% source traceability.
