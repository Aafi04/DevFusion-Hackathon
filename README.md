<div align="center">

# SchemaDoc AI

### Intelligent Data Dictionary Agent

_DevFusion Hackathon — Team Dual Core_

Mohd Aafi (Team Lead) · Girish Mishra

[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Groq](https://img.shields.io/badge/Groq-LLM_API-FF6B35?logo=groq&logoColor=white)](https://groq.com)
[![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-00d084?logo=supabase&logoColor=white)](https://supabase.com)
[![Render](https://img.shields.io/badge/Render-Deployment-46E3B7?logo=render&logoColor=white)](https://render.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)

</div>

---

## Overview

SchemaDoc AI connects to **any SQL database** — SQLite, PostgreSQL, MySQL, or MSSQL — and automatically generates a complete, AI-enriched data dictionary with quality scoring, relationship visualization, natural language querying, and business-ready reports.

The system uses a **cyclic LangGraph state machine** with a deterministic validation gate that catches AI hallucinations, prevents data loss, and self-corrects via retry loops — guaranteeing schema integrity.

**Live deployment:** Frontend on [Vercel](https://schemadoc-frontend.vercel.app) · Backend on [Render](https://schemadoc-backend.onrender.com) · Database on [Supabase](https://supabase.com)

---

## Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│     Extract      │────▶│  AI Enrichment   │────▶│   Validation     │────▶│    Dashboard     │
│  (SQLAlchemy +   │     │  (Groq           │     │   Gate           │     │  (Next.js +      │
│   Profiling)     │     │   Mixtral +      │     │  (Deterministic) │     │   TailwindCSS)   │
│                  │     │   LangChain)     │     │  (Deterministic) │     │   + Caching)     │
└──────────────────┘     └──────────────────┘     └───────┬──────────┘     └──────────────────┘
        │                        ▲                        │
        │                        │  FAILED + retry < 3    │
  Local SQLite or             └────────────────────────┘
  Sample DBs

        │
        ▼ (on success)
  ┌──────────────────┐
  │ Supabase Cache   │
  │  (TTL: 7 days)   │
  └──────────────────┘
```

| Layer                 | Role                                                           | Technology                         |
| --------------------- | -------------------------------------------------------------- | ---------------------------------- |
| **Data Ingestion**    | Dialect-agnostic schema extraction + statistical profiling     | SQLAlchemy 2.0, ThreadPoolExecutor |
| **Orchestration**     | Cyclic state machine with conditional retry edges              | LangGraph StateGraph               |
| **Enrichment Engine** | Semantic analysis with token budgeting & exponential retry     | Groq Mixtral-8x7b + LangChain      |
| **Validation Gate**   | Anti-hallucination guard — column-level integrity verification | Deterministic Python               |
| **Caching Layer**     | Persistent schema cache with TTL + HTTP cache headers          | Supabase PostgreSQL                |
| **Backend API**       | REST API serving pipeline, chat, export, schema + cache        | FastAPI + Uvicorn                  |
| **Frontend**          | Interactive dashboard with 7 pages + HTTP caching              | Next.js 15 + TailwindCSS           |
| **Database**          | Local SQLite + Supabase PostgreSQL cache                       | Supabase + SQLite                  |

---

## Features

| Page                 | Description                                                                                                                           |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Landing Page**     | Animated hero with feature showcase, tech stack badges, and team info                                                                 |
| **Dashboard**        | Run pipelines against cloud databases, animated pipeline visualizer with real-time stage tracking, retry visualization                |
| **Schema Explorer**  | Full table browser with per-column stats, tags (PK/FK/PII/UNIQUE), AI descriptions, sample values, null/unique percentages            |
| **Knowledge Graph**  | Interactive ER diagram — ReactFlow-powered node graph with foreign key edges and table metadata                                       |
| **NL → SQL Chat**    | Natural language to SQL interface grounded in enriched schema context, markdown-rendered responses with syntax-highlighted SQL        |
| **Business Reports** | AI-generated executive overview, domain detection, quality issues, relationship map, per-table documentation, downloadable as MD/JSON |
| **Settings**         | Connection health status, session management, and reset                                                                               |

### Sample Databases (Local + Caching)

Three pre-configured sample databases — generated locally or cached in Supabase:

| Database          | Tables | Rows  | Domain              |
| ----------------- | ------ | ----- | ------------------- |
| **Demo Database** | 3      | ~500  | Sample e-commerce   |
| **Bike Store**    | 5      | ~2.5k | Retail inventory    |
| **Chinook Music** | 4      | ~2k   | Digital music store |

**Caching & Performance:**

- First run: Enrichment via Groq LLM (uses ~15-25k tokens)
- Repeat queries: Served from Supabase cache (7-day TTL, 0 tokens)
- HTTP Cache-Control headers: 1-hour browser cache on all GET endpoints

### Anti-Hallucination Pipeline

- **Deterministic Validation Gate** compares every AI-enriched column set against the raw source of truth
- Detects **data loss** (missing columns) and **hallucinations** (invented columns)
- Automatically retries enrichment up to 3 times on failure
- Full execution trace visible in the animated Pipeline Visualizer

### Performance

- **Batched SQL profiling** — all column stats computed in one query per table (not per-column)
- **Parallel table processing** — ThreadPoolExecutor profiles tables concurrently
- **LLM Token Optimization** — 65-75% reduction via batched calls (enrichment + report), schema compression, and exponential backoff retry
- **Persistent Caching** — Supabase PostgreSQL cache with 7-day TTL, 60-70% cache hit rate on repeat queries
- **HTTP Caching** — Cache-Control headers on GET endpoints (1-hour browser cache)
- **Graceful Degradation** — Supabase optional; in-memory fallback if unavailable

### Production Hardening

- **Centralized Error Handling** — all API errors return consistent `{error, detail, status_code}` JSON via global exception handlers (no raw tracebacks leak to clients)
- **Rate Limiting** — IP-based sliding-window limits via `slowapi`: pipeline runs (5/min), chat (20/min), AI reports (10/min), reads (60/min). Returns structured 429 responses with `Retry-After` headers
- **E2E Test Suite** — 21 automated tests across 4 categories (happy-path, edge-cases, rate limiting, error structure) using `pytest` + `httpx` AsyncClient
- **Cross-Platform UI** — responsive layout with mobile bottom navigation, iOS safe-area support, and adaptive padding

---

## Live Demo

Visit **[schema-doc-ai-hackfest-2-0-ft-turgo.vercel.app](https://schema-doc-ai-hackfest-2-0-ft-turgo.vercel.app)** — select any database from the dropdown and click **Run Pipeline**. No setup required.

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Groq API key](https://console.groq.com) (free tier: 1M tokens/month)
- (Optional) A [Supabase account](https://supabase.com) for persistent caching

### Backend

```bash
# Clone the repository
git clone https://github.com/Aafi04/SchemaDoc-AI-Hackfest-2.0-ft.-Turgon-AI.git
cd SchemaDoc-AI-Hackfest-2.0-ft.-Turgon-AI

# Create and activate virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (from https://console.groq.com)

# Start the backend
uvicorn backend.main:app --reload --port 8001
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard opens at **http://localhost:3000**. The backend API runs at **http://localhost:8001**.

### Local SQLite Databases (Optional)

For offline development with local SQLite files:

```bash
python data/scripts/get_chinook.py     # Chinook (11 tables)
python data/scripts/get_olist.py       # Olist (8 tables, 550k+ rows)
python data/scripts/get_bikestore.py   # Bike Store (9 tables)
python setup_demo.py                   # Small 3-table demo DB
```

> **Caching Layer:** When `SUPABASE_URL` and `SUPABASE_KEY` are set in `.env`, enriched schemas are persisted to Supabase with automatic cleanup. Repeated queries hit the cache instead of calling Groq LLM, reducing tokens and improving response time.

---

## Project Structure

```
├── render.yaml                     # Render deployment config
├── vercel.json                     # Vercel deployment config
├── backend/
│   ├── main.py                     # FastAPI application entry point
│   ├── core/
│   │   ├── config.py               # Settings (Pydantic BaseSettings)
│   │   ├── state.py                # TypedDict state definitions
│   │   ├── exceptions.py           # Centralized error handling & custom exceptions
│   │   ├── rate_limiter.py         # IP-based rate limiting (slowapi)
│   │   └── utils.py                # Shared utilities (DecimalEncoder, etc.)
│   ├── api/routes/
│   │   ├── pipeline.py             # Pipeline execution + database listing
│   │   ├── schema.py               # Schema overview + table detail
│   │   ├── chat.py                 # NL → SQL chat endpoint
│   │   └── export.py               # JSON/MD export + AI business reports
│   ├── connectors/
│   │   └── sql_connector.py        # SQLAlchemy extraction + batched profiling
│   ├── pipeline/
│   │   ├── graph.py                # LangGraph pipeline builder
│   │   └── nodes/
│   │       ├── enrichment_node.py  # Groq Mixtral enrichment + token budgeting
│   │       └── validation_node.py  # Anti-hallucination gate
│   ├── services/
│   │   ├── pipeline_service.py     # Run management + execution
│   │   └── usage_search.py         # Forensic log search (ReAct tool)
│   └── tests/
│       └── test_e2e.py             # 21 E2E tests (pytest + httpx)
├── frontend/
│   ├── src/app/
│   │   ├── page.tsx                # Animated landing page
│   │   └── dashboard/
│   │       ├── page.tsx            # Pipeline runner + visualizer
│   │       ├── schema/page.tsx     # Schema explorer
│   │       ├── graph/page.tsx      # ER knowledge graph
│   │       ├── chat/page.tsx       # NL → SQL chat
│   │       ├── reports/page.tsx    # Business report viewer
│   │       └── settings/page.tsx   # Health check + session reset
│   ├── src/components/
│   │   ├── PipelineVisualizer.tsx  # Animated pipeline stage component
│   │   └── layout/                 # NavRail, TopBar, AppShell, MobileNav
│   └── src/lib/
│       ├── api.ts                  # API client + TypeScript types
│       └── utils.ts                # Utility functions
├── shared/
│   └── schemas.py                  # Pydantic request/response models
└── data/
    ├── scripts/                    # Database download scripts
    └── usage_logs.sql              # Query logs for ReAct tool
```

---

## Tech Stack

| Component              | Technology                               |
| ---------------------- | ---------------------------------------- |
| AI Model               | Groq Mixtral-8x7b-32768 (free tier)      |
| LLM Framework          | LangChain Core + LangChain Groq          |
| Orchestration          | LangGraph (cyclic StateGraph)            |
| Token Optimization     | Batching, compression, exponential retry |
| Database Introspection | SQLAlchemy 2.0 (dialect-agnostic)        |
| Persistent Cache       | Supabase PostgreSQL (7-day TTL)          |
| Cache Headers          | HTTP Cache-Control (1-hour browser)      |
| Backend API            | FastAPI + Uvicorn                        |
| Rate Limiting          | slowapi (IP-based sliding window)        |
| E2E Testing            | pytest + httpx AsyncClient               |
| Frontend               | Next.js 16, TypeScript, TailwindCSS      |
| Animations             | Framer Motion                            |
| Data Fetching          | TanStack React Query                     |
| ER Visualization       | ReactFlow                                |
| Markdown Rendering     | react-markdown + remark-gfm              |
| Backend Hosting        | Render (Python 3 + Uvicorn)              |
| Frontend Hosting       | Vercel (Next.js)                         |
| Database Hosting       | Supabase PostgreSQL                      |

---

## Deployment

The application is **fully deployed and publicly accessible**:

| Service     | Platform | URL                                                                      |
| ----------- | -------- | ------------------------------------------------------------------------ |
| Frontend    | Vercel   | [schemadoc-frontend.vercel.app](https://schemadoc-frontend.vercel.app)   |
| Backend API | Render   | [schemadoc-backend.onrender.com](https://schemadoc-backend.onrender.com) |
| Database    | Supabase | PostgreSQL serverless (cache + metadata)                                 |

### Self-Hosting

<details>
<summary>Deploy your own instance</summary>

#### Backend → Render

1. [render.com](https://render.com) → New Web Service → Deploy from GitHub
2. **Runtime:** Python 3
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port 8000`
5. Add env vars:
   - `LLM_PROVIDER=groq`
   - `GROQ_API_KEY` (from [console.groq.com](https://console.groq.com))
   - `SUPABASE_URL` + `SUPABASE_KEY` (optional, for persistent caching)
   - `CORS_ORIGINS` = your Vercel frontend URL

#### Frontend → Vercel

1. [vercel.com](https://vercel.com) → Add New Project → Import repo
2. Set **Root Directory** to `frontend`
3. Add env var: `NEXT_PUBLIC_API_URL` = your Render backend URL

#### Database → Supabase (Optional)

1. Create project at [supabase.com](https://supabase.com)
2. Run migration SQL: `backend/migrations/001_create_cache_tables.sql`
3. Set `SUPABASE_URL` + `SUPABASE_KEY` in Render backend

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guides and troubleshooting.

> API keys are set in each platform's dashboard — never committed to Git.

</details>

---

## Running Tests

```bash
# Activate virtual environment, then:
pytest backend/tests/test_e2e.py -v
```

**21 tests** across 4 categories:

| Category        | Tests | Covers                                                      |
| --------------- | ----- | ----------------------------------------------------------- |
| Happy Path      | 6     | Health check, root, databases, runs, reset, docs            |
| Edge Cases      | 11    | Invalid inputs, missing runs, empty messages, all 404 paths |
| Rate Limiting   | 2     | 429 trigger + structured response body                      |
| Error Structure | 2     | Consistent JSON error format for 404 & 422                  |

---

## Team Dual Core

Built for **Hackfest 2.0 ft. Turgon AI** — February 2026.
