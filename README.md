# AI Signal Intelligence Engine

Production-grade asynchronous data ingestion, entity resolution, and intelligence pipeline for the global Artificial Intelligence industry.

Built as an engineering assessment for **AI Signal**.

---

## Key Features

- **Five Intelligence Categories:**
  - **AI Startups:** Name, website, verified employee count, description.
  - **AI Products:** Name, startup association, normalized pricing (`FREE`, `FREEMIUM`, `PAID`, `ENTERPRISE`).
  - **AI Research Papers:** Arxiv integration, author metadata, verified GitHub star metrics.
  - **AI Jobs:** Strict 24-hour temporal filtering across 5 distinct job boards with role family classification.
  - **AI News:** Strict 24-hour temporal filtering across 5 premier technology publications with full-text preservation.
- **Resilient Multi-Provider LLM Engine:**
  - Provider failover chain: **Gemini Flash** (primary) $\rightarrow$ **Groq Llama** (fallback) $\rightarrow$ **DeepSeek** (secondary fallback).
  - Exponential backoff with randomized jitter on HTTP 429 rate limits.
  - Intelligent document chunking on HTTP 413 (Payload Too Large).
  - Grounding verification against raw source text to prevent hallucinations.
- **Entity Resolution Engine:**
  - Seed database of 50 prominent AI startups.
  - Deterministic string normalization (stripping corporate suffixes and web domains).
  - RapidFuzz similarity scoring ($\ge 88\%$ confidence threshold).
  - Ambiguity rejection guard to prevent false merges.
  - Complete, traceable `EntityResolutionLog` export.
- **Production Data Delivery:**
  - Automated 6-tab Excel workbook (`Startups`, `Products`, `Research Papers`, `Jobs`, `News`, `Entity Mapping Log`).
  - Standalone CSV exports per category.
  - Google Sheets API cloud sync architecture.
- **High Scalability Architecture:**
  - Single-node async design targeting 5,000+ records.
  - Distributed scaling blueprint (Redis, Celery/Temporal, PostgreSQL partitioning) targeting 500,000+ records.

---

## Project Structure

```
ai-signal-intelligence/
│
├── src/
│   ├── collectors/
│   │   ├── base.py                   # Standardized BaseCollector interface & telemetry
│   │   ├── startups/                 # AI Startup collector & parsers
│   │   ├── products/                 # AI Product collector & pricing normalization
│   │   ├── research/                 # Arxiv collector & GitHub REST API star fetcher
│   │   ├── news/                     # 5x News feeds with 24h temporal filter
│   │   └── jobs/                     # 5x Job boards with 24h temporal filter
│   │
│   ├── llm/
│   │   ├── base.py                   # Provider-independent LLM interface & DTOs
│   │   ├── providers.py              # Gemini, Groq, DeepSeek & Mock implementations
│   │   └── client.py                 # Resilient fallback client with backoff & chunking
│   │
│   ├── entity_resolution/
│   │   ├── seeds.py                  # Seed database of 50 prominent AI startups
│   │   └── resolver.py               # Deterministic + RapidFuzz entity resolver
│   │
│   ├── validation/
│   │   └── schemas.py                # Strict Pydantic v2 domain schemas & export adapters
│   │
│   ├── storage/
│   │   ├── database.py               # Async SQLAlchemy engine & session factory
│   │   └── models.py                 # Relational tables for PostgreSQL & SQLite
│   │
│   ├── exporters/
│   │   ├── excel.py                  # OpenPyXL 6-tab formatted workbook exporter
│   │   ├── csv_exporter.py           # Per-category CSV exporter
│   │   └── sheets.py                 # Google Sheets API publisher
│   │
│   ├── utils/
│   │   ├── config.py                 # Pydantic Settings & environment manager
│   │   ├── logging.py                # Structured console & JSON logger
│   │   ├── rate_limiter.py           # Token bucket rate limiter with jitter
│   │   └── http_client.py            # Resilient aiohttp client session
│   │
│   └── main.py                       # CLI application entrypoint
│
├── tests/
│   ├── test_schemas.py               # Pydantic schema validation tests
│   ├── test_entity_resolution.py     # Deterministic & RapidFuzz resolution tests
│   ├── test_llm_interface.py         # LLM failover, chunking & grounding tests
│   └── test_config.py                # Configuration loading tests
│
├── data/
│   ├── raw/                          # Raw payload artifacts
│   ├── processed/                    # Normalized datasets
│   └── exports/                      # Generated Excel and CSV workbooks
│
├── logs/                             # Application runtime logs
├── docs/
│   └── roadmap.md                    # Phased technical implementation roadmap
│
├── .env.example                      # Template configuration file
├── .gitignore                        # Git exclusion rules
├── requirements.txt                  # Production dependencies
├── pytest.ini                        # Pytest configuration
├── architecture.md                   # Comprehensive system architecture document
└── README.md                         # Project documentation
```

---

## Getting Started

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Installation
Clone the repository and install dependencies:
```bash
# Clone repository
git clone <repo-url>
cd "AI Signal Intelligence"

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and configure your API keys:
```bash
copy .env.example .env   # Windows
# or
cp .env.example .env     # Linux/macOS
```

Key environment variables:
- `GEMINI_API_KEY`: Google Gemini API key (Primary LLM extraction).
- `GROQ_API_KEY`: Groq API key (Fallback 1).
- `DEEPSEEK_API_KEY`: DeepSeek API key (Fallback 2).
- `GITHUB_TOKEN`: GitHub Personal Access Token for verified star metrics.
- `DATABASE_URL`: Database connection string (`sqlite+aiosqlite:///data/ai_signal.db` for dev).

### 4. Running the Pipeline
Run the dry-run command to verify configuration and initialization:
```bash
python -m src.main --dry-run
```

Run pipeline and generate the initial 6-tab Excel workbook:
```bash
python -m src.main
```

### 5. Executing Data Collectors Individually
```bash
# AI Startups (1,000 verified records)
python -m src.collectors.startups.collector --limit 1000

# AI Products (1,000 verified records)
python -m src.collectors.products.collector --limit 1000

# AI Research Papers (1,000 verified papers with GitHub metrics)
python -m src.collectors.research.collector --limit 1000

# AI News (Articles within preceding 24 hours across 5 news feeds)
python -m src.collectors.news.collector

# AI Jobs (Job listings within preceding 24 hours across 5 job boards)
python -m src.collectors.jobs.collector
```

### 6. Running the Test Suite
Execute the 47-test suite:
```bash
pytest -v
```

---

## Known Limitations & Integrity Governance

1. **Strict 24-Hour Temporal Window:** The news and job collectors strictly filter for records published within the preceding 24 hours. If an external job board or news feed published no new postings in that exact 24-hour window, zero records are recorded. Missing records are never synthetically generated.
2. **Directory Self-Reporting:** Startup metadata originates from the Y Combinator directory and foundational seed registries. While authentic, corporate changes such as unannounced acquisitions or private funding rounds may lag.
3. **No Fabricated Financials:** Valuation metrics, private cap tables, and unverified funding stages without an authoritative directory source are retained as `null` (`UNAVAILABLE`) to preserve zero hallucination guarantees.

