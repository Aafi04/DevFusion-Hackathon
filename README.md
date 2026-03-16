<div align="center">

# SchemaDoc AI

### Intelligent Data Dictionary Agent

_Hackfest 2.0 ft. Turgon AI — Team Dual Core_

Mohd Aafi (Team Lead) · Rahul Kumar (Frontend Developer)

NOTICE! Live Demo has been taken down due to increase in API Usage, Demo Video still accessible on the page :)

[![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=next.js&logoColor=white)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Orchestration-1C3C3C?logo=langchain&logoColor=white)](https://github.com/langchain-ai/langgraph)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-AI_Engine-4285F4?logo=google&logoColor=white)](https://ai.google.dev)
[![Neon](https://img.shields.io/badge/Neon-PostgreSQL-00e599?logo=postgresql&logoColor=white)](https://neon.tech)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)

</div>

---

## Overview

SchemaDoc AI connects to **any SQL database** — SQLite, PostgreSQL, MySQL, or MSSQL — and automatically generates a complete, AI-enriched data dictionary with quality scoring, relationship visualization, natural language querying, and business-ready reports.

The system uses a **cyclic LangGraph state machine** with a deterministic validation gate that catches AI hallucinations, prevents data loss, and self-corrects via retry loops — guaranteeing schema integrity.

**Live deployment:** Frontend on [Vercel](https://schema-doc-ai-hackfest-2-0-ft-turgo.vercel.app) · Backend on [Railway](https://schemadoc-ai-hackfest-20-ft-turgon-ai-production.up.railway.app/api/health) · Database on [Neon PostgreSQL](https://neon.tech)

---

## Architecture

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│     Extract      │────▶│  AI Enrichment   │────▶│   Validation     │────▶│    Dashboard     │
│  (SQLAlchemy +   │     │  (Gemini 2.5     │     │   Gate           │     │  (Next.js 15 +   │
│   Profiling)     │     │   Flash + ReAct) │     │  (Deterministic) │     │   TailwindCSS)   │
└──────────────────┘     └──────────────────┘     └───────┬──────────┘     └──────────────────┘
        │                        ▲                        │
        │                        │  FAILED + retry < 3    │
  Neon PostgreSQL                └────────────────────────┘
  (3 databases,
   575k+ rows)
```

| Layer                 | Role                                                           | Technology                         |
| --------------------- | -------------------------------------------------------------- | ---------------------------------- |
| **Data Ingestion**    | Dialect-agnostic schema extraction + statistical profiling     | SQLAlchemy 2.0, ThreadPoolExecutor |
| **Orchestration**     | Cyclic state machine with conditional retry edges              | LangGraph StateGraph               |
| **Enrichment Engine** | Semantic analysis with forensic log evidence via ReAct agents  | Gemini 2.5 Flash + LangChain       |
| **Validation Gate**   | Anti-hallucination guard — column-level integrity verification | Deterministic Python               |
| **Backend API**       | REST API serving pipeline, chat, export, and schema endpoints  | FastAPI + Uvicorn                  |
| **Frontend**          | Interactive dashboard with 7 pages                             | Next.js 15 + TailwindCSS           |
| **Cloud Database**    | 3 real-world PostgreSQL databases (575k+ rows)                 | Neon PostgreSQL (serverless)       |

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

### Cloud Databases (Always Available)

Three real-world databases hosted on Neon PostgreSQL — no local setup required:

| Database                    | Tables | Rows     | Domain                           |
| --------------------------- | ------ | -------- | -------------------------------- |
| **Olist E-Commerce Brazil** | 8      | 550,000+ | Brazilian marketplace orders     |
| **Bike Store Sales**        | 9      | 9,000+   | Retail store inventory & orders  |
| **Chinook Music Store**     | 11     | 15,600+  | Digital music store transactions |

### Anti-Hallucination Pipeline

- **Deterministic Validation Gate** compares every AI-enriched column set against the raw source of truth
- Detects **data loss** (missing columns) and **hallucinations** (invented columns)
- Automatically retries enrichment up to 3 times on failure
- Full execution trace visible in the animated Pipeline Visualizer

### Performance

- **Batched SQL profiling** — all column stats computed in one query per table (not per-column)
- **Parallel table processing** — ThreadPoolExecutor profiles tables concurrently
- **Schema caching** — unchanged schemas skip AI enrichment entirely
- **Report caching** — business reports generated once per run, served instantly on revisit
- **Event-based connection pooling** — compatible with Neon's serverless pooler via `SET search_path`

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
- A [Google Gemini API key](https://aistudio.google.com/apikey)

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
# Edit .env and add your GOOGLE_API_KEY

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

> When `NEON_DATABASE_URL` is set in `.env`, cloud databases appear automatically in the dropdown alongside any local SQLite files.

---

## Project Structure

```
├── railway.toml                    # Railway deployment config (Nixpacks)
├── requirements.txt                # Python dependencies
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
│   │       ├── enrichment_node.py  # Gemini ReAct enrichment
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

| Component              | Technology                              |
| ---------------------- | --------------------------------------- |
| AI Model               | Google Gemini 2.5 Flash                 |
| Orchestration          | LangGraph (cyclic StateGraph)           |
| LLM Framework          | LangChain Core + LangChain Google GenAI |
| Database Introspection | SQLAlchemy 2.0 (dialect-agnostic)       |
| Cloud Database         | Neon PostgreSQL (serverless pooler)     |
| Backend API            | FastAPI + Uvicorn                       |
| Rate Limiting          | slowapi (IP-based sliding window)       |
| E2E Testing            | pytest + httpx AsyncClient              |
| Frontend               | Next.js 16, TypeScript, TailwindCSS     |
| Animations             | Framer Motion                           |
| Data Fetching          | TanStack React Query                    |
| ER Visualization       | ReactFlow                               |
| Markdown Rendering     | react-markdown + remark-gfm             |
| Backend Hosting        | Railway (Nixpacks)                      |
| Frontend Hosting       | Vercel                                  |

---

## Deployment

The application is **fully deployed and publicly accessible**:

| Service     | Platform | URL                                                                                                                                                   |
| ----------- | -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Frontend    | Vercel   | [schema-doc-ai-hackfest-2-0-ft-turgo.vercel.app](https://schema-doc-ai-hackfest-2-0-ft-turgo.vercel.app)                                              |
| Backend API | Railway  | [schemadoc-ai-hackfest-20-ft-turgon-ai-production.up.railway.app](https://schemadoc-ai-hackfest-20-ft-turgon-ai-production.up.railway.app/api/health) |
| Database    | Neon     | PostgreSQL serverless (3 schemas, 575k+ rows)                                                                                                         |

### Self-Hosting

<details>
<summary>Deploy your own instance</summary>

#### Backend → Railway

1. [railway.app](https://railway.app) → New Project → Deploy from GitHub
2. Root directory = **repo root** (`railway.toml` handles the config)
3. Add env vars: `GOOGLE_API_KEY`, `NEON_DATABASE_URL`, `CORS_ORIGINS`

#### Frontend → Vercel

1. [vercel.com](https://vercel.com) → Add New Project → Import repo
2. Set **Root Directory** to `frontend`
3. Add env var: `NEXT_PUBLIC_API_URL` = your Railway backend URL

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
