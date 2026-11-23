"""Generate a professional, strictly 3-page Architecture PDF using Playwright."""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import pypdf

HTML_CONTENT = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {
    size: A4 portrait;
    margin: 12mm 15mm 12mm 15mm;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    line-height: 1.35;
    font-size: 9pt;
    margin: 0;
    padding: 0;
  }
  .page-break {
    page-break-after: always;
  }
  h1 {
    font-size: 16pt;
    color: #0f172a;
    margin: 0 0 4px 0;
    border-bottom: 2px solid #2563eb;
    padding-bottom: 4px;
  }
  h2 {
    font-size: 11.5pt;
    color: #1e40af;
    margin: 10px 0 4px 0;
    border-bottom: 1px solid #cbd5e1;
    padding-bottom: 2px;
  }
  h3 {
    font-size: 9.5pt;
    color: #0f172a;
    margin: 6px 0 2px 0;
  }
  p {
    margin: 3px 0;
  }
  ul, ol {
    margin: 3px 0;
    padding-left: 18px;
  }
  li {
    margin-bottom: 2px;
  }
  .header-meta {
    font-size: 8pt;
    color: #64748b;
    margin-bottom: 8px;
  }
  .badge {
    background: #e0e7ff;
    color: #3730a3;
    padding: 1px 5px;
    border-radius: 3px;
    font-weight: 600;
    font-size: 7.5pt;
  }
  .grid {
    display: flex;
    gap: 10px;
    margin: 6px 0;
  }
  .col {
    flex: 1;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 6px 8px;
  }
  .col h4 {
    margin: 0 0 4px 0;
    font-size: 8.5pt;
    color: #1e3a8a;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 8pt;
    margin: 6px 0;
  }
  th, td {
    border: 1px solid #cbd5e1;
    padding: 4px 6px;
    text-align: left;
  }
  th {
    background: #f1f5f9;
    color: #0f172a;
    font-weight: 600;
  }
  code {
    font-family: Consolas, monospace;
    background: #f1f5f9;
    padding: 1px 3px;
    border-radius: 2px;
    font-size: 8pt;
  }
  .footer {
    position: absolute;
    bottom: 0;
    width: 100%;
    font-size: 7.5pt;
    color: #94a3b8;
    text-align: right;
  }
</style>
</head>
<body>

<!-- PAGE 1 -->
<div class="page-break" style="position: relative; min-height: 270mm;">
  <h1>AI Signal Intelligence Engine — System Architecture</h1>
  <div class="header-meta">
    <strong>Author:</strong> AI Signal Technical Lead & Systems Architect &nbsp;|&nbsp;
    <strong>Document Version:</strong> 1.0.0 &nbsp;|&nbsp;
    <strong>Target Scale:</strong> 1,000 to 500,000+ Records
  </div>

  <h2>1. Executive Summary & Design Philosophy</h2>
  <p>The <strong>AI Signal Intelligence Engine</strong> is a modular, production-oriented asynchronous data pipeline architected to continuously collect, normalize, resolve, and publish verified intelligence regarding the global Artificial Intelligence industry.</p>
  <ul>
    <li><strong>Zero Fabrication / Absolute Provenance:</strong> No entity, metric, or URL is ever synthetically created. Every record preserves traceable source metadata and timestamps.</li>
    <li><strong>Resilient Ingestion:</strong> Built with <code>aiohttp</code>, concurrency semaphores (limit=10), token-bucket rate limiting with jitter, and Windows SSL certificate management via <code>certifi</code>.</li>
    <li><strong>Strict Validation & Typing:</strong> All entities adhere to immutable Pydantic v2 schemas enforcing strict typing, semantic nulls, and schema versioning.</li>
  </ul>

  <h2>2. Five Intelligence Streams</h2>
  <div class="grid">
    <div class="col">
      <h4>1. AI Startups (1,000 Verified)</h4>
      <p>Sourced from Y Combinator Algolia backend & 50 foundational seed startups. Tracks name, domain, description, team size, headquarters, and verified funding stage provenance.</p>
    </div>
    <div class="col">
      <h4>2. AI Products (1,000 Verified)</h4>
      <p>Sourced from Hugging Face Spaces & verified frontier registry. Normalizes pricing models into <code>FREE</code>, <code>FREEMIUM</code>, <code>PAID</code>, and <code>ENTERPRISE</code> with canonical startup attribution.</p>
    </div>
  </div>
  <div class="grid">
    <div class="col">
      <h4>3. AI Research Papers (1,000 Verified)</h4>
      <p>Ingested via official arXiv API across AI, CV, CL, and RO categories. Enriched with real-time GitHub repository star and fork metrics via GitHub REST API.</p>
    </div>
    <div class="col">
      <h4>4 & 5. AI Jobs & News (24h Window)</h4>
      <p>Monitors 5 job boards and 5 technology news feeds with strict 24-hour temporal filtering, <code>RoleFamily</code> taxonomy classification, and zero synthetic fill.</p>
    </div>
  </div>

  <h2>3. High-Level Ingestion Architecture</h2>
  <table>
    <tr>
      <th>Layer</th>
      <th>Core Components</th>
      <th>Key Responsibilities</th>
    </tr>
    <tr>
      <td><strong>Collection</strong></td>
      <td><code>ResilientHttpClient</code>, <code>AsyncRateLimiter</code></td>
      <td>Async HTTP connection pooling, token bucket throttling, polite jitter (100–300ms), and 429 retry loops.</td>
    </tr>
    <tr>
      <td><strong>Transformation</strong></td>
      <td>Category Collectors (<code>startups</code>, <code>products</code>, etc.)</td>
      <td>Domain normalization, feed parsing, category tagging, deduplication by compound keys.</td>
    </tr>
    <tr>
      <td><strong>Resolution</strong></td>
      <td><code>EntityResolver</code> (RapidFuzz + Seed DB)</td>
      <td>Canonical company mapping, legal suffix stripping, ambiguity margin safeguards, audit log export.</td>
    </tr>
    <tr>
      <td><strong>Storage & Output</strong></td>
      <td><code>ExcelExporter</code>, <code>PostgreSQL / SQLite</code></td>
      <td>6-tab formatted workbook generation, relational schema persistence, CSV data warehouse mirroring.</td>
    </tr>
  </table>

  <div class="footer">Page 1 of 3 — AI Signal Intelligence Engine Architecture</div>
</div>

<!-- PAGE 2 -->
<div class="page-break" style="position: relative; min-height: 270mm;">
  <h1>Resilient LLM Hierarchy & Entity Resolution</h1>
  <div class="header-meta">Fault Tolerance, Fallback Routing, and Entity Disambiguation Engine</div>

  <h2>4. Multi-Provider Resilient LLM Architecture</h2>
  <p>To guard against provider outages, sudden rate limits (HTTP 429), and context window limits (HTTP 413), LLM extraction is abstracted across a resilient fallback chain:</p>
  
  <div class="grid">
    <div class="col">
      <h4>Primary: Gemini Flash</h4>
      <p>High-throughput structured output provider for real-time document transformation and attribute extraction.</p>
    </div>
    <div class="col">
      <h4>Fallback 1: Groq Llama</h4>
      <p>Activated automatically upon Gemini rate limiting or service unavailability. Fast inference via LPU hardware.</p>
    </div>
    <div class="col">
      <h4>Fallback 2: DeepSeek</h4>
      <p>Secondary failover for deep semantic extraction and reasoning when prior tiers exhaust retry budgets.</p>
    </div>
  </div>

  <h3>Key LLM Guardrails:</h3>
  <ul>
    <li><strong>HTTP 429 Rate Limit Handling:</strong> Exponential backoff with randomized jitter (1.5x factor + uniform jitter) across up to 3 retries per provider before failing over.</li>
    <li><strong>HTTP 413 Payload Chunking:</strong> When document size exceeds model context or returns 413, <code>chunk_text()</code> partitions text at paragraph boundaries and dynamically halves chunk sizes.</li>
    <li><strong>Anti-Hallucination Grounding Guard:</strong> <code>validate_grounding()</code> performs case-insensitive substring verification against raw source text. Critical entities not present in source text are rejected.</li>
  </ul>

  <h2>5. Entity Resolution & Canonical Mapping Engine</h2>
  <p>The <code>EntityResolver</code> prevents entity duplication across fragmented sources using a hybrid deterministic and fuzzy matching architecture:</p>
  <table>
    <tr>
      <th>Stage</th>
      <th>Mechanism</th>
      <th>Action & Confidence Threshold</th>
    </tr>
    <tr>
      <td><strong>1. Deterministic Normalization</strong></td>
      <td>Regex URL stripping & legal suffix removal</td>
      <td>Removes <code>https://</code>, <code>www</code>, TLDs, and suffixes (<code>Inc</code>, <code>LLC</code>, <code>Corp</code>, <code>GmbH</code>, <code>PBC</code>).</td>
    </tr>
    <tr>
      <td><strong>2. Exact Canonical Index</strong></td>
      <td>Seed database dictionary lookup</td>
      <td>Direct match against 50 foundational AI startups and verified aliases (Confidence = 100.0%).</td>
    </tr>
    <tr>
      <td><strong>3. Fuzzy Similarity Scoring</strong></td>
      <td>RapidFuzz Token Set Ratio</td>
      <td>Evaluates normalized tokens. Matches accepted if similarity score $\ge 88.0\%$.</td>
    </tr>
    <tr>
      <td><strong>4. Ambiguity Safeguard</strong></td>
      <td>Score Delta Threshold (margin &lt; 6.0%)</td>
      <td>If top two match scores are within 6.0% delta, entity is flagged as ambiguous to avoid false merges.</td>
    </tr>
  </table>
  <p>Every resolution generates an <code>EntityResolutionLog</code> record containing raw name, canonical name, match method, confidence score, and resolution timestamp, exported directly to Tab 6 of the master workbook.</p>

  <div class="footer">Page 2 of 3 — AI Signal Intelligence Engine Architecture</div>
</div>

<!-- PAGE 3 -->
<div class="page-break" style="position: relative; min-height: 270mm;">
  <h1>Storage Models, Scalability & Production Delivery</h1>
  <div class="header-meta">Data Model Persistence, 500,000+ Record Scaling Blueprint & Delivery</div>

  <h2>6. Relational Storage Schema (PostgreSQL / SQLite)</h2>
  <p>The storage tier uses SQLAlchemy 2.0 declarative models supporting async sessions via <code>aiosqlite</code> and <code>psycopg</code>:</p>
  <ul>
    <li><code>StartupDB</code>: Primary key, <code>startup_id</code> (unique), <code>canonical_name</code> (indexed), verified employee count, official website, funding stage, funding stage source, and verification status.</li>
    <li><code>ProductDB</code>: Product name, canonical startup name, normalized pricing enum, direct product URL, and description.</li>
    <li><code>ResearchPaperDB</code>: arXiv accession ID, paper URL (unique), primary category, GitHub repository URL, stars, and forks.</li>
    <li><code>JobDB</code> & <code>NewsDB</code>: Relational models with published timestamps for temporal index filtering.</li>
  </ul>

  <h2>7. Scaling Blueprint: 1,000 to 500,000+ Records</h2>
  <div class="grid">
    <div class="col">
      <h4>Current Tier: Single-Node Async</h4>
      <ul>
        <li>Python 3.11+ <code>asyncio</code> + <code>aiohttp</code>.</li>
        <li>Memory-efficient streaming & checkpoints.</li>
        <li>Throughput: 10,000+ entities/hour.</li>
        <li>SQLite storage & OpenPyXL exports.</li>
      </ul>
    </div>
    <div class="col">
      <h4>Enterprise Tier: Distributed Cluster</h4>
      <ul>
        <li>Distributed queues: Temporal / Celery + Redis.</li>
        <li>PostgreSQL with range partitioning on <code>collected_at</code>.</li>
        <li>Distributed scraping workers across multi-region proxies.</li>
        <li>S3 / Cloud Storage data lake in Apache Parquet.</li>
      </ul>
    </div>
  </div>

  <h2>8. Quality Verification & Deliverables Summary</h2>
  <table>
    <tr>
      <th>Deliverable Artifact</th>
      <th>Verified Metric / Status</th>
      <th>Integrity Checksum / Compliance</th>
    </tr>
    <tr>
      <td><code>startups.json / .csv</code></td>
      <td>1,000 unique records (950 YC + 50 Seeds)</td>
      <td>SHA-256: <code>cd6c97728697f5be46bbe40395890d263a8440e9d9f5477b1fa7166dc58065ba</code></td>
    </tr>
    <tr>
      <td><code>products.json / .csv</code></td>
      <td>1,000 unique AI products (971 Freemium, 14 Paid, etc.)</td>
      <td>100% Pydantic valid; 0 missing URLs or descriptions.</td>
    </tr>
    <tr>
      <td><code>research_papers.json / .csv</code></td>
      <td>1,000 unique arXiv papers (120 GitHub URLs, 49 stars/forks)</td>
      <td>Zero duplicate arXiv IDs; 100% traceable official URLs.</td>
    </tr>
    <tr>
      <td><code>news.json / .csv</code></td>
      <td>4 authentic articles published within 24h</td>
      <td>TechCrunch, The Verge, Ars Technica, MIT Tech Review.</td>
    </tr>
    <tr>
      <td><code>jobs.json / .csv</code></td>
      <td>0 authentic listings within strict 24h window</td>
      <td>Preserved honestly without synthetic fabrication.</td>
    </tr>
    <tr>
      <td><code>ai_signal_intelligence.xlsx</code></td>
      <td>6-tab Master Excel Workbook</td>
      <td>Tabs: Startups, Products, Research Papers, Jobs, News, Entity Mapping Log.</td>
    </tr>
  </table>

  <div class="footer">Page 3 of 3 — AI Signal Intelligence Engine Architecture</div>
</div>

</body>
</html>
"""

async def generate_pdf():
    pdf_path = Path("docs/architecture.pdf")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.set_content(HTML_CONTENT, wait_until="networkidle")
        await page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
            margin={"top": "0mm", "bottom": "0mm", "left": "0mm", "right": "0mm"}
        )
        await browser.close()
    
    reader = pypdf.PdfReader(str(pdf_path))
    num_pages = len(reader.pages)
    print(f"Generated {pdf_path} with EXACTLY {num_pages} pages.")
    assert num_pages <= 3, f"PDF exceeded 3 pages: got {num_pages}"

if __name__ == "__main__":
    asyncio.run(generate_pdf())
