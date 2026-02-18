# Nexus MENA OSINT

Nexus MENA OSINT is a multidomain platform for disinformation and risk monitoring across MENA in Arabic and English.

## What this MVP includes

- Unified investigation workflow: case creation, collection, analysis, risk scoring.
- Multi-platform connector layer for X, Telegram, YouTube, Instagram, and Web intelligence.
- Narrative and coordination analysis with explainable risk signals.
- Evidence-first model with case timelines and graph-ready entity links.
- Supabase-ready SQL schema for production deployment.

## Monorepo layout

- `apps/web`: Next.js investigation dashboard.
- `apps/api`: FastAPI intelligence API and analysis engine.
- `workers`: ingest and analysis workers for scheduled orchestration.
- `infra/supabase/migrations`: baseline relational schema.

## Quick start

### 1) API

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r apps/api/requirements.txt
uvicorn app.main:app --reload --app-dir apps/api
```

API runs at `http://localhost:8000`.

### 2) Web

```bash
cd apps/web
npm install
npm run dev
```

Web runs at `http://localhost:3000`.

Create `apps/web/.env.local` from `apps/web/.env.example` if needed.

### 3) Tests

```bash
pytest apps/api/tests -q
```

### 4) Optional workers

```bash
pip install -r workers/requirements.txt
python workers/ingest_worker.py
python workers/analyze_worker.py
```

## Core API endpoints

- `GET /health`
- `GET /api/v1/cases`
- `POST /api/v1/cases`
- `POST /api/v1/cases/{case_id}/collect`
- `POST /api/v1/cases/{case_id}/analyze`
- `GET /api/v1/cases/{case_id}`
- `GET /api/v1/cases/{case_id}/graph`

## Security posture

- Do not place tokens in source files.
- Use environment variable secrets only.
- Rotate any leaked keys before deployment.
- Keep human review required for high-severity actions in production.
