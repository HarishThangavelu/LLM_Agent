🚀 Agentic Job Intelligence Pipeline
📌 Introduction

This project builds a local agentic AI pipeline for intelligent job discovery, ranking, and decision support.

Instead of manually searching job portals daily, the system:

crawls job portals automatically

filters relevant engineering roles

extracts job descriptions

semantically matches them with the candidate’s resume

ranks opportunities using an ATS-style similarity score

produces structured shortlists for efficient manual applications

The system is designed as a real data ingestion + reasoning pipeline, not a static ML demo.

❗ Problem Statement

Modern job search — especially in AI / Software / Data roles — is:

repetitive and time-consuming

noisy with irrelevant listings

difficult to track systematically

inefficient in prioritizing high-fit opportunities

Manual filtering results in:

missed opportunities

cognitive overload

inconsistent application strategy

There is a need for a continuous intelligent monitoring system that:

discovers new roles

evaluates relevance automatically

reduces manual screening effort

✅ Solution Overview

This project implements a multi-stage agent pipeline:

Crawl job portals (StepStone Germany)

Extract structured job metadata

Fetch and cache Job Descriptions (JD)

Compute semantic similarity with resume using local embedding model

Maintain incremental job database

Generate priority ranking for application decision

🧠 System Architecture
High Level Flow
Job Portal (StepStone)
        ↓
Playwright Scraper (Pagination + Anti-bot Safe)
        ↓
Structured Job Storage (CSV Master Table)
        ↓
JD Fetch + Local Cache
        ↓
Embedding Engine (Ollama local model)
        ↓
ATS Similarity Scoring
        ↓
Ranked Application Shortlist
🔧 Core Engineering Components
1️⃣ Scraping Layer — Playwright Crawler (V4)

Responsibilities:

browser-level scraping to bypass throttling

lazy-loading scroll handling

pagination depth control

relevance filtering using skill keywords

freshness filtering (≤3 days old listings)

retry navigation logic for HTTP2 failures

portal-safe random crawl pacing

Why Playwright (not requests):

Approach	Issue
Requests + BS4	blocked / incomplete DOM
Static scraping	misses dynamic listings
API access	unavailable
Playwright	✅ full rendering + resilient
2️⃣ Job Storage Layer

Maintains:

outputs/master_jobs.csv

Columns:

title

job link

posted date

ats_score

priority

status

Features:

duplicate removal using job link

incremental update (only new jobs appended)

persistent ranking history

3️⃣ JD Fetch + Cache Layer

Design decision:

❗ Do NOT store full JD in CSV.

Instead:

data/jd_cache/<hash>.txt

Benefits:

cleaner structured dataset

faster ATS reruns

avoids repeated network calls

enables offline embedding scoring

4️⃣ ATS Scoring Engine (Local LLM Embeddings)

Model:

Ollama → nomic-embed-text

Pipeline:

embed resume once (cached vector)

embed JD text (truncated for stability)

compute cosine similarity

assign priority band:

ATS Score	Priority
≥85	HIGH
70–85	MEDIUM
<70	LOW

Engineering considerations:

retry logic for embedding failures

worker throttling (5–9 sec delay)

incremental scoring (only pending rows processed)

crash-safe CSV persistence

5️⃣ Runner Orchestration Layer

run.py coordinates:

query generation (role + skill combinations)

controlled crawl batch execution

storage update

conditional ATS execution (skip if no new work)

This mimics real workflow engine behaviour.

🎯 Query Strategy

Search pattern:

werkstudent-<skill>
praktikum-<skill>
abschlussarbeit-<skill>

Skills sourced dynamically from:

data/resume.txt

Example:

machine learning

python

data engineer

computer vision

automation

This allows resume-driven job discovery.

⚙ Infrastructure Design

Optimized for low-resource local execution:

Component	Stack
Scraper	Playwright (headless Chromium)
Embedding	Ollama local inference
Pipeline	Python
Data storage	CSV + text cache
Environment	WSL Ubuntu

Advantages:

no cloud cost

reproducible experiments

offline scoring capability

📈 Current Capabilities

resilient browser crawler

pagination with crawl stop logic

incremental job database

local semantic ranking

cache-aware ATS worker

crash-resumable scoring

portal-safe ingestion pacing

🚧 Limitations

sequential crawl scheduling

CSV storage scalability limits

JD fetch still HTTP-based (Playwright fallback planned)

no dashboard visualization yet

no automated application submission

🔮 Roadmap

Planned upgrades:

multi-query async crawl scheduler

SQLite job queue

vector database integration

job trend analytics dashboard

automated shortlist export

multi-portal ingestion (Indeed / Xing)

agentic notification system

full autonomous job intelligence loop

Long-term vision:

Build a startup-grade agent platform capable of:

opportunity discovery

industrial market intelligence

automated research pipelines

AI-assisted outreach workflows

