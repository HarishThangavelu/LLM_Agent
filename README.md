# 🤖 Agentic Job Intelligence Pipeline

**A local AI-powered pipeline that automatically discovers, filters, and semantically ranks job opportunities against your resume — running 100% locally, zero cloud cost.**

> Built by [Harish Thangavelu](https://github.com/HarishThangavelu) · MSc Student @ FAU Erlangen-Nürnberg  
> 🔍 Actively seeking Werkstudent / Internship roles in AI & Data Engineering in Bavaria

---

## 🧠 What This Is

Instead of manually scanning job portals every day, this system does it for you:

- Crawls job portals automatically using browser-level scraping
- Filters listings by role type, freshness, and keyword relevance
- Fetches and caches full job descriptions
- Computes semantic similarity between your resume and each JD using a **local embedding model**
- Ranks every opportunity with an ATS-style priority score

This is a real data ingestion + reasoning pipeline — not a toy demo.

---

## 🔧 System Architecture

```
Job Portal (StepStone)
        ↓
Playwright Scraper  ←  pagination + anti-bot safe
        ↓
Relevance Filter    ←  role type · freshness · keywords
        ↓
JD Fetch + Hash Cache
        ↓
Embedding Engine    ←  Ollama · nomic-embed-text (local)
        ↓
ATS Similarity Scoring
        ↓
Ranked Shortlist    →  25–30 relevant roles per run
```

---

## ⚙️ Core Components

### 1 · Playwright Scraper
Browser-level scraping to handle dynamic portals that block static HTTP scrapers.

| Approach | Problem |
|---|---|
| `requests` + BeautifulSoup | Blocked / incomplete DOM |
| Static scraping | Misses dynamically loaded listings |
| **Playwright ✅** | Full DOM rendering + resilient pagination |

Features: lazy-load scroll handling · pagination depth control · retry logic for HTTP2 errors · randomized crawl pacing · freshness filter (≤ 3 days)

### 2 · Relevance Filter
Early-stage filtering at ingestion — before any heavy processing:
- Role type: Werkstudent / Praktikum / Abschlussarbeit
- Posting age: last 3 days only
- Keyword match: skills sourced dynamically from `data/resume.txt`

### 3 · Hash-Based JD Cache
Each job description is stored as a hashed `.txt` file. The master dataset holds only metadata + link.

```
data/jd_cache/<hash>.txt   ← raw JD text
outputs/master_jobs.csv    ← metadata index
```

Benefits: faster reruns · no repeated network calls · offline embedding support · clean structured dataset

### 4 · ATS Scoring Engine (Local LLM Embeddings)

Model: **Ollama → `nomic-embed-text`** (runs fully locally)

| ATS Score | Priority |
|---|---|
| ≥ 85 | 🔴 HIGH |
| 70 – 85 | 🟡 MEDIUM |
| < 70 | 🟢 LOW |

Pipeline:
1. Embed resume once → cached vector
2. Embed each JD (truncated for stability)
3. Compute cosine similarity
4. Assign priority band
5. Persist incrementally (crash-safe)

### 5 · Runner Orchestration (`run.py`)
Coordinates the full pipeline: query generation → crawl batches → storage update → conditional ATS scoring (skips if no new work). Mimics a real workflow engine.

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Scraping | Python · Playwright (headless Chromium) |
| Embeddings | Ollama · `nomic-embed-text` |
| Similarity | Cosine similarity · NLP |
| Storage | CSV + text cache (SQLite planned) |
| Environment | WSL Ubuntu · Python |
| Orchestration | Custom agentic pipeline (`run.py`) |

---

## 📈 Current Capabilities

- Resilient browser crawler with pagination
- Incremental job database (no full reruns)
- Local semantic ranking — private, no API cost
- Cache-aware ATS worker
- Crash-resumable incremental scoring
- ~25–30 relevant roles discovered per run

---

## 🚀 Getting Started

### Prerequisites

```bash
# Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Install and start Ollama
# https://ollama.com
ollama pull nomic-embed-text
```

### Run

```bash
python run.py
```

Results are written to `outputs/master_jobs.csv` with ATS scores and priority bands.

---

## 🗂️ Project Structure

```
LLM_Agent/
├── run.py                  # Main orchestration entry point
├── scraper/                # Playwright scraping layer
├── pipeline/               # ATS scoring + embedding engine
├── data/
│   ├── resume.txt          # Your resume (used for embedding)
│   └── jd_cache/           # Cached job description text files
├── outputs/
│   └── master_jobs.csv     # Ranked job database
├── requirements.txt
└── README.md
```

---

## ⚠️ Limitations

- Sequential crawling (async scheduler in progress)
- CSV storage has scale limits (SQLite migration planned)
- No dashboard visualization yet
- No automated application submission (by design — human applies manually)

---

## 🔮 Roadmap

- [ ] Async multi-query crawl scheduler
- [ ] SQLite job queue replacing CSV
- [ ] Vector database integration
- [ ] Streamlit opportunity dashboard
- [ ] Multi-portal support: Indeed · Xing
- [ ] Agentic notification system
- [ ] Automated shortlist export

---

## 💡 Design Philosophy

> Real AI systems are not just models — they are data ingestion reliability, workflow orchestration, and decision usability.

This project focuses on engineering robustness before feature expansion. Every component is designed to be incremental, crash-safe, and runnable on a local machine without cloud dependencies.

---

## 📬 Contact

**Harish Thangavelu**  
MSc Electromobility & AI Systems · FAU Erlangen-Nürnberg  
Open to Werkstudent / Internship roles in Bavaria — AI Engineering · Data Engineering · ML Systems

[GitHub](https://github.com/HarishThangavelu) · [LinkedIn](https://linkedin.com/in/YOUR_HANDLE)