# Research Agent (Phase 1)

[![Live Demo](https://img.shields.io/badge/Demo-Vercel%20Live-brightgreen?style=for-the-badge&logo=vercel)](https://research-agent-taupe-eta.vercel.app)
[![Tests](https://img.shields.io/badge/Tests-33%20Passed-success?style=for-the-badge&logo=pytest)](https://github.com/Sarthakbotmfs/research-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

An evidence-grounded, local-first research agent application for Windows. It accepts a technical or scientific claim, autonomously discovers scholarly material from **OpenAlex** and **Crossref**, extracts and classifies evidence into empirical categories (Supporting, Contradicting, Common Ground, and Insufficient), and generates a fully traceable research report with citation links and export capabilities.

**Live Deployment:** [https://research-agent-taupe-eta.vercel.app](https://research-agent-taupe-eta.vercel.app)

---

## Key Features

- **Scholarly Discovery**: Public API adapters for OpenAlex and Crossref with bounded retries, rate-limiting, and DOI/URL deduplication.
- **Evidence Integrity**: Every material finding is linked to a stored source passage with a SHA-256 cryptographic hash and author independence checks.
- **Balanced Adversarial Search**: Automatically formulates targeted counter-evidence queries to uncover negative results, refutations, and publication bias.
- **Local-First & Secure**: SQLite with WAL mode, robust SSRF protection blocking private IPs, link-local addresses, and loopback redirects.
- **Provider-Neutral LLM**: Configurable OpenAI-compatible interface with structured Pydantic schema validation and a deterministic fallback mode for zero-credential discovery.
- **Real-Time Observability**: Server-Sent Events (SSE) streaming actual research events, query counts, and extracted passages to a restrained dark-themed React dashboard.
- **Multi-Format Exports**: One-click downloads for Markdown (`.md`), JSON Research Dossier (`.json`), and formatted PDF (`.pdf`).

---

## Architecture Overview

```
Research Ahh ai/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints: research, events (SSE), evidence, report, exports
│   │   ├── core/         # Settings, sanitized logging, limits, and SSRF security
│   │   ├── db/           # SQLAlchemy 2.x models, async sessions, and repository
│   │   ├── providers/    # OpenAlex, Crossref, and OpenAI-compatible LLM adapters
│   │   ├── research/     # Planner, extractor, classifier, verification, synthesis, orchestrator
│   │   ├── exports/      # Markdown, JSON, and PDF document generators
│   │   ├── schemas/      # Validated Pydantic contracts and structured output models
│   │   └── main.py       # FastAPI application and CORS setup
│   ├── migrations/       # Alembic async migration versions
│   ├── tests/            # 33 comprehensive unit and integration tests
│   └── pyproject.toml    # Backend dependencies, ruff, and pytest configuration
├── frontend/
│   ├── src/
│   │   ├── api/          # Fetch client and EventSource SSE subscription
│   │   ├── components/   # Navbar, ClaimSubmission, LiveInvestigation, FindingsDashboard, etc.
│   │   ├── types/        # TypeScript interfaces and Zod schemas
│   │   ├── App.tsx       # State management and view router
│   │   └── main.tsx      # QueryClientProvider root
│   ├── tailwind.config.js
│   └── vite.config.ts
├── .env.example          # Environment variables template
└── README.md
```

---

## Prerequisites

- **OS**: Windows 10/11
- **Python**: 3.12 (managed via `uv` or system Python)
- **Node.js**: v18+ (tested on Node v24)
- **Shell**: Windows PowerShell

---

## Installation & Setup

### 1. Clone & Set Up Backend

In Windows PowerShell from the repository root:

```powershell
# Create Python 3.12 virtual environment (if not already created)
uv venv --python 3.12 .venv

# Activate environment
.venv\Scripts\Activate.ps1

# Install backend dependencies
uv pip install -e "backend[dev]"

# Copy environment configuration
Copy-Item .env.example .env
```

### 2. Configure Environment (`.env`)

Edit `.env` as desired:

```ini
# Application
ENV=development
LOG_LEVEL=INFO
HOST=127.0.0.1
PORT=8000
FRONTEND_ORIGIN=http://localhost:5173

# Database
DATABASE_URL=sqlite+aiosqlite:///./data/research_agent.db

# LLM Provider (Optional: if blank, runs in Discovery-Only Heuristic Mode)
LLM_PROVIDER=openai
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key-here
LLM_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=60.0
LLM_MAX_OUTPUT_TOKENS=4096

# Scholarly Indices Polite Headers
CROSSREF_MAILTO=research-agent@example.com
OPENALEX_EMAIL=research-agent@example.com
```

> **Privacy Notice**: Hosted LLM inference transmits the evaluated research claim and retrieved scholarly abstract excerpts to the configured model provider.

### 3. Database Migrations

Apply database migrations:

```powershell
cd backend
..\.venv\Scripts\alembic.exe upgrade head
cd ..
```

### 4. Set Up Frontend

```powershell
cd frontend
npm install
cd ..
```

---

## Starting the Application

Open two Windows PowerShell windows:

### Terminal 1: Backend Server

```powershell
.venv\Scripts\Activate.ps1
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The backend API and Swagger documentation will be available at:
- **API URL**: `http://127.0.0.1:8000`
- **Swagger Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/health`

### Terminal 2: Frontend Dashboard

```powershell
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## Running the Automated Test Suite

All tests execute with mocked network endpoints and require zero external credentials or network connectivity:

```powershell
# Run backend pytest suite (33 tests)
cd backend
..\.venv\Scripts\pytest.exe -v
cd ..

# Run backend linter & formatter
cd backend
..\.venv\Scripts\ruff.exe check app tests
cd ..

# Run frontend TypeScript type checking and build
cd frontend
npm run build
cd ..
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/research` | Submit a claim and launch research investigation |
| `GET` | `/api/research` | List recent research tasks (history) |
| `GET` | `/api/research/{task_id}` | Get task details, subclaims, and source summary |
| `GET` | `/api/research/{task_id}/events` | Server-Sent Events (SSE) stream with `Last-Event-ID` replay |
| `GET` | `/api/research/{task_id}/evidence` | List all extracted evidence items and category counts |
| `GET` | `/api/research/{task_id}/report` | Retrieve final synthesized research report |
| `GET` | `/api/research/{task_id}/export?format=md` | Download Markdown report document |
| `GET` | `/api/research/{task_id}/export?format=json` | Download complete JSON research dossier |
| `GET` | `/api/research/{task_id}/export?format=pdf` | Download formatted PDF research report |

---

## Integration Status: Live vs. Mocked

- **OpenAlex API**: Real live integration tested against public endpoint `https://api.openalex.org/works`.
- **Crossref API**: Real live integration tested against public endpoint `https://api.crossref.org/works` using the Polite Pool header.
- **LLM Provider**: Tested in both **OpenAI-compatible hosted mode** and **Deterministic Discovery-Only Heuristic Mode** (when no API key is supplied).
- **Automated Tests**: Use offline HTTP mocking (`respx`) and deterministic test fixtures so testing is fast, isolated, and requires no API keys or internet access.

---

## Known Limitations & Phase 2 Roadmap

1. **Paywalled Literature**: The agent respects access boundaries and only extracts abstracts and permitted open-access web full texts. Paywalled proprietary papers only have their peer-reviewed abstracts evaluated.
2. **PDF Table Extraction**: Complex multi-column statistical tables inside PDF binaries are simplified into text passages; deep table OCR will be introduced in Phase 2.
3. **Graph Clustering**: In Phase 2, co-citation graph analysis will be added to further quantify consensus clusters across scholarly citation networks.
