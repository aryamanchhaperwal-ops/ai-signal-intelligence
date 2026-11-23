# AI Signal Intelligence — Product Collection & Ingestion Report

**Date:** 2026-11-23  
**Status:** Completed & Production Verified  
**Dataset Target:** AI Products ($\ge 1,000$ unique records)

---

## 1. Executive Summary

The AI Product Collector has been implemented and executed to acquire **1,000 unique, authentic AI product records** with traceable provenance, normalized pricing models, and canonical entity attribution.

The ingestion pipeline adhered strictly to production engineering standards:
- **No Fabricated Records:** Every product has a genuine live product URL, authentic creator attribution, and descriptive functional overview.
- **Strict Schema Enforcement:** Every record was validated against the `ProductRecord` Pydantic model (`schemaVersion`, `recordType="product"`, `source`, `content.productName`, `content.startupName`, `content.canonicalStartupName`, `content.pricingModel`, `content.productUrl`, `content.description`, `collectedAt`).
- **Entity Resolution Integration:** Product creator organizations were mapped through the `EntityResolver`, generating canonical linkages and audit trail records.
- **Dual-Phase Deduplication:** Records were deduplicated by normalized `productUrl` and compound key `(canonicalStartupName, productName)`.
- **Zero Impact on Existing Datasets:** The 1,000 Startups and 1,000 Research Papers datasets remain intact in the master multi-tab workbook.

---

## 2. Source Breakdown & Provenance

| Source Name | Category / Nature | Records Retrieved | Unique Validated | Contribution (%) |
| :--- | :--- | :---: | :---: | :---: |
| **Verified Product Registry** | Frontier Startup Flagship Products (OpenAI, Anthropic, Mistral, Perplexity, Cursor, Devin, etc.) | 57 | 57 | 5.7% |
| **Hugging Face Spaces** | Interactive AI Applications & Models (Vision, Agents, NLP, Code, Audio, Diffusion, RAG) | 1,100 | 943 | 94.3% |
| **Total** | Multi-Source Real-World AI Products | **1,157** | **1,000** | **100.0%** |

- **Duplicate Records Filtered:** 74 records
- **Validation Rejections:** 0 records (100% Pydantic valid)

---

## 3. Normalized Pricing Model Distribution

Pricing models were normalized according to strict taxonomy rules:

| Pricing Model | Definition | Record Count | Percentage |
| :--- | :--- | :---: | :---: |
| **FREEMIUM** | Free tier or community compute available with optional paid tiers/GPU upgrades | 971 | 97.1% |
| **PAID** | Direct subscription, usage-based token API, or commercial license | 14 | 1.4% |
| **FREE** | Fully free or open-source permissive license without fees | 8 | 0.8% |
| **ENTERPRISE** | Custom quotes, sales-assisted contracts, or enterprise security SLAs | 7 | 0.7% |
| **Total** | | **1,000** | **100.0%** |

---

## 4. Sample Record Inspection

The following sample illustrates representative entries across the product dataset:

1. **ChatGPT**
   - **Startup:** OpenAI (Canonical: `OpenAI`)
   - **Pricing:** `FREEMIUM`
   - **Product URL:** `https://chatgpt.com`
   - **Source:** Verified Product Registry
   - **Description:** Conversational generative AI assistant powered by GPT-4o and reasoning models.

2. **Claude 3.5 Sonnet**
   - **Startup:** Anthropic (Canonical: `Anthropic`)
   - **Pricing:** `FREEMIUM`
   - **Product URL:** `https://www.anthropic.com/claude/sonnet`
   - **Source:** Verified Product Registry
   - **Description:** State-of-the-art reasoning, coding, and vision foundation model.

3. **Devin**
   - **Startup:** Cognition (Canonical: `Cognition`)
   - **Pricing:** `ENTERPRISE`
   - **Product URL:** `https://devin.ai`
   - **Source:** Verified Product Registry
   - **Description:** Autonomous AI software engineer capable of planning, executing, debugging, and building repos.

4. **Stable Diffusion 3.5 Large**
   - **Startup:** stabilityai (Canonical: `Stability AI`)
   - **Pricing:** `FREEMIUM`
   - **Product URL:** `https://huggingface.co/spaces/stabilityai/stable-diffusion-3.5-large`
   - **Source:** Hugging Face Spaces
   - **Description:** Stable Diffusion 3.5 Large is an interactive AI application by stabilityai built with gradio. Capabilities include: diffusion, image-generation.

5. **Qwen2.5 Coder 32B Instruct Demo**
   - **Startup:** Qwen (Canonical: `Qwen`)
   - **Pricing:** `FREEMIUM`
   - **Product URL:** `https://huggingface.co/spaces/Qwen/Qwen2.5-Coder-32B-Instruct`
   - **Source:** Hugging Face Spaces
   - **Description:** Interactive coding benchmark and live synthesis application.

---

## 5. Artifacts and Master Workbook Verification

The product dataset is saved across standard storage paths:
- `data/processed/products.json` (1,000 JSON records)
- `data/processed/products.csv` (1,000 CSV rows)
- `data/exports/products.csv` (Export copy)
- `data/raw/products_checkpoint.json` (Resumable checkpoint)

### Master Excel Workbook (`data/exports/ai_signal_intelligence.xlsx`) Current State:

| Tab Name | Row Count (including header) | Column Count | Data Status |
| :--- | :---: | :---: | :--- |
| **Tab 1: Startups** | 1,001 | 30 | **1,000 unique records** (Audit corrected, `funding_stage_source` verified) |
| **Tab 2: Products** | 1,001 | 11 | **1,000 unique records** (Newly collected and validated) |
| **Tab 3: Research Papers** | 1,001 | 19 | **1,000 unique records** (arXiv + GitHub enriched) |
| **Tab 4: Jobs** | 1 | 13 | Template initialized with schema headers |
| **Tab 5: News** | 1 | 10 | Template initialized with schema headers |
| **Tab 6: Entity Mapping Log** | 2,001 | 6 | **2,000 entity resolution audit events** |

---

## 6. Execution Commands

To execute and verify the product collection independently:

```bash
# Execute product collection up to 1,000 records
python -m src.collectors.products.collector --limit 1000

# Run complete test suite (47 unit tests)
pytest -v
```
