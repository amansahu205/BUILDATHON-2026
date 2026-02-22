# IMPLEMENTATION_PLAN.md — VERDICT
> AI-Powered Deposition Coaching & Trial Preparation Platform  
> Version: 1.0.0 — Hackathon Edition | February 21, 2026  
> Team: VoiceFlow Intelligence | Track: AI Automation — August.law Sponsor Track  
> Build Window: **48 hours** | Feb 20 (6 PM) → Feb 22 (6 PM)
<!-- Updated: Feb 22 2026 — Nia removed, Databricks Vector Search added, voiceagents integrated -->
<!-- Last edited: Feb 22 2026 18:00 — Added Section 0: live implementation status snapshot -->

---

## TABLE OF CONTENTS

0. [Current Implementation Status (Feb 22, 2026 — Live Snapshot)](#0-current-implementation-status)
1. [Overview](#1-overview)
2. [Pre-Hackathon Checklist (T-24 hrs)](#2-pre-hackathon-checklist-t-24-hrs)
3. [Phase 1 — Foundation (Hour 0–4, Fri 6–10 PM)](#3-phase-1--foundation-hour-04-fri-610-pm)
4. [Phase 2 — Core AI Agents + Databricks (Hour 4–12, Fri 10 PM–Sat 6 AM)](#4-phase-2--core-ai-agents-hour-412-fri-10-pmsat-6-am)
5. [Phase 3 — Full Pipeline (Hour 12–24, Sat 6 AM–6 PM)](#5-phase-3--full-pipeline-hour-1224-sat-6-am6-pm)
6. [Phase 4 — Polish + Brief (Hour 24–36, Sat 6 PM–Sun 6 AM)](#6-phase-4--polish--brief-hour-2436-sat-6-pmsun-6-am)
7. [Phase 5 — Integration + P1 Features (Hour 36–44, Sun 6 AM–2 PM)](#7-phase-5--integration--p1-features-hour-3644-sun-6-am2-pm)
8. [Phase 6 — Demo Preparation (Hour 44–48, Sun 2–6 PM)](#8-phase-6--demo-preparation-hour-4448-sun-26-pm)
9. [Milestones & Timeline](#9-milestones--timeline)
10. [Risk Mitigation](#10-risk-mitigation)
11. [Success Criteria](#11-success-criteria)
12. [Post-MVP Roadmap](#12-post-mvp-roadmap)

---

## 0. CURRENT IMPLEMENTATION STATUS

> **Snapshot taken:** February 22, 2026 — Hackathon demo deadline (6 PM ET)  
> **Legend:** ✅ Done | ⚠️ Partial / needs wire-up | ❌ Not implemented | 🔧 Fixed today

---

### 0.1 — Backend Foundation

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI server + CORS + health check | ✅ | `/api/v1/health` returns `{ status, db, version, timestamp }` |
| All 11 SQLAlchemy ORM models | ✅ | `app/models/` — Firm, User, Case, Document, Witness, Session, Alert, Brief, RefreshToken, SessionEvent, AttorneyAnnotation |
| PostgreSQL async engine + session factory | ✅ | `app/database.py` — asyncpg driver |
| Redis client | ✅ | `app/redis_client.py` |
| JWT auth middleware + login/refresh/logout | ✅ | `app/middleware/auth.py`, `app/routers/auth.py` |
| Pydantic settings (`app/config.py`) | ✅ | All env vars declared |
| Alembic migration chain | ✅ | 3 migrations (see §0.4) |
| Seed scripts | 🔧 | `seed.py` + `seed_cases.py` — updated today to use `case_name`/`opposing_party` |

---

### 0.2 — AI Agents (`app/agents/`)

| Agent | File | Status | Notes |
|-------|------|--------|-------|
| Interrogator | `interrogator.py` | ✅ | Claude streaming + Databricks prior-statement retrieval + aggression routing |
| Objection Copilot | `objection.py` | ✅ | Databricks `fre_rules_index` → Claude FRE classification ≤1.5s |
| Inconsistency Detector | `detector.py` | ✅ | Databricks `prior_statements_index` → Nemotron scoring → Claude fallback |
| Review Orchestrator | `orchestrator.py` | ✅ | Claude brief synthesis; called at session end |
| System Prompt Builder | `prompt.py` | ✅ | `build_system_prompt(case)` — case facts + 5-dim rubric + behavioral audio tags |
| Agent Data Models | `models.py` | ✅ | `VerdictCase` Pydantic model (used by all agents) |

---

### 0.3 — Services (`app/services/`)

| Service | File | Status | Notes |
|---------|------|--------|-------|
| Claude SDK wrapper | `claude.py` | ✅ | `claude_chat()` + `claude_stream()` |
| ElevenLabs TTS/STT | `elevenlabs.py` | ✅ | `text_to_speech()`, `speech_to_text()`, `get_conversation_token()`, `build_conversation_override()` |
| ElevenLabs Conversational AI (WS) | `elevenlabs2.py` | ✅ | Signed WebSocket session start for voiceagents integration |
| Nemotron API | `nemotron.py` | ✅ | `score_contradiction()` with 5s timeout |
| Databricks Vector Search | `databricks_vector.py` | ✅ | `search_fre_rules()`, `search_prior_statements()`, `upsert_prior_statement()`, `get_embedding()` |
| Document ingestion pipeline | `ingestion.py` | ✅ | PDF/DOCX/TXT → S3 → Claude extract → Databricks upsert |
| Text extraction | `text_extraction.py` | ✅ | pdfplumber (PDF), mammoth (DOCX), plain TXT |
| AWS S3 | `s3.py` | ✅ | Presigned PUT/GET, download_bytes |
| Aggression/Vulnerability scoring | `aggression.py` | ✅ | `score_witness()`, `score_vulnerability()` — heuristic rule-based |
| Rule-based report generator | `report_generator.py` | ✅ | `generate_rule_based_report()` + coaching brief dict |
| PDF report with radar chart | `pdf_report.py` | ✅ | reportlab + matplotlib 5-axis radar chart |

---

### 0.4 — Database Migrations (Alembic)

| Revision | Description | Status |
|----------|-------------|--------|
| `a3946072bcfb` | Add `extractedFacts`, `priorStatements`, `exhibitList`, `focusAreas` to Case | ✅ Applied |
| `89b5474f4498` | Add DB-level `DEFAULT NOW()` to all `updatedAt` columns (9 tables) | ✅ Applied |
| `c7f3a1d82e04` 🔧 | **Sync Case schema with voiceagents** — rename `name→caseName`, `opposingFirm→opposingParty`; add `witnessName`, `witnessRole`, `aggressionLevel` | ⚠️ **Written — run `alembic upgrade head` to apply** |

---

### 0.5 — API Routers (`app/routers/`)

| Router | Prefix | Status | Notes |
|--------|--------|--------|-------|
| `auth.py` | `/api/v1/auth` | ✅ | Login, refresh, logout, `/me` |
| `cases.py` | `/api/v1/cases` | 🔧 | **Updated today**: all endpoints rewritten to use `case_name`, `opposing_party`, `witness_name`, `witness_role`, `aggression_level`; `UpdateCaseRequest` now typed |
| `sessions.py` | `/api/v1/sessions` | 🔧 | **Updated today**: `_build_verdict_case()` updated to read new Case columns; aggression falls back through `case.aggression_level → session.aggression → "Medium"` |
| `briefs.py` | `/api/v1/briefs` | 🔧 | **Updated today**: `session.case.case_name` (was `.name`); aggression default changed from `"STANDARD"` to `"Medium"` |
| `witnesses.py` | `/api/v1/cases` | ✅ | CRUD for Witness model |
| `documents.py` | `/api/v1` | ✅ | Presign, confirm-upload, ingestion status, fact review |
| `conversations.py` | `/api/v1/conversations` | ✅ | ElevenLabs Conversational AI session start/end |
| `tts.py` | `/api/v1/tts` | ✅ | Direct TTS endpoint |

---

### 0.6 — Case Schema Migration (Today's Core Work)

> The ElevenLabs Conversational AI WebSocket service (`voiceagents/`) expects a flat `VerdictCase` Pydantic model with snake_case fields. The legacy Prisma-generated PostgreSQL schema used `name` and `opposingFirm`. All the following were updated atomically today:

| File | Change |
|------|--------|
| `app/models/case.py` | Already had new columns pre-defined; confirmed correct |
| `app/schemas/cases.py` | `CreateCaseRequest`, `UpdateCaseRequest`, `CaseOut` — all fields match voiceagents VerdictCase |
| `app/routers/cases.py` | Rewrote all 5 endpoints; `UpdateCaseRequest` is now typed (was raw `dict`) |
| `app/routers/sessions.py` | `_build_verdict_case()` uses `case.case_name`, `case.opposing_party`, `case.witness_name`, `case.witness_role`, `case.aggression_level` |
| `app/routers/briefs.py` | `session.case.case_name` (was `session.case.name`) |
| `scripts/seed.py` | `case_name=`, `opposing_party=` |
| `scripts/seed_cases.py` | Same renames + now seeds `witness_name`, `witness_role`, `aggression_level` from JSON |
| `scripts/verify_interrogator.py` | `Case.case_name` in SELECT/ORDER BY |
| `alembic/versions/c7f3a1d82e04_sync_case_schema_with_voiceagents.py` | Migration file written (**run `alembic upgrade head`**) |

---

### 0.7 — Voiceagents Microservice (`voiceagents/`)

| Component | Status | Notes |
|-----------|--------|-------|
| FastAPI app (`app/main.py`) | ✅ | Separate service; own `Dockerfile` + `requirements.txt` |
| `VerdictCase` Pydantic model | ✅ | `app/models.py` — canonical flat schema; main backend now mirrors it |
| Session start router (`routers/sessions.py`) | ✅ | Calls `get_conversation_token()` + `build_conversation_override()` → returns signed WS URL |
| Conversation router (`routers/conversations.py`) | ✅ | ElevenLabs conversation lifecycle |
| TTS router (`routers/tts.py`) | ✅ | Direct ElevenLabs TTS |
| Analysis router (`routers/analysis.py`) | ✅ | Post-session analysis endpoint |
| Reports router (`routers/reports.py`) | ✅ | Brief/report generation |
| System prompt (`app/prompt.py`) | ✅ | `build_system_prompt(case)` — shared logic with main backend |

---

### 0.8 — Frontend (`verdict-frontend/design-first-focus/`)

| Page / Component | Status | Notes |
|-----------------|--------|-------|
| `LandingPage.tsx` | ✅ | Marketing landing |
| `LoginPage.tsx` | ✅ | Email + password |
| `OnboardingPage.tsx` | ✅ | Firm setup flow |
| `DashboardPage.tsx` | ⚠️ | Scaffolded; likely mock data — needs real `/api/v1/cases` integration |
| `CaseListPage.tsx` | ⚠️ | Scaffolded; needs updated API field names (`caseName` not `name`) |
| `NewCasePage.tsx` | ⚠️ | Scaffolded; must POST `caseName`, `witnessName`, `witnessRole`, `aggressionLevel` |
| `CaseDetailPage.tsx` | ⚠️ | Scaffolded + case-tabs subpages |
| `SessionConfigPage.tsx` | ⚠️ | Scaffolded |
| `SessionLobbyPage.tsx` | ⚠️ | Scaffolded |
| `LiveSessionPage.tsx` | ⚠️ | Three-panel layout scaffolded; alert rail + transcript wiring needed |
| `WitnessSessionPage.tsx` | ⚠️ | Scaffolded; ElevenLabs WS integration needed |
| `PostSessionPage.tsx` | ⚠️ | Scaffolded |
| `BriefViewerPage.tsx` | ⚠️ | Scaffolded; Recharts radar needed |
| `WitnessProfilePage.tsx` | ⚠️ | Scaffolded (P1.1) |
| `FactReviewPage.tsx` | ⚠️ | Scaffolded |
| `AdminPage.tsx` | ⚠️ | Scaffolded |
| `SettingsPage.tsx` | ⚠️ | Scaffolded |

> **Frontend note:** Most pages are Lovable-scaffolded with mock/static data. The primary integration gap is wiring `axios` calls to the live backend using the updated field names from today's schema change (e.g., `caseName`, `opposingParty`, `witnessName`).

---

### 0.9 — What Still Needs Doing Before Demo

| # | Task | Priority | Owner |
|---|------|----------|-------|
| 1 | **Run `alembic upgrade head`** to apply migration `c7f3a1d82e04` on Supabase | 🔴 P0 — blocks everything | Nikhil |
| 2 | **Re-seed DB** after migration: `python scripts/seed_cases.py` | 🔴 P0 | Nikhil |
| 3 | **Frontend API integration** — replace mock data with live `/api/v1/cases` calls using new field names | 🔴 P0 | Dhanush |
| 4 | **Live session alert rail** — wire SSE `QUESTION_CHUNK` / `objection_alert` / `inconsistency_alert` events to React state | 🔴 P0 | Dhanush + M4 |
| 5 | **ElevenLabs Conversational AI** — `WitnessSessionPage` connects to signed WS URL from `/api/v1/conversations` | 🔴 P0 | M4 |
| 6 | **End-to-end demo walkthrough** — login → create case → upload doc → start session → see alerts → view brief | 🔴 P0 | All |
| 7 | Verify `GET /api/v1/health` on Railway/Render returns `db: connected` | 🟡 P1 | Nikhil |
| 8 | Brief PDF generation + S3 presigned GET working | 🟡 P1 | Aman |
| 9 | FRE corpus ingested into Databricks `fre_rules_index` (`scripts/fre_xml_ingestion.py`) | 🟡 P1 | Aman |
| 10 | Behavioral Sentinel (P1.4) — NOT implementing; time budget exhausted | ⚪ Cut | — |
| 11 | SAML SSO — NOT implementing; email+password sufficient for demo | ⚪ Cut | — |

---

## 1. OVERVIEW

### Project Identity

| Field | Value |
|-------|-------|
| **App Name** | VERDICT |
| **Tagline** | AI-powered deposition coaching. From 16 hours of prep to 6. |
| **Build Type** | 48-hour hackathon MVP |
| **Demo Deadline** | Sunday, February 22, 2026 — 6:00 PM ET |
| **Track** | AI Automation — August.law Sponsor Track |
| **Secondary Prizes** | ElevenLabs (primary target), Databricks, Anthropic Claude |

### Team Roles (4 Members)

| Member | Primary Role | Owns |
|--------|-------------|------|
FOUND_AMAN
| **Nikhil** | Backend + Data Pipelines | FastAPI, PostgreSQL (SQLAlchemy), Redis, Databricks Delta Lake schema |
| **Dhanush** | Frontend + UI/UX | Vite+React pages, shadcn/ui components, Framer Motion, Recharts radar |
| **[Member 4]** | Full-Stack / Integration | Auth (SAML/JWT), WebSocket plumbing, ElevenLabs Conversational AI, deployment |

### Build Philosophy

**Documentation-first → code fast.** Every decision was made in PRD, APP_FLOW, TECH_STACK, and BACKEND_STRUCTURE before the hackathon started. During the build window we execute against the spec, not debate architecture.

**Non-negotiables (P0):**
1. P0.1 Interrogator Agent — ElevenLabs voice questions
2. P0.2 Objection Copilot — FRE classification ≤1.5s
3. P0.3 Inconsistency Detector — Nemotron scoring ≤4s
4. P0.4 Case File Ingestion — PDF → S3 → extracted facts → Databricks Vector Search upsert
5. P0.5 Coaching Brief — Review Orchestrator + ElevenLabs narration

**Cut if behind schedule (in order):** P1.4 Behavioral Sentinel → P1.2 Weakness Map → P1.1 Multi-session profile → brief PDF export → SAML SSO (keep email/password)

### Reference Documents

| Doc | Use During Build |
|-----|-----------------|
| `PRD` | Feature scope, acceptance criteria, sponsor prize requirements |
| `APP_FLOW.md` | Screen inventory, user flows, error states, decision trees |
| `TECH_STACK.md` | Exact library versions, configuration snippets |
| `BACKEND_STRUCTURE.md` | API endpoints, schema, validation rules, error codes |

---

## 2. PRE-HACKATHON CHECKLIST (T-24 HRS)

> Complete EVERYTHING on this list before 6 PM Friday. Not completing pre-work is the most common cause of hackathon failure.

### API Keys & Credentials (all 4 members verify access)

```bash
# Test each API key before the clock starts:

# Anthropic Claude
curl -X POST https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-20250514","max_tokens":10,"messages":[{"role":"user","content":"ping"}]}'

# ElevenLabs
curl -H "xi-api-key: $ELEVENLABS_API_KEY" \
  https://api.elevenlabs.io/v1/voices | jq '.voices | length'

# NVIDIA Nemotron
curl -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NEMOTRON_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"nvidia/llama-3.1-nemotron-ultra-253b-v1","messages":[{"role":"user","content":"ping"}],"max_tokens":10}'

# Databricks Vector Search (verify endpoint exists)
python -c "from databricks.vector_search.client import VectorSearchClient; c = VectorSearchClient(); print(c.list_endpoints())"

# Databricks SQL warehouse
python -c "
from databricks.sdk import WorkspaceClient
w = WorkspaceClient()
wh = w.warehouses.get(os.environ['DATABRICKS_SQL_WAREHOUSE_ID'])
print({'status': 'connected', 'warehouseId': wh.id})
"
```

### Infrastructure Pre-Provisioned

- [ ] GitHub private repo created, all 4 members added
- [ ] Vercel project linked to GitHub repo → auto-deploy on push to `main`
- [ ] Railway project created, PostgreSQL + Redis plugins added
- [ ] Supabase project created as PostgreSQL backup
- [ ] Upstash Redis created as Redis backup
- [ ] AWS S3 bucket `verdict-documents-hackathon` created (us-east-1)
- [ ] AWS IAM user with S3 PutObject/GetObject/DeleteObject policy
- [ ] Resend account verified, domain DNS records set
- [ ] All env vars loaded in `.env.local` (frontend) and `.env` (backend)
- [ ] All env vars added to Vercel dashboard and Railway dashboard

### Pre-Built Assets (prepared in the 24 hrs before)

- [ ] SQLAlchemy models written and validated (all 11 models in `app/models/`)
- [ ] FRE XML file from uscode.house.gov ready for ingestion (`scripts/fre_xml_ingestion.py`)
- [ ] Databricks Vector Search endpoint + indexes created (`scripts/setup_databricks.py`)
- [ ] Sample case document ready for demo: `demo/chen_v_metropolitan.pdf` (real-looking, 50 pages)
- [ ] ElevenLabs voice IDs confirmed: Interrogator (`Adam`), Coach (`Rachel`)
- [ ] MediaPipe face_landmarker.task model file downloaded to `public/models/`
- [ ] Figma component library exported or shadcn/ui components installed
- [ ] Monorepo workspace structure initialized (see Step 1.1)

---

## 3. PHASE 1 — FOUNDATION (Hour 0–4, Fri 6–10 PM)

**Goal:** All 4 team members have a running repo, working database, passing health check, and can start the server locally.

**All 4 members work in parallel on separate concerns during this phase.**

---

### Step 1.1 — Initialize Monorepo Structure

**Owner:** Aman (sets up, others pull)  
**Duration:** 30 minutes  
**Goal:** Establish the folder structure that all 4 members will code into for the next 47.5 hours.

```bash
# Create monorepo
mkdir verdict && cd verdict
git init
echo "packages:\n  - apps/*\n  - packages/*" > pnpm-workspace.yaml

# Initialize workspaces
mkdir -p apps/frontend apps/backend packages/shared

# Root package.json
cat > package.json << 'EOF'
{
  "name": "verdict",
  "private": true,
  "workspaces": ["apps/*", "packages/*"],
  "scripts": {
    "dev:frontend": "npm run dev --prefix verdict-frontend/design-first-focus",
    "dev:backend": "uvicorn app.main:app --reload --port 4000 --app-dir verdict-backend",
    "build": "npm run build --workspace=apps/frontend",
    "lint": "eslint apps/frontend",
    "typecheck": "tsc --noEmit -p apps/frontend/tsconfig.json",
    "test": "vitest run",
    "db:migrate": "cd verdict-backend && alembic upgrade head",
    "db:seed": "cd verdict-backend && python scripts/seed.py",
    "prepare": "husky"
  },
  "devDependencies": {
    "concurrently": "9.1.2",
    "husky": "9.1.7",
    "lint-staged": "15.4.3",
    "@commitlint/cli": "19.7.1",
    "@commitlint/config-conventional": "19.7.0",
    "eslint": "9.20.0",
    "typescript-eslint": "8.24.1",
    "prettier": "3.4.2",
    "prettier-plugin-tailwindcss": "0.6.11",
    "vitest": "2.1.8"
  }
}
EOF

# Frontend already scaffolded with Vite+React in verdict-frontend/design-first-focus/
cd verdict-frontend/design-first-focus
npm install  # Installs React, Vite, shadcn/ui, Tailwind, Zustand, axios, etc.

# Backend already set up as FastAPI/Python in verdict-backend/
cd ../../verdict-backend
pip install -r requirements.txt  # FastAPI + SQLAlchemy + all Python deps

# Push initial commit
cd ../..
git add -A
git commit -m "chore: initialize monorepo structure"
git remote add origin git@github.com:voiceflow-intelligence/verdict.git
git push -u origin main
```

**✅ Success Criteria:**
- [ ] `uvicorn app.main:app --reload --port 4000` starts FastAPI backend
- [ ] `npm run dev` (frontend) starts Vite SPA on port 5173
- [ ] All 4 team members can `git pull` and run locally
- [ ] GitHub repo visible at correct URL
- [ ] Vercel auto-deploys frontend on push (verify in Vercel dashboard)

---

### Step 1.2 — Backend Project Setup

**Owner:** Nikhil  
**Duration:** 45 minutes  
**Goal:** FastAPI server running with health check, CORS, logging, and error handler.

```bash
cd verdict-backend

# Create virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env
cp .env.example .env
# Fill in DATABASE_URL, REDIS_URL, JWT_SECRET, ANTHROPIC_API_KEY

# Run migrations
alembic upgrade head

# Seed demo data
python scripts/seed.py

# Start dev server
uvicorn app.main:app --reload --port 4000
```

```python
# app/main.py (entry point — already created)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="VERDICT API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=[settings.FRONTEND_URL], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

@app.get("/api/v1/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "db": "connected"}
```

```bash
# Test it works
uvicorn app.main:app --reload --port 4000
curl http://localhost:4000/api/v1/health
# Expected: {"status":"ok","version":"1.0.0","db":"connected"}
```

**✅ Success Criteria:**
- [ ] `curl http://localhost:4000/api/v1/health` returns `{ "status": "ok" }`
- [ ] `curl http://localhost:4000/api/v1/health` from frontend origin returns CORS headers
- [ ] Uvicorn logs show request in terminal
- [ ] `uvicorn app.main:app --reload --port 4000` starts FastAPI on port 4000

---

### Step 1.3 — Database Setup

**Owner:** Nikhil  
**Duration:** 45 minutes  
**Goal:** PostgreSQL connected, all 11 tables created, Alembic migration applied, seed data ready.

```bash
cd verdict-backend

# Set DATABASE_URL in .env (already done in Step 1.2)

# Apply migrations (creates all 11 tables)
alembic upgrade head

# Seed demo data
python scripts/seed.py
# Expected: ✅ Seed complete: firm, 3 users, 2 cases, 1 witness

# To browse data visually:
# Connect any SQL client (TablePlus, DBeaver) to your Supabase DATABASE_URL
```

```python
# app/database.py — async SQLAlchemy engine (already created)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

engine = create_async_engine(settings.DATABASE_URL_ASYNC, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

```python
# scripts/seed.py — demo data for development + hackathon demo
import asyncio
from passlib.context import CryptContext
from app.database import AsyncSessionLocal
from app.models.firm import Firm
from app.models.user import User
from app.models.case import Case

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def main():
    async with AsyncSessionLocal() as db:
        firm = Firm(name="Demo Law Group LLP", seats=10)
        db.add(firm)
        await db.flush()

        user = User(firm_id=firm.id, email="sarah.chen@demo.com", name="Sarah Chen",
                    role="PARTNER", password_hash=pwd_context.hash("Demo!Pass123"))
        db.add(user)
        await db.commit()
        print(f"✅ Seed complete: firmId={firm.id}")

asyncio.run(main())
```

```bash
python scripts/seed.py
# Expected: ✅ Seed complete: firmId=...
```

**✅ Success Criteria:**
- [ ] SQL client shows 11 tables with seed data in `Firm`, `User`, `Case`
- [ ] `alembic current` shows `head`
- [ ] `python scripts/seed.py` completes without errors
- [ ] Migration file committed to Git

---

### Step 1.4 — Redis + AWS S3 Setup

**Owner:** Nikhil  
**Duration:** 30 minutes  
**Goal:** Redis connected, S3 bucket accessible, both tested.

```python
# app/redis_client.py — async redis-py client (already created)
import redis.asyncio as aioredis
from app.config import settings

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
```

```python
# Test Redis connectivity (run from verdict-backend/)
import asyncio, redis.asyncio as aioredis
from dotenv import load_dotenv; load_dotenv()
from app.config import settings

async def test():
    r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await r.set("test", "verdict")
    val = await r.get("test")
    print(f"Redis GET: {val}")  # Should print: Redis GET: verdict
    await r.aclose()

asyncio.run(test())
```

```python
# Test S3 (upload a test file)
import boto3, os
from dotenv import load_dotenv; load_dotenv()

s3 = boto3.client("s3", region_name=os.environ["AWS_REGION"])
s3.put_object(Bucket=os.environ["S3_BUCKET_NAME"], Key="test/connection-test.txt", Body=b"verdict s3 test")
print("✅ S3 write success")
```

**✅ Success Criteria:**
- [ ] `Redis GET: verdict` printed from test script
- [ ] S3 `verdict-documents-hackathon/test/connection-test.txt` visible in AWS console
- [ ] No connection errors in FastAPI startup logs

---

### Step 1.5 — Authentication Foundation

**Owner:** [Member 4]  
**Duration:** 60 minutes  
**Goal:** JWT middleware + login/refresh endpoints working. This unblocks all other authenticated routes.

```python
# app/routers/auth.py — login endpoint (already created)
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt
from passlib.context import CryptContext
from nanoid import generate
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def sign_access_token(sub: str, firm_id: str, role: str, email: str) -> str:
    payload = {"sub": sub, "firmId": firm_id, "role": role, "email": email}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

@router.post("/login")
async def login(body: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await db.execute(select(User).where(User.email == body.email.lower()))
    user = user.scalar_one_or_none()
    if not user or not user.password_hash:
        raise HTTPException(401, detail={"code": "INVALID_CREDENTIALS"})
    if not user.is_active:
        raise HTTPException(403, detail={"code": "ACCOUNT_INACTIVE"})
    if not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(401, detail={"code": "INVALID_CREDENTIALS"})
    
    access_token = sign_access_token(str(user.id), str(user.firm_id), user.role, user.email)
    response.set_cookie("access_token", f"Bearer {access_token}", httponly=True, samesite="strict", secure=True)
    return {"success": True, "data": {"user": {"id": str(user.id), "email": user.email, "name": user.name, "role": user.role}}}
```

```python
# app/middleware/auth.py — require_auth dependency (already created)
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.config import settings

security = HTTPBearer()

async def require_auth(credentials=Depends(security), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, detail={"code": "TOKEN_INVALID"})
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(403, detail={"code": "ACCOUNT_INACTIVE"})
    return user
```

```bash
# Test login endpoint (after registering auth routes)
curl -X POST http://localhost:4000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sarah.chen@demo.com","password":"Demo!Pass123"}'
# Expected: { "success": true, "data": { "user": {...} } }
# + Set-Cookie headers with access_token and refresh_token
```

**✅ Success Criteria:**
- [ ] `POST /auth/login` with seed user credentials returns 200 + JWT
- [ ] Passing JWT to a protected route returns 200
- [ ] Passing expired/missing JWT returns 401
- [ ] `POST /auth/logout` clears tokens

---

### Phase 1 Gate Check ✅ (Hour 4 — Fri 10 PM)

Before moving to Phase 2, all 4 members verify:
- [ ] `uvicorn app.main:app --reload --port 4000` starts, no errors
- [ ] `curl /api/v1/health` → `{ "status": "ok" }`
- [ ] `curl /api/v1/auth/login` with seed data → JWT returned
- [ ] SQL client shows all 11 tables with seed rows
- [ ] Redis SET/GET working
- [ ] S3 test file exists
- [ ] Vercel preview URL deploying (check Vercel dashboard)

---

## 4. PHASE 2 — CORE AI AGENTS (Hour 4–12, Fri 10 PM–Sat 6 AM)

**Goal:** Interrogator Agent asking questions via ElevenLabs, Objection Copilot firing FRE alerts via Databricks Vector Search, and Inconsistency Detector using Databricks prior_statements_index. All three testable via manual curl before Phase 3.

**Parallel workstreams — split the team:**

| Hours 4–8 | Hours 8–12 |
|-----------|-----------|
| **Aman:** Interrogator Agent + Claude SDK + build_system_prompt | **Aman:** Objection Copilot + Databricks Vector Search (fre_rules_index) |
| **[M4]:** ElevenLabs TTS/STT integration | **[M4]:** WebSocket session room setup |
| **Nikhil:** Session + Cases API routes | **Nikhil:** Document upload pipeline (S3 presign) |
| **Dhanush:** Design system + layout shell | **Dhanush:** Login page + Dashboard shell |

---

### Step 2.1 — Claude SDK Agent Framework

**Owner:** Aman  
**Duration:** 90 minutes  
**Goal:** Reusable Claude streaming function that all 4 agents will call.

```python
# app/services/claude.py (already created)
from anthropic import AsyncAnthropic
from app.config import settings

client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

async def claude_chat(system_prompt: str, user_message: str, max_tokens=1024) -> str:
    response = await client.messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text

async def claude_stream(system_prompt: str, user_message: str, max_tokens=512):
    """Streaming Claude call — for Interrogator question generation"""
    async with client.messages.stream(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
```

```python
# Quick test
import asyncio
from app.services.claude import claude_chat

async def test():
    result = await claude_chat("You are a test.", "Say pong")
    print(f"Claude: {result}")

asyncio.run(test())
```

---

### Step 2.2a — Databricks Vector Search Setup

**Owner:** Aman  
**Duration:** 45 minutes  
**Goal:** Both Vector Search indexes created and queryable. Foundation Model API for embeddings confirmed working.

**One-time setup (run in Databricks notebook):**
```python
from databricks.vector_search.client import VectorSearchClient

client = VectorSearchClient()

# Create endpoint (takes ~15 minutes first time)
client.create_endpoint_and_wait(
    name="verdict-vector-endpoint",
    endpoint_type="STANDARD"
)

# Create FRE rules index
client.create_direct_access_index(
    endpoint_name="verdict-vector-endpoint",
    index_name="verdict.sessions.fre_rules_index",
    primary_key="id",
    embedding_dimension=1024,
    embedding_vector_column="embedding",
    schema={
        "id": "string", "rule_number": "string", "rule_title": "string",
        "article": "string", "category": "string",
        "is_deposition_relevant": "boolean", "chunk_type": "string",
        "content": "string", "doc_type": "string", "source": "string",
        "embedding": "array<float>"
    }
)

# Create prior statements index
client.create_direct_access_index(
    endpoint_name="verdict-vector-endpoint",
    index_name="verdict.sessions.prior_statements_index",
    primary_key="id",
    embedding_dimension=1024,
    embedding_vector_column="embedding",
    schema={
        "id": "string", "case_id": "string", "content": "string",
        "source_page": "int", "source_line": "int",
        "speaker": "string", "doc_id": "string",
        "embedding": "array<float>"
    }
)
```

**Ingest FRE corpus (one-time, run before demo):**
```bash
# Uses official uscode.house.gov USLM XML — all 11 Articles, Rules 101-1103
python scripts/fre_xml_ingestion.py \
  --xml data/usc28a.xml \
  --host $DATABRICKS_HOST \
  --token $DATABRICKS_TOKEN \
  --catalog verdict \
  --schema sessions
```

**New env vars to add:**
```
DATABRICKS_VECTOR_ENDPOINT=verdict-vector-endpoint
DATABRICKS_VECTOR_INDEX=verdict.sessions.prior_statements_index
DATABRICKS_FRE_INDEX=verdict.sessions.fre_rules_index
```

**✅ Success Criteria:**
- [ ] `client.list_endpoints()` shows `verdict-vector-endpoint` with status ONLINE
- [ ] `client.list_indexes("verdict-vector-endpoint")` shows both indexes
- [ ] FRE corpus query returns FRE 611(c) for "Isn't it true" question text
- [ ] Foundation Model API embedding call returns 1024-dimension vector

---

### Step 2.2b — Objection Copilot Update (P0.2)

**Owner:** Aman  
**Duration:** 30 minutes  
**Goal:** Objection Copilot queries Databricks fre_rules_index instead of hardcoded rules.

```python
# app/services/databricks_vector.py
import httpx
from databricks.vector_search.client import VectorSearchClient
from app.config import settings

async def get_embedding(text: str) -> list[float]:
    """Generate embedding via Databricks Foundation Model API."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.DATABRICKS_HOST}/serving-endpoints/databricks-gte-large-en/invocations",
            headers={"Authorization": f"Bearer {settings.DATABRICKS_TOKEN}"},
            json={"input": [text]},
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()["data"][0]["embedding"]

def search_fre_rules(question_text: str, top_k: int = 3, deposition_only: bool = True) -> list[dict]:
    """Retrieve most relevant FRE rules for a deposition question."""
    client = VectorSearchClient(
        workspace_url=settings.DATABRICKS_HOST,
        personal_access_token=settings.DATABRICKS_TOKEN,
    )
    index = client.get_index(settings.DATABRICKS_FRE_INDEX)
    filters = {"is_deposition_relevant": True} if deposition_only else {}
    results = index.similarity_search(
        query_text=question_text,
        columns=["rule_number", "rule_title", "article", "category", "content", "chunk_type"],
        filters=filters,
        num_results=top_k,
    )
    return results.get("result", {}).get("data_array", [])

def search_prior_statements(case_id: str, witness_answer: str, top_k: int = 3) -> list[dict]:
    """Retrieve semantically similar prior statements for a case."""
    client = VectorSearchClient(
        workspace_url=settings.DATABRICKS_HOST,
        personal_access_token=settings.DATABRICKS_TOKEN,
    )
    index = client.get_index(settings.DATABRICKS_VECTOR_INDEX)
    results = index.similarity_search(
        query_text=witness_answer,
        columns=["id", "content", "source_page", "source_line", "speaker"],
        filters={"case_id": case_id},
        num_results=top_k,
    )
    return results.get("result", {}).get("data_array", [])

def upsert_prior_statement(statement_id: str, case_id: str, content: str, metadata: dict) -> None:
    """Upsert a prior statement into the prior_statements_index (called during doc ingestion)."""
    import asyncio
    embedding = asyncio.run(get_embedding(content))
    client = VectorSearchClient(
        workspace_url=settings.DATABRICKS_HOST,
        personal_access_token=settings.DATABRICKS_TOKEN,
    )
    index = client.get_index(settings.DATABRICKS_VECTOR_INDEX)
    index.upsert({"id": statement_id, "case_id": case_id, "content": content,
                  "embedding": embedding, **metadata})
```

**Updated Objection Copilot flow:**
```
Question text
→ search_fre_rules(question_text, top_k=3, deposition_only=True) [Databricks fre_rules_index]
→ Top 3 FRE rules + Advisory Committee Notes
→ Claude prompt with FRE context → JSON response
→ { isObjectionable, freRule, category, explanation, confidence } in ≤1.5s
```

**✅ Success Criteria:**
- [ ] `search_fre_rules("Isn't it true you knew about the dosage?")` returns FRE 611(c) as top result
- [ ] Objection Copilot response arrives within 1,500ms
- [ ] FRE Advisory Committee Notes in context improves classification accuracy

---

### Step 2.2c — Voiceagents Integration

**Owner:** Aman  
**Duration:** 30 minutes  
**Goal:** Copy voiceagents service files into main backend. These contain the actual interrogator orchestration logic.

```bash
# Files already present in app/agents/ and app/services/ (copied from verdict_voiceagents/):
# app/agents/prompt.py        — build_system_prompt(case) 
# app/services/aggression.py  — score_witness(), score_vulnerability()
# app/services/report_generator.py — generate_rule_based_report()
# app/services/pdf_report.py  — generate_pdf() with matplotlib radar chart
```

**`build_system_prompt(case)` — key function:**
- Takes case with fields: `extracted_facts`, `prior_statements`, `exhibit_list`, `focus_areas`, `aggression_level`
- Returns rich interrogator system prompt with behavioral audio tags: `[pause]`, `[sigh]`, `[nervous laugh]`
- 5-dimension scoring rubric built into the prompt
- Replaces the 8-line INTERROGATOR_SYSTEM constant

**Updated ElevenLabs service — add to `app/services/elevenlabs.py`:**
```python
async def get_conversation_token(agent_id: str) -> str:
    """Get signed WebSocket URL for ElevenLabs Conversational AI session."""
    result = await eleven.conversational_ai.get_signed_url(agent_id=agent_id)
    return result.signed_url

def build_conversation_override(system_prompt: str, first_message: str) -> dict:
    """Build per-session ElevenLabs conversation config override.
    Prevents race conditions from mutating shared agent configuration."""
    return {
        "agent": {
            "prompt": {"prompt": system_prompt},
            "first_message": first_message,
        }
    }
```

**✅ Success Criteria:**
- [ ] `build_system_prompt(case)` returns prompt >500 chars with case-specific facts
- [ ] `get_conversation_token(agent_id)` returns a valid WSS URL
- [ ] `generate_rule_based_report(transcript, events, case)` returns dict with sessionScore

---

### Step 2.3 — Interrogator Agent (P0.1)

**Owner:** Aman  
**Duration:** 90 minutes  
**Goal:** Session creation uses `build_system_prompt(case)` + ElevenLabs `conversation_config_override`. Question streaming via SSE returns first chunk within 2 seconds.

```python
# app/agents/interrogator.py -- already implemented
# Accepts VerdictCase object; queries Databricks Vector Search for prior statements

from app.agents.models import VerdictCase
from app.services.claude import claude_stream
from app.services.databricks_vector import search_prior_statements
from app.agents.prompt import build_system_prompt


async def generate_question(
    case: VerdictCase,
    current_topic: str,
    question_number: int,
    prior_answer: str = None,
    hesitation_detected: bool = False,
    recent_inconsistency_flag: bool = False,
    prior_weak_areas: list[str] = None,
):
    system_prompt = build_system_prompt(case)

    # Retrieve semantically similar prior statements from Databricks Vector Search
    prior_context = []
    if prior_answer:
        prior_context = await search_prior_statements(
            case_id=case.id, witness_answer=prior_answer, top_k=3
        )

    aggression_instructions = {
        "STANDARD":    "Ask methodically. Allow witness to elaborate.",
        "ELEVATED":    "Press on contradictions. Use controlled silence.",
        "HIGH_STAKES": "Maximum pressure. Expose inconsistencies directly. Demand specifics.",
    }.get(case.aggression_level, "Ask methodically.")

    prior_lines = ""
    if prior_context:
        prior_lines = "Relevant prior sworn statements:
" + "
".join(
            f'- "{r.get("content", "")}"' for r in prior_context
        )

    user_message = (
        f"Case type: {case.case_type}
"
        f"Witness role: {case.witness_role}
"
        f"Current focus topic: {current_topic}
"
        f"Question number: {question_number}
"
        + (f'Witness last answered: "{prior_answer}"' if prior_answer else "First question on this topic.") + "
"
        + ("Witness hesitated significantly before answering.
" if hesitation_detected else "")
        + ("Inconsistency detected in last answer -- probe this area harder.
" if recent_inconsistency_flag else "")
        + f"{prior_lines}
"
        + f"Prior weak areas: {', '.join(prior_weak_areas) if prior_weak_areas else 'None (first session)'}
"
        + f"Aggression instruction: {aggression_instructions}

"
        + "Generate the next deposition question:"
    ).strip()

    async for chunk in claude_stream(system_prompt, user_message, max_tokens=200):
        yield chunk
```

```python
# app/routers/sessions.py -- POST /api/v1/sessions/{session_id}/agents/question

from app.agents.models import VerdictCase
from app.agents.interrogator import generate_question

@router.post("/{session_id}/agents/question")
async def stream_question(
    session_id: str,
    body: QuestionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id, Session.firm_id == user.firm_id)
        .options(selectinload(Session.case), selectinload(Session.witness))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    case = VerdictCase(
        id=session.case.id,
        case_name=session.case.name,
        case_type=session.case.case_type,
        opposing_party=session.case.opposing_firm or "Unknown",
        deposition_date=str(session.case.deposition_date or ""),
        witness_name=session.witness.name if session.witness else "Unknown",
        witness_role=session.witness.role if session.witness else "DEFENDANT",
        extracted_facts=session.case.extracted_facts or "",
        prior_statements=session.case.prior_statements or "",
        exhibit_list=session.case.exhibit_list or "",
        focus_areas=session.case.focus_areas or "",
        aggression_level=session.aggression or "STANDARD",
    )

    async def event_stream():
        full_text = ""
        yield f"data: {json.dumps({'type': 'QUESTION_START', 'questionNumber': body.questionNumber})}

"
        async for chunk in generate_question(
            case=case,
            current_topic=body.currentTopic,
            question_number=body.questionNumber,
            prior_answer=body.priorAnswer,
            hesitation_detected=body.hesitationDetected,
            recent_inconsistency_flag=body.recentInconsistencyFlag,
        ):
            full_text += chunk
            yield f"data: {json.dumps({'type': 'QUESTION_CHUNK', 'text': chunk})}

"
        try:
            audio = await text_to_speech(full_text, settings.ELEVENLABS_INTERROGATOR_VOICE_ID)
            yield f"data: {json.dumps({'type': 'QUESTION_AUDIO', 'audioBase64': base64.b64encode(audio).decode()})}

"
        except Exception:
            pass
        yield f"data: {json.dumps({'type': 'QUESTION_END', 'fullText': full_text})}

"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

```bash
# Test Interrogator via curl
curl -N -X POST http://localhost:4000/api/v1/sessions/SEED_SESSION_ID/agents/question \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "questionNumber": 1,
    "currentTopic": "TIMELINE_CHRONOLOGY",
    "hesitationDetected": false,
    "recentInconsistencyFlag": false
  }'
# Expected: stream of SSE events with question chunks, ending with QUESTION_END
```

**✅ Success Criteria:**
- [ ] First question chunk arrives within 2 seconds of request
- [ ] Full question arrives within 4 seconds
- [ ] `session_events` row created for `QUESTION_DELIVERED`
- [ ] Question is legally appropriate for the case type
- [ ] With `recentInconsistencyFlag: true`, question presses harder on the topic

---

### Step 2.4 — ElevenLabs TTS/STT Integration

**Owner:** [Member 4]  
**Duration:** 90 minutes  
**Goal:** Interrogator question text → ElevenLabs audio → WebSocket to witness. STT transcribing witness audio → text.

```python
# app/services/elevenlabs.py -- already implemented
from elevenlabs.client import AsyncElevenLabs
from app.config import settings
import httpx

eleven = AsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

VOICES = {
    "INTERROGATOR": settings.ELEVENLABS_INTERROGATOR_VOICE_ID,  # Adam
    "COACH":        settings.ELEVENLABS_COACH_VOICE_ID,          # Rachel
}


async def text_to_speech(text: str, voice_id: str = "") -> bytes:
    vid = voice_id or VOICES["INTERROGATOR"]
    audio = await eleven.text_to_speech.convert(
        voice_id=vid, text=text, model_id="eleven_turbo_v2_5"
    )
    return b"".join([chunk async for chunk in audio])


async def speech_to_text(audio_bytes: bytes) -> str:
    from io import BytesIO
    result = await eleven.speech_to_text.convert(
        file=BytesIO(audio_bytes), model_id="scribe_v1"
    )
    return result.text or ""


def get_conversation_token(agent_id: str) -> str:
    # Signed WebSocket URL for ElevenLabs Conversational AI
    resp = httpx.post(
        "https://api.elevenlabs.io/v1/convai/conversation/get_signed_url",
        headers={"xi-api-key": settings.ELEVENLABS_API_KEY},
        json={"agent_id": agent_id},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["signed_url"]


def build_conversation_override(system_prompt: str, first_message: str) -> dict:
    # Per-session config override - prevents shared agent config mutation
    return {"agent": {"prompt": {"prompt": system_prompt}, "first_message": first_message}}
```

```python
# app/routers/ws.py -- WebSocket: witness audio -> STT -> attorney transcript (abbreviated)
# Full implementation in Step 3.3; this shows the STT path only.
from fastapi import WebSocket
from app.services.elevenlabs import speech_to_text

@router.websocket("/ws/session/{session_id}")
async def session_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    role = websocket.query_params.get("role", "attorney")
    # auth check and room registry handled in Step 3.3

    async for raw in websocket.iter_bytes():
        if role == "witness":
            try:
                transcribed_text = await speech_to_text(raw)
                atty_ws = _rooms.get(session_id, {}).get("attorney")
                if atty_ws:
                    await atty_ws.send_json({
                        "type": "answer_received",
                        "transcribedText": transcribed_text,
                    })
            except Exception:
                await websocket.send_json({
                    "type": "stt_fallback",
                    "message": "Speech recognition unavailable. Please type your answer.",
                })
```

**✅ Success Criteria:**
- [ ] `textToSpeech("What was the dosage?", VOICES.INTERROGATOR)` returns audio stream
- [ ] Audio plays correctly in browser when streamed via WebSocket
- [ ] `speechToText(audioBuffer)` returns accurate text within 3 seconds
- [ ] STT fallback message received when audio is too noisy

---

### Step 2.5 — Objection Copilot (P0.2)

**Owner:** Aman  
**Duration:** 60 minutes  
**Goal:** `POST /sessions/:id/agents/objection` classifying questions in ≤1.5s. Must fire alert via WebSocket.

```python
# app/agents/objection.py -- already implemented
import json
from app.services.claude import claude_chat
from app.services.databricks_vector import search_fre_rules

OBJECTION_SYSTEM = (
    "You are an expert attorney specializing in evidence law and Federal Rules of Evidence.
"
    "Analyze the given deposition question for objectionable content.
"
    "Respond ONLY with valid JSON. No preamble, no markdown.

"
    'JSON format:
{"isObjectionable": boolean, "category": "LEADING"|"HEARSAY"|"COMPOUND"|'
    '"ASSUMES_FACTS"|"SPECULATION"|null, "freRule": string|null, "explanation": string|null, "confidence": number}'
)


async def analyze_for_objections(question_text: str, session_id: str) -> dict:
    # Top-3 relevant FRE rules from Databricks Vector Search (fre_rules_index)
    fre_results = await search_fre_rules(
        question_text=question_text, top_k=3, deposition_only=True
    )
    fre_context = ""
    if fre_results:
        fre_context = "

Relevant FRE rules:
" + "
".join(
            r.get("content", "") for r in fre_results
        )

    prompt = f'Analyze this deposition question for FRE objections:

"{question_text}"{fre_context}'
    raw = await claude_chat(OBJECTION_SYSTEM, prompt, max_tokens=256)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"isObjectionable": False, "category": None,
                "freRule": None, "explanation": None, "confidence": 0.0}
```

```bash
# Test Objection Copilot
curl -X POST http://localhost:4000/api/v1/sessions/SEED_ID/agents/objection \
  -H "Authorization: Bearer JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "questionNumber": 3,
    "questionText": "Isn'\''t it true you had completely forgotten about the dosage by then?",
    "questionTimestamp": "2026-02-21T15:14:22.000Z"
  }'
# Expected in <1500ms:
# { "isObjectionable": true, "category": "LEADING", "freRule": "FRE 611(c)", "confidence": 0.94 }
# + WebSocket objection_alert event fired to attorney room
```

**✅ Success Criteria:**
- [ ] Response arrives within 1,500ms (measure `processingMs` in response)
- [ ] "Isn't it true..." correctly flagged as LEADING (FRE 611c)
- [ ] "What did the doctor tell you?" correctly flagged as HEARSAY (FRE 801)
- [ ] "Where were you on Tuesday?" correctly returns `isObjectionable: false`
- [ ] `alerts` row created in database
- [ ] WebSocket `objection_alert` event received in browser console

---

### Step 2.7 — Railway Deployment Setup

**Owner:** [Member 4]  
**Duration:** 20 minutes  
**Goal:** Backend deployable to Railway with a single `railway up` command.

```bash
# Required config files in verdict-backend/:

# Procfile
web: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT

# railway.toml
[deploy]
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"

# .python-version
3.12

# nixpacks.toml
[phases.setup]
nixPkgs = ["python312", "gcc"]

# Deploy
railway login
railway link
railway up

# Post-deploy seed
railway run python scripts/seed.py
railway run python scripts/seed_cases.py
```

**Render backup (run once):**
```bash
# render.yaml already in verdict-backend/
# Deploy via Render dashboard: New Web Service → Connect GitHub → verdict-backend/
# Environment: set all .env vars in Render dashboard
# Start command: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Frontend env:**
```bash
# verdict-frontend/design-first-focus/.env.production
VITE_API_BASE_URL=https://verdict-backend-production.up.railway.app

# .env.development (local)
VITE_API_BASE_URL=http://localhost:4000
```

**✅ Success Criteria:**
- [ ] `curl https://verdict-backend-production.up.railway.app/api/v1/health` → `{ "status": "ok" }`
- [ ] Railway dashboard shows green health check
- [ ] Render backup URL also returning 200 health check

---

### Phase 2 Gate Check ✅ (Hour 12 — Sat 6 AM)

- [ ] Interrogator question streams from Claude → ElevenLabs TTS → audio to witness browser
- [ ] Objection Copilot fires within 1.5s — `objection_alert` visible in browser console
- [ ] Databricks Vector Search `fre_rules_index` returns FRE 611(c) for "Isn't it true..." question
- [ ] Databricks `prior_statements_index` created and accepting upserts
- [ ] Login flow works end-to-end (browser form → JWT → protected API call)
- [ ] Dashboard page renders with seed case data
- [ ] Cases API: GET /cases, POST /cases working

---

## 5. PHASE 3 — FULL PIPELINE (Hour 12–24, Sat 6 AM–6 PM)

**Goal:** Complete end-to-end session flow: upload document → S3 → Databricks Vector Search upsert → configure session → live session with all 3 P0 agents → Inconsistency Detector detecting the demo contradiction.

**This is the highest-risk phase.** If any step takes >2x estimated time, escalate immediately.

---

### Step 3.1 — Inconsistency Detector + Nemotron (P0.3)

**Owner:** Aman  
**Duration:** 120 minutes  
**Goal:** Witness answer compared against Databricks Vector Search prior_statements_index results, Nemotron scoring, alert fired at ≥0.75 confidence.

```python
# app/services/nemotron.py -- already implemented
import json
import httpx
from app.config import settings


async def score_contradiction(
    witness_answer: str,
    prior_statements: list[dict],
    case_context: str,
) -> dict:
    joined = "
".join(f'[{i}] "{s.get("content","")}"' for i, s in enumerate(prior_statements))
    prompt = (
        "You are analyzing a witness deposition for contradictions.

"
        f"Case context: {case_context}

"
        f'Witness answer just given:
"{witness_answer}"

'
        f"Prior sworn statements on record:
{joined}

"
        'Respond ONLY with JSON: {"contradiction_confidence": float, '
        '"best_match_index": int, "reasoning": "one sentence"}'
    )
    async with httpx.AsyncClient(timeout=settings.NEMOTRON_TIMEOUT_MS / 1000) as client:
        resp = await client.post(
            f"{settings.NEMOTRON_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {settings.NEMOTRON_API_KEY}"},
            json={"model": settings.NEMOTRON_MODEL,
                  "messages": [{"role": "user", "content": prompt}],
                  "max_tokens": 200, "temperature": 0.1},
        )
        resp.raise_for_status()
    return json.loads(resp.json()["choices"][0]["message"]["content"])
```

```python
# app/agents/detector.py -- already implemented
import json
from app.services.databricks_vector import search_prior_statements
from app.services.nemotron import score_contradiction
from app.services.claude import claude_chat

CONFIDENCE_THRESHOLD_LIVE = 0.75
CONFIDENCE_THRESHOLD_SECONDARY = 0.50
CONFIDENCE_THRESHOLD_CLAUDE_FALLBACK = 0.85


async def detect_inconsistency(
    question_text: str,
    answer_text: str,
    session_id: str,
    case_id: str,
    case_type: str,
    behavioral_corroboration_ms: int = 0,
) -> dict:
    # Step 1: Semantic search via Databricks Vector Search (prior_statements_index)
    prior_statements = await search_prior_statements(
        case_id=case_id, witness_answer=answer_text, top_k=5
    )
    if not prior_statements:
        return {"flagFound": False, "isLiveFired": False, "contradictionConfidence": 0,
                "priorQuote": None, "priorDocumentPage": None,
                "priorDocumentLine": None, "impeachmentRisk": "STANDARD"}

    # Step 2: Nemotron scoring (with Claude fallback)
    using_fallback = False
    try:
        score = await score_contradiction(
            witness_answer=answer_text,
            prior_statements=prior_statements,
            case_context=f"{case_type} deposition",
        )
    except Exception:
        using_fallback = True
        raw = await claude_chat(
            'Score contradiction 0-1. Return only JSON: {"contradiction_confidence": number, "best_match_index": number}',
            f'Answer: "{answer_text}"
Prior:
'
            + "
".join(f"[{i}] {s.get('content','')}" for i, s in enumerate(prior_statements)),
        )
        score = json.loads(raw)

    threshold = CONFIDENCE_THRESHOLD_CLAUDE_FALLBACK if using_fallback else CONFIDENCE_THRESHOLD_LIVE
    confidence = score.get("contradiction_confidence", 0)
    best_idx = score.get("best_match_index", -1)
    best_match = prior_statements[best_idx] if 0 <= best_idx < len(prior_statements) else None

    if confidence < CONFIDENCE_THRESHOLD_SECONDARY:
        return {"flagFound": False, "isLiveFired": False,
                "contradictionConfidence": confidence, "priorQuote": None,
                "priorDocumentPage": None, "priorDocumentLine": None, "impeachmentRisk": "STANDARD"}

    impeachment_risk = "STANDARD"
    adjusted_confidence = confidence
    if behavioral_corroboration_ms >= 800:
        impeachment_risk = "HIGH"
        adjusted_confidence = min(1.0, confidence + 0.05)

    return {
        "flagFound": True,
        "isLiveFired": confidence >= threshold,
        "contradictionConfidence": adjusted_confidence,
        "priorQuote": best_match.get("content") if best_match else None,
        "priorDocumentPage": best_match.get("metadata", {}).get("page") if best_match else None,
        "priorDocumentLine": best_match.get("metadata", {}).get("line") if best_match else None,
        "impeachmentRisk": impeachment_risk,
    }
```

```bash
# Test Inconsistency Detector
curl -X POST http://localhost:4000/api/v1/sessions/SEED_ID/agents/inconsistency \
  -H "Authorization: Bearer JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "questionNumber": 8,
    "questionText": "What was the exact dosage you administered?",
    "answerText": "Approximately $200, in that range",
    "answerTimestamp": "2026-02-21T15:15:03.000Z"
  }'
# Expected (given "The dosage was exactly $217" is in the demo doc):
# { "flagFound": true, "contradictionConfidence": 0.91, "priorQuote": "The dosage was exactly $217.", "impeachmentRisk": "STANDARD" }
# And with behavioralCorroboration.durationMs >= 800: impeachmentRisk: "HIGH"
```

**✅ Success Criteria:**
- [ ] Demo contradiction ($200 vs $217) detected with confidence ≥0.75
- [ ] Response arrives within 4,000ms
- [ ] `isLiveFired: true` for confidence ≥0.75
- [ ] `isLiveFired: false` for confidence 0.50–0.74
- [ ] `flagFound: false` for unrelated answer
- [ ] Nemotron timeout → graceful Claude fallback, threshold raised to 0.85
- [ ] WebSocket `inconsistency_alert` fires to attorney room

---

### Step 3.2 — Document Ingestion Pipeline (P0.4)

**Owner:** Nikhil  
**Duration:** 120 minutes  
**Goal:** Upload PDF → S3 → text extraction → Claude fact extraction → Databricks Vector Search upsert → ready in <3 min for 50-page demo doc.

```python
# app/services/ingestion.py
import json
import hashlib
from datetime import datetime
import pdfplumber
import mammoth
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document
from app.redis_client import redis_client
from app.services.s3 import download_bytes
from app.services.claude import claude_chat
from app.services.databricks_vector import upsert_prior_statement, get_embedding
from app.database import AsyncSessionLocal


async def run_ingestion_pipeline(document_id: str) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Document).where(Document.id == document_id))
        doc = result.scalar_one_or_none()
        if not doc:
            return

        async def update_status(status: str, **extra):
            doc.ingestion_status = status
            for k, v in extra.items():
                setattr(doc, k, v)
            await db.commit()
            await redis_client.set(
                f"ingestion:{document_id}",
                json.dumps({"status": status, **extra}),
                ex=600,
            )

        try:
            await update_status("INDEXING", ingestion_started_at=datetime.utcnow())

            # Step 1: Fetch file from S3
            file_bytes = download_bytes(doc.s3_key)

            # Step 2: Extract text based on MIME type
            if doc.mime_type == "application/pdf":
                with pdfplumber.open(__import__("io").BytesIO(file_bytes)) as pdf:
                    text_content = "\n".join(
                        page.extract_text() or "" for page in pdf.pages
                    )
                    page_count = len(pdf.pages)
            elif "wordprocessingml" in doc.mime_type:
                result_obj = mammoth.extract_raw_text(
                    {"file_like_object": __import__("io").BytesIO(file_bytes)}
                )
                text_content = result_obj.value
                page_count = 1
            else:
                text_content = file_bytes.decode("utf-8", errors="ignore")
                page_count = 1

            if not text_content.strip():
                raise ValueError(
                    "No text content found in document. Scanned/image PDFs are not supported."
                )

            await redis_client.set(
                f"ingestion:{document_id}",
                json.dumps({"status": "INDEXING", "progress": 30, "pageCount": page_count}),
                ex=600,
            )

            # Step 3: Extract structured facts via Claude
            facts_json = await claude_chat(
                "Extract structured facts from this legal document. "
                "Return ONLY valid JSON with keys: parties, keyDates, disputedFacts, priorStatements. "
                "Each is an array of objects.",
                f"Document type: {doc.doc_type}\n\nContent:\n{text_content[:12000]}",
                max_tokens=2048,
            )
            extracted_facts = json.loads(facts_json)

            await redis_client.set(
                f"ingestion:{document_id}",
                json.dumps({"status": "INDEXING", "progress": 60, "pageCount": page_count}),
                ex=600,
            )

            # Step 4: Upsert prior statements to Databricks Vector Search
            prior_statements = extracted_facts.get("priorStatements", [])
            for idx, stmt in enumerate(prior_statements):
                stmt_id = f"{document_id}-stmt-{idx}"
                content = stmt.get("text", str(stmt))
                upsert_prior_statement(
                    statement_id=stmt_id,
                    case_id=doc.case_id,
                    content=content,
                    metadata={
                        "doc_id": document_id,
                        "source_page": stmt.get("page", 0),
                        "source_line": stmt.get("line", 0),
                        "speaker": stmt.get("speaker", "UNKNOWN"),
                    },
                )

            await redis_client.set(
                f"ingestion:{document_id}",
                json.dumps({"status": "INDEXING", "progress": 90, "pageCount": page_count}),
                ex=600,
            )

            # Step 5: Mark as READY
            await update_status(
                "READY",
                page_count=page_count,
                ingestion_completed_at=datetime.utcnow(),
                extracted_facts=extracted_facts,
                databricks_doc_id=f"case:{doc.case_id}:{document_id}",
            )
            print(f"✅ Ingestion complete for {document_id} ({page_count} pages)")

        except Exception as err:
            await update_status(
                "FAILED",
                ingestion_error=str(err),
                ingestion_completed_at=datetime.utcnow(),
            )
            print(f"❌ Ingestion failed for {document_id}: {err}")
```

```bash
# Test ingestion with demo PDF
curl -X POST http://localhost:4000/api/v1/cases/DEMO_CASE_ID/documents/presign \
  -H "Authorization: Bearer JWT" \
  -H "Content-Type: application/json" \
  -d '{"filename":"chen_depo_2024.pdf","mimeType":"application/pdf","fileSizeBytes":2097152}'
# → get uploadUrl and documentId

# Upload file directly to S3 presigned URL (frontend handles this, but test with curl)
curl -X PUT "PRESIGNED_URL" \
  -H "Content-Type: application/pdf" \
  --data-binary @demo/chen_v_metropolitan.pdf

# Confirm upload and trigger ingestion
curl -X POST http://localhost:4000/api/v1/cases/DEMO_CASE_ID/documents/DOCUMENT_ID/confirm-upload \
  -H "Authorization: Bearer JWT"

# Poll status every 3 seconds
watch -n 3 curl -s http://localhost:4000/api/v1/cases/DEMO_CASE_ID/documents/DOCUMENT_ID/ingestion-status \
  -H "Authorization: Bearer JWT"
# Expected progression: UPLOADING → INDEXING (progress 30% → 70%) → READY
```

**✅ Success Criteria:**
- [ ] Demo PDF (50 pages) reaches READY status in <3 minutes
- [ ] `extractedFacts` contains recognizable parties, dates, disputed facts from the demo doc
- [ ] Databricks Vector Search returns relevant prior statements when queried for the demo case
- [ ] Duplicate upload (same file hash) returns `409 DUPLICATE_DOCUMENT`
- [ ] Image-only PDF returns error with message about text extraction

---

### Step 3.3 — Live Session WebSocket Plumbing

**Owner:** [Member 4]  
**Duration:** 90 minutes  
**Goal:** Full WebSocket session room — attorney and witness both connected, events flowing both directions.

```python
# app/routers/ws.py — WebSocket endpoint (FastAPI built-in WebSocket)
import json
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy import select
from app.redis_client import redis_client
from app.database import AsyncSessionLocal
from app.models.session import Session
from app.models.attorney_annotation import AttorneyAnnotation
from app.config import settings

router = APIRouter()

# In-memory room registry: session_id → {role: WebSocket}
_rooms: dict[str, dict[str, WebSocket]] = {}


@router.websocket("/ws/session/{session_id}")
async def session_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    token = websocket.query_params.get("token", "")
    role = websocket.query_params.get("role", "attorney")
    user_id: Optional[str] = None

    # Auth: witness uses Redis token, attorney uses JWT
    if role == "witness":
        stored = await redis_client.get(f"witness:{token}")
        if not stored:
            await websocket.close(code=4001)
            return
        stored_data = json.loads(stored)
        if stored_data.get("sessionId") != session_id:
            await websocket.close(code=4001)
            return
    else:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("sub")
        except JWTError:
            await websocket.close(code=4001)
            return

    # Register in room
    if session_id not in _rooms:
        _rooms[session_id] = {}
    _rooms[session_id][role] = websocket

    # Notify attorney when witness joins
    if role == "witness":
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Session).where(Session.id == session_id))
            sess = result.scalar_one_or_none()
            if sess:
                sess.witness_joined_at = datetime.utcnow()
                await db.commit()
        atty_ws = _rooms.get(session_id, {}).get("attorney")
        if atty_ws:
            await atty_ws.send_json({"type": "witness_connected", "sessionId": session_id})

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type", "")

            # Witness: STT transcription already handled in /agents/question SSE stream
            if msg_type == "answer_text":
                atty_ws = _rooms.get(session_id, {}).get("attorney")
                if atty_ws:
                    await atty_ws.send_json({
                        "type": "answer_received",
                        "questionNumber": msg.get("questionNumber"),
                        "transcribedText": msg.get("text", ""),
                    })

            # Attorney: timestamped annotation
            elif msg_type == "annotation_add":
                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(Session).where(Session.id == session_id))
                    sess = result.scalar_one_or_none()
                    if sess:
                        db.add(AttorneyAnnotation(
                            session_id=session_id,
                            firm_id=sess.firm_id,
                            question_number=msg.get("questionNumber", 0),
                            note_text=msg.get("text", ""),
                            session_timestamp_ms=int(datetime.utcnow().timestamp() * 1000),
                        ))
                        await db.commit()

            # Flush session event buffer to PostgreSQL every 60 s
            elif msg_type == "flush_events":
                buffered = await redis_client.get(f"session_events:{session_id}")
                if buffered:
                    # persist buffered events (handled in session event service)
                    await redis_client.delete(f"session_events:{session_id}")

    except WebSocketDisconnect:
        _rooms.get(session_id, {}).pop(role, None)
        if role == "witness":
            atty_ws = _rooms.get(session_id, {}).get("attorney")
            if atty_ws:
                await atty_ws.send_json({"type": "witness_disconnected", "sessionId": session_id})
```

```bash
# Test WebSocket connection with websocat (cross-platform alternative to wscat)
# Install: https://github.com/vi/websocat

# Attorney connection
websocat "ws://localhost:4000/ws/session/SEED_SESSION?role=attorney&token=JWT_TOKEN"

# In second terminal — witness connection
websocat "ws://localhost:4000/ws/session/SEED_SESSION?role=witness&token=WITNESS_TOKEN"

# Send a test annotation from attorney:
# > {"type":"annotation_add","questionNumber":3,"text":"Good moment to flag"}
# Expected: DB row created in attorney_annotations
```

**✅ Success Criteria:**
- [ ] Attorney and witness both connected to same session room
- [ ] `witness_connected` event fires to attorney when witness joins
- [ ] `objection_alert` event reaches only attorney socket (not witness)
- [ ] Annotation creates DB row
- [ ] Disconnect fires `witness_disconnected` to attorney room

---

### Step 3.4 — Frontend: Design System + Core Screens

**Owner:** Dhanush  
**Duration:** Full Phase 3 (parallel to Steps 3.1–3.3)  
**Goal:** All P0 screens built and navigable. Attorney can log in, see dashboard, create a case, and enter the live session screen.

```bash
cd verdict-frontend/design-first-focus

# Install UI dependencies
npm install \
  @radix-ui/react-alert-dialog@1.1.6 \
  @radix-ui/react-dialog@1.1.6 \
  @radix-ui/react-dropdown-menu@2.1.6 \
  @radix-ui/react-label@2.1.2 \
  @radix-ui/react-progress@1.1.2 \
  @radix-ui/react-select@2.1.6 \
  @radix-ui/react-switch@1.1.3 \
  @radix-ui/react-tabs@1.1.3 \
  @radix-ui/react-toast@1.2.6 \
  @radix-ui/react-tooltip@1.1.8 \
  class-variance-authority@0.7.1 \
  clsx@2.1.1 \
  tailwind-merge@2.6.0 \
  lucide-react@0.477.0 \
  framer-motion@12.4.7 \
  zustand@5.0.2 \
  @tanstack/react-query@5.66.0 \
  axios@1.7.9 \
  react-hook-form@7.54.2 \
  @hookform/resolvers@3.10.0 \
  zod@3.24.1 \
  socket.io-client@4.8.1 \
  recharts@2.15.0 \
  wavesurfer.js@7.8.11

# Install shadcn/ui CLI and init
npx shadcn@latest init
# Select: New York style, Slate color, yes to CSS variables

# Add all needed components
npx shadcn@latest add button card badge tabs dialog progress
npx shadcn@latest add select switch toast tooltip alert
npx shadcn@latest add table input label form
```

```typescript
// verdict-frontend/design-first-focus/src/lib/tailwind-config-additions.ts
// Add to tailwind.config.ts — VERDICT design tokens
const verdictColors = {
  'verdict-navy': '#0F1729',      // Primary dark — three-panel session bg
  'verdict-slate': '#1E2B3C',     // Secondary dark — card backgrounds
  'verdict-blue': '#3B82F6',      // Primary accent — attorney actions
  'verdict-red': {
    50: '#FFF0F0',
    500: '#EF4444',               // Alert rail inconsistency
    700: '#B91C1C',               // HIGH IMPEACHMENT RISK badge
  },
  'verdict-amber': '#F59E0B',     // Timer warning, objection alerts
  'verdict-green': '#10B981',     // Agent active, confirmed flags
  'verdict-purple': '#8B5CF6',    // ElevenLabs waveform
};
```

**Key screens to build (in priority order):**
1. `/login` — email/password form + JWT storage
2. `/dashboard` — case grid, session countdown badges
3. `/cases/new` — case creation form
4. `/cases/:id` — case detail with Documents/Witnesses/Sessions tabs
5. `/cases/:id/documents/facts` — fact review and confirmation
6. `/cases/:id/witnesses/new` — add witness modal
7. `/cases/:id/session/new` — session configuration
8. `/cases/:id/session/:id/lobby` — pre-session waiting room
9. `/cases/:id/session/:id/live` — **three-panel live session UI (most important)**
10. `/briefs/:id` — coaching brief viewer

```typescript
// verdict-frontend/design-first-focus/src/stores/session.store.ts — Zustand store for live session
import { create } from 'zustand';

interface Alert {
  id: string;
  type: 'OBJECTION' | 'INCONSISTENCY' | 'COMPOSURE';
  questionNumber: number;
  firedAt: string;
  freRule?: string;
  priorQuote?: string;
  contradictionConfidence?: number;
  impeachmentRisk?: 'STANDARD' | 'HIGH';
  decision?: 'CONFIRMED' | 'REJECTED' | 'ANNOTATED';
}

interface SessionStore {
  sessionId: string | null;
  status: 'LOBBY' | 'ACTIVE' | 'PAUSED' | 'COMPLETE';
  questionCount: number;
  elapsedSeconds: number;
  alerts: Alert[];
  transcript: Array<{ speaker: 'INTERROGATOR' | 'WITNESS'; text: string; questionNumber: number }>;
  agentStatus: { interrogator: string; objection: string; inconsistency: string; sentinel: string };
  
  // Actions
  addAlert: (alert: Alert) => void;
  resolveAlert: (alertId: string, decision: Alert['decision']) => void;
  addTranscriptLine: (line: { speaker: string; text: string; questionNumber: number }) => void;
  incrementQuestion: () => void;
  setStatus: (status: SessionStore['status']) => void;
}

export const useSessionStore = create<SessionStore>((set) => ({
  sessionId: null,
  status: 'LOBBY',
  questionCount: 0,
  elapsedSeconds: 0,
  alerts: [],
  transcript: [],
  agentStatus: { interrogator: 'STANDBY', objection: 'STANDBY', inconsistency: 'STANDBY', sentinel: 'INACTIVE' },
  
  addAlert: (alert) => set((s) => ({ alerts: [alert, ...s.alerts] })),
  resolveAlert: (alertId, decision) => set((s) => ({
    alerts: s.alerts.map(a => a.id === alertId ? { ...a, decision } : a),
  })),
  addTranscriptLine: (line) => set((s) => ({ transcript: [...s.transcript, line] })),
  incrementQuestion: () => set((s) => ({ questionCount: s.questionCount + 1 })),
  setStatus: (status) => set({ status }),
}));
```

**✅ Success Criteria (Phase 3 frontend):**
- [ ] `/login` → submits → JWT stored → redirects to `/dashboard`
- [ ] `/dashboard` renders case cards from API
- [ ] `/cases/new` form creates a case, redirects to case detail
- [ ] Document upload UI shows progress while ingestion runs
- [ ] Fact review screen displays extracted parties, dates, statements
- [ ] Live session screen: three-panel layout renders correctly on 1280px+ desktop
- [ ] Alert card slides in when `objection_alert` WebSocket event arrives

---

### Phase 3 Gate Check ✅ (Hour 24 — Sat 6 PM)

- [ ] Upload `demo/chen_v_metropolitan.pdf` → ingestion completes → facts extracted
- [ ] Create session → attorney and witness both connect via WebSocket
- [ ] Start session → Interrogator asks first question via ElevenLabs audio
- [ ] Witness answers → STT transcribes → transcript appears on attorney screen
- [ ] $217 demo contradiction → Inconsistency Detector fires → alert visible in alert rail
- [ ] Leading question → Objection Copilot fires within 1.5s → alert visible
- [ ] All P0 flows technically functional (polish TBD Phase 4)

---

## 6. PHASE 4 — POLISH + BRIEF (Hour 24–36, Sat 6 PM–Sun 6 AM)

**Goal:** P0.5 Coaching Brief fully working. Full session flow is smooth. ElevenLabs Coach voice narrating brief clips. All judge-facing interactions are polished.

---

### Step 4.1 — Review Orchestrator + Coaching Brief (P0.5)

**Owner:** Aman  
**Duration:** 90 minutes

```python
# app/agents/orchestrator.py -- already implemented
import json, re
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import AsyncSessionLocal
from app.models.session import Session
from app.models.brief import Brief
from app.models.witness import Witness
from app.services.claude import claude_chat
from app.services.elevenlabs import text_to_speech
from app.services.s3 import upload_bytes
from app.config import settings


async def generate_coaching_brief(session_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Session).where(Session.id == session_id)
            .options(selectinload(Session.alerts), selectinload(Session.case),
                     selectinload(Session.witness))
        )
        session = result.scalar_one_or_none()
        if not session:
            raise ValueError("Session not found")

        confirmed_flags = [a for a in session.alerts
                           if a.attorney_decision == "CONFIRMED"
                           and a.alert_type in ("INCONSISTENCY", "INCONSISTENCY_SECONDARY")]
        objections       = [a for a in session.alerts if a.alert_type == "OBJECTION"]
        composure_alerts = [a for a in session.alerts if a.alert_type == "COMPOSURE"]
        weakness_map     = _compute_weakness_map(session.alerts)

        session_score = round(
            (1 - len(confirmed_flags) / max(session.question_count, 1)) * 50
            + (25 if not objections else max(0, 25 - len(objections) * 5))
            + (min(weakness_map.get("timeline", 75) + weakness_map.get("financial", 75), 100) / 100) * 25
        )

        flag_lines = "
".join(
            f'- Q{a.question_number}: contradicts "{(a.prior_quote or "")[:80]}" (conf: {a.contradiction_confidence})'
            for a in confirmed_flags
        ) or "None"

        narrative_prompt = (
            f"Generate a professional attorney coaching brief.

"
            f"Case: {session.case.name} ({session.case.case_type})
"
            f"Witness: {session.witness.name} ({session.witness.role})
"
            f"Session #{session.session_number} | Score: {session_score}/100 | "
            f"Questions: {session.question_count}
"
            f"Confirmed inconsistencies: {len(confirmed_flags)} | Objections: {len(objections)}

"
            f"Inconsistency details:
{flag_lines}

"
            f"Weakness scores: {json.dumps(weakness_map)}

"
            "Write a 3-paragraph brief. Be specific and actionable. End with 3 numbered recommendations."
        )
        narrative_text = await claude_chat(
            "You are a senior litigation coach writing coaching briefs for attorneys.",
            narrative_prompt, max_tokens=1500
        )

        audio_manifest = []
        for flag in confirmed_flags[:3]:
            clip = (
                f"At question {flag.question_number}, the witness contradicted prior sworn statement: "
                f'"{(flag.prior_quote or "")[:100]}". Impeachment risk: {flag.impeachment_risk}.'
            )
            try:
                audio_bytes = await text_to_speech(clip, settings.ELEVENLABS_COACH_VOICE_ID)
                s3_key = f"firms/{session.firm_id}/briefs/{session_id}/alert_{flag.id}.mp3"
                upload_bytes(s3_key, audio_bytes, content_type="audio/mpeg")
                audio_manifest.append({"alertId": flag.id, "s3Key": s3_key})
            except Exception:
                pass

        recommendations = [l.strip() for l in narrative_text.split("
")
                           if re.match(r"^\d+\.", l.strip())][:3] or [
            "Practice precise, consistent answers for the key disputed facts.",
            "Pause before answering questions beginning with 'Isn\'t it true...'",
            "Review all prior deposition testimony carefully before the next session.",
        ]

        brief = Brief(
            session_id=session_id, firm_id=session.firm_id,
            witness_id=session.witness_id,
            generation_status="COMPLETE",
            generation_completed_at=datetime.utcnow(),
            session_score=session_score,
            consistency_rate=1 - len(confirmed_flags) / max(session.question_count, 1),
            confirmed_flags=len(confirmed_flags), objection_count=len(objections),
            composure_alert_count=len(composure_alerts),
            top_recommendations=recommendations, narrative_text=narrative_text,
            weakness_map_scores=weakness_map, elevenlabs_audio_manifest=audio_manifest,
        )
        db.add(brief)

        wit = (await db.execute(select(Witness).where(Witness.id == session.witness_id))).scalar_one_or_none()
        if wit:
            wit.latest_score = session_score
            if session.session_number == 1:
                wit.baseline_score = session_score

        await db.commit()
        await db.refresh(brief)
        return {"briefId": brief.id, "sessionScore": session_score}


def _compute_weakness_map(alerts: list) -> dict:
    axes = ["timeline", "financial", "communications", "relationships", "actions", "prior_statements"]
    scores = {a: 75 for a in axes}
    for alert in alerts:
        if alert.attorney_decision != "CONFIRMED":
            continue
        topic = (alert.metadata or {}).get("topic", "").lower().replace("_", "")
        matched = next((a for a in axes if topic in a.replace("_", "")), None)
        if matched:
            scores[matched] = max(0, scores[matched] - 15)
    return scores
```

**✅ Success Criteria:**
- [ ] Brief generates within 3 minutes of session end
- [ ] `narrativeText` is coherent professional prose (not boilerplate)
- [ ] `topRecommendations` has 3 specific, actionable items
- [ ] ElevenLabs Coach voice audio clips uploaded to S3 and accessible
- [ ] `weaknessMapScores` correctly reflects topics where alerts fired
- [ ] `GET /briefs/:id` returns full brief JSON
- [ ] Brief viewer page renders score, inconsistencies, and recommendations

---

### Step 4.2 — Coaching Brief Frontend (P0.5)

**Owner:** Dhanush  
**Duration:** 60 minutes  
**Goal:** Beautiful, polished brief viewer. Recharts radar chart rendering. Audio clip playback working.

```typescript
// verdict-frontend/design-first-focus/src/pages/BriefViewerPage.tsx — key components

// Score card with animated count-up
import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

function ScoreCard({ score, delta }: { score: number; delta?: number }) {
  const [displayed, setDisplayed] = useState(0);
  
  useEffect(() => {
    // Count up animation 1.2s
    const start = Date.now();
    const duration = 1200;
    const tick = () => {
      const elapsed = Date.now() - start;
      const progress = Math.min(elapsed / duration, 1);
      setDisplayed(Math.round(progress * score));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [score]);

  const color = score >= 75 ? 'text-green-500' : score >= 50 ? 'text-amber-500' : 'text-red-500';
  
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
      <div className={`text-7xl font-bold ${color}`}>{displayed}</div>
      <div className="text-gray-400 text-sm">/100</div>
      {delta !== undefined && (
        <div className={`text-sm font-medium ${delta >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {delta >= 0 ? '▲' : '▼'} {Math.abs(delta)} pts vs Session 1
        </div>
      )}
    </motion.div>
  );
}

// Weakness Map Radar
import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer } from 'recharts';

function WeaknessMap({ scores }: { scores: Record<string, number> }) {
  const data = Object.entries(scores).map(([key, value]) => ({
    subject: key.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase()),
    value,
    fullMark: 100,
  }));
  
  return (
    <ResponsiveContainer width="100%" height={400}>
      <RadarChart data={data}>
        <PolarGrid stroke="#1E2B3C" />
        <PolarAngleAxis dataKey="subject" tick={{ fill: '#94A3B8', fontSize: 12 }} />
        <Radar name="Score" dataKey="value" stroke="#3B82F6" fill="#3B82F6" fillOpacity={0.3} />
      </RadarChart>
    </ResponsiveContainer>
  );
}
```

**✅ Success Criteria:**
- [ ] Score card number counts up from 0 → actual score in 1.2s
- [ ] Score color: green ≥75, amber 50–74, red <50
- [ ] Radar chart renders with 6 axes (7 if Sentinel active) with correct scores
- [ ] Audio clip plays when attorney clicks [▶ Play clip] on inconsistency row
- [ ] HIGH IMPEACHMENT RISK badge renders in red with pulse animation
- [ ] [Download PDF] button triggers PDF generation

---

### Step 4.3 — UI Polish Pass

**Owner:** Dhanush + [Member 4]  
**Duration:** 90 minutes  
**Goal:** Live session screen looks professional. Alert rail animations working. All P0 screens are demo-ready.

**Critical UI checklist for judges:**
- [ ] Three-panel layout: left control (220px) | center transcript | right alert rail (320px)
- [ ] Alert card slides in from right with spring animation (300ms)
- [ ] Red border pulse on HIGH IMPEACHMENT RISK alerts (×2 cycles)
- [ ] Timer shows amber at <10 min, red at <5 min
- [ ] Waveform animates when Interrogator speaks (wavesurfer.js)
- [ ] "Monitoring active" green pulse in alert rail header
- [ ] [CONFIRMED] click → green flash → grays out card
- [ ] [REJECTED] click → slides out right 200ms
- [ ] Transcript auto-scrolls to latest exchange

---

### Phase 4 Gate Check ✅ (Hour 36 — Sun 6 AM)

- [ ] Full demo run-through: login → create case → upload doc → add witness → configure session → start → 3 questions → contradiction detected → end → brief generated → brief viewed
- [ ] ElevenLabs coach voice plays in brief
- [ ] Recharts radar chart renders correctly
- [ ] All animations functional
- [ ] No console errors during demo flow
- [ ] Brief PDF download working

---

## 7. PHASE 5 — INTEGRATION + P1 FEATURES (Hour 36–44, Sun 6 AM–2 PM)

**Goal:** P1.4 Behavioral Sentinel, P1.1 multi-session witness profile, P1.2 Weakness Map in Databricks, Databricks Delta Live Tables streaming. These are sponsor prize differentiators — implement only what can be demo'd cleanly.

---

### Step 5.1 — Behavioral Sentinel Frontend (P1.4)

**Owner:** Dhanush + Aman  
**Duration:** 60 minutes  
**Goal:** MediaPipe Face Mesh running in-browser, AU vectors sent to backend, composure alerts firing.

```typescript
// verdict-frontend/design-first-focus/src/lib/mediapipe-sentinel.ts
import { FaceLandmarker, FilesetResolver } from '@mediapipe/tasks-vision';

let faceLandmarker: FaceLandmarker | null = null;

export async function initMediaPipe() {
  const vision = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.20/wasm'
  );
  faceLandmarker = await FaceLandmarker.createFromOptions(vision, {
    baseOptions: {
      modelAssetPath: '/models/face_landmarker.task',
      delegate: 'GPU',
    },
    runningMode: 'VIDEO',
    numFaces: 1,
    outputFaceBlendshapes: true,
  });
  return faceLandmarker;
}

export function extractAUVectors(landmarks: any[]): {
  au4: number; au6: number; au12: number; au20: number; au45: number;
} {
  // Map MediaPipe blendshape scores to FACS Action Units
  if (!landmarks || landmarks.length === 0) return { au4: 0, au6: 0, au12: 0, au20: 0, au45: 0 };
  
  const bs = landmarks[0].categories;
  const findScore = (name: string) => bs.find((c: any) => c.categoryName === name)?.score ?? 0;
  
  return {
    au4: findScore('browInnerUp'),          // Brow furrow
    au6: findScore('cheekSquintLeft'),       // Cheek raise
    au12: findScore('mouthSmileLeft'),       // Lip corner
    au20: findScore('mouthStretchLeft'),     // Lip stretch (fear)
    au45: findScore('eyeBlinkLeft'),         // Blink rate
  };
}

// React hook for witness view
export function useBehavioralSentinel(sessionId: string, socket: any) {
  useEffect(() => {
    if (!sentinelEnabled) return;
    
    let videoEl: HTMLVideoElement;
    let animFrameId: number;
    let expressionStartTime: number | null = null;
    let currentExpression: string | null = null;

    const processFrame = async () => {
      if (!faceLandmarker || !videoEl) return animationFrameId = requestAnimationFrame(processFrame);
      
      const results = faceLandmarker.detectForVideo(videoEl, Date.now());
      const auVectors = extractAUVectors(results.faceBlendshapes ?? []);
      
      // Detect sustained Fear expression (AU4 + AU20 both > 0.6 for ≥800ms)
      const isFear = auVectors.au4 > 0.6 && auVectors.au20 > 0.6;
      
      if (isFear && !expressionStartTime) {
        expressionStartTime = Date.now();
        currentExpression = 'FEAR';
      } else if (!isFear) {
        if (expressionStartTime && currentExpression) {
          const durationMs = Date.now() - expressionStartTime;
          if (durationMs >= 800) {
            // Send to backend
            socket.emit('behavioral_vectors', { auVectors, durationMs, questionNumber: currentQuestion });
          }
        }
        expressionStartTime = null;
        currentExpression = null;
      }
      
      animFrameId = requestAnimationFrame(processFrame);
    };
    
    // Initialize camera
    navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
      videoEl = document.createElement('video');
      videoEl.srcObject = stream;
      videoEl.play();
      initMediaPipe().then(() => requestAnimationFrame(processFrame));
    }).catch(() => {
      console.warn('Camera denied — Behavioral Sentinel disabled');
    });
    
    return () => cancelAnimationFrame(animFrameId);
  }, [sentinelEnabled]);
}
```

**✅ Success Criteria:**
- [ ] Camera permission prompt appears when Sentinel is enabled
- [ ] AU vectors appear in backend logs when simulating Fear expression
- [ ] `POST /sessions/:id/agents/behavioral` creates COMPOSURE alert
- [ ] `composure_alert` WebSocket event appears in attorney alert rail
- [ ] Inconsistency flag upgraded to HIGH IMPEACHMENT RISK when Sentinel corroborates
- [ ] Camera denial → graceful silent degradation (no error, sentinel badge shows "Inactive")

---

### Step 5.2 — Databricks Delta Lake Integration

**Owner:** Nikhil  
**Duration:** 60 minutes  
**Goal:** Session events streaming to Databricks, Weakness Map data queryable.

```python
# app/services/databricks_sql.py -- Delta Lake session event streaming
import json
from databricks import sql as databricks_sql
from app.config import settings

_conn = None


def _get_connection():
    global _conn
    if _conn is None:
        _conn = databricks_sql.connect(
            server_hostname=settings.DATABRICKS_HOST.replace("https://", ""),
            http_path=f"/sql/1.0/warehouses/{settings.DATABRICKS_SQL_WAREHOUSE_ID}",
            access_token=settings.DATABRICKS_TOKEN,
        )
    return _conn


def stream_session_events_to_delta(events: list[dict]) -> None:
    if not events:
        return
    try:
        conn = _get_connection()
        with conn.cursor() as cursor:
            values = ", ".join(
                f"('{e['sessionId']}', '{e['firmId']}', '{e['eventType']}', "
                f"'{e['occurredAt']}', '{json.dumps(e.get('emotionVectors', {}))}', "
                f"{e.get('questionNumber') or 'null'})"
                for e in events
            )
            cursor.execute(
                f"INSERT INTO {settings.DATABRICKS_CATALOG}.{settings.DATABRICKS_SCHEMA}"
                f".session_events VALUES {values}"
            )
        print(f"Streamed {len(events)} events to Databricks Delta")
    except Exception as err:
        print(f"Databricks stream failed (non-critical): {err}")


def query_weakness_map_scores(session_id: str) -> dict[str, float]:
    try:
        conn = _get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                f"SELECT topic_axis, AVG(confidence_score) as avg_score "
                f"FROM {settings.DATABRICKS_CATALOG}.{settings.DATABRICKS_SCHEMA}.inconsistency_flags "
                f"WHERE session_id = '{session_id}' GROUP BY topic_axis"
            )
            rows = cursor.fetchall()
        return {row[0]: round(float(row[1]), 2) for row in rows}
    except Exception:
        return {}
```

**✅ Success Criteria:**
- [ ] Session events appear in Databricks Delta table after session ends
- [ ] Emotion vectors visible in Delta Live Tables UI (for judge demo)
- [ ] Weakness Map scores queryable via Databricks SQL

---

### Step 5.3 — Multi-Session Witness Profile (P1.1)

**Owner:** Dhanush + Nikhil  
**Duration:** 45 minutes  
**Goal:** Witness profile page shows score trend chart, improvement delta, and persisting inconsistencies.

```typescript
// apps/frontend/src/app/cases/[caseId]/witnesses/[witnessId]/page.tsx
// Score trend chart using Recharts LineChart
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine } from 'recharts';

function ScoreTrendChart({ sessions, depositionDate }: { sessions: any[]; depositionDate?: string }) {
  const data = sessions.map((s, i) => ({
    name: `Session ${i + 1}`,
    score: s.score,
    date: new Date(s.endedAt).toLocaleDateString(),
  }));

  if (depositionDate) {
    data.push({ name: 'Deposition', score: null as any, date: new Date(depositionDate).toLocaleDateString() });
  }

  return (
    <LineChart width={500} height={250} data={data}>
      <CartesianGrid strokeDasharray="3 3" stroke="#1E2B3C" />
      <XAxis dataKey="name" tick={{ fill: '#94A3B8' }} />
      <YAxis domain={[0, 100]} tick={{ fill: '#94A3B8' }} />
      <Tooltip />
      {depositionDate && <ReferenceLine x="Deposition" stroke="#EF4444" strokeDasharray="4 4" label="Depo" />}
      <Line type="monotone" dataKey="score" stroke="#3B82F6" strokeWidth={2} dot={{ fill: '#3B82F6' }} />
    </LineChart>
  );
}
```

---

### Phase 5 Gate Check ✅ (Hour 44 — Sun 2 PM)

- [ ] Behavioral Sentinel fires composure alert in live demo with real camera
- [ ] Composure corroboration upgrades inconsistency to HIGH IMPEACHMENT RISK
- [ ] Databricks table has session events visible in Delta Live Tables
- [ ] Witness profile shows score trend across 3 demo sessions
- [ ] Load test: 5 concurrent WebSocket connections (use Artillery or k6)
- [ ] All P0 flows still working after P1 additions (regression check)

---

## 8. PHASE 6 — DEMO PREPARATION (Hour 44–48, Sun 2–6 PM)

**Goal:** Win the hackathon. Every minute of this phase is invested in the demo experience, not new features.

---

### Step 6.1 — Demo Scenario Setup

**Owner:** Aman (leads), all members verify

**Demo Scenario A — Primary (5 minutes, live):**
```
1. Attorney (Aman) opens VERDICT on main screen
2. Shows pre-loaded case: "Chen v. Metropolitan Hospital"
3. Navigates to Dr. Emily Chen's witness profile — shows Session 1 score: 44/100
4. Clicks "Start Session 2" — witness (Dhanush on separate laptop) joins via token link
5. Interrogator asks: "Ms. Chen, what was the exact dosage you administered?"
6. Dhanush answers: "Approximately $200, in that range"
7. [DEMO MOMENT] Inconsistency Detector fires within 4 seconds:
   ▸ Alert rail: "INCONSISTENCY DETECTED — 91% confidence"
   ▸ Prior quote: "The dosage was exactly $217" (from uploaded depo PDF, page 47)
   ▸ Behavioral Sentinel: shows FEAR expression detected (pre-staged or live camera)
   ▸ Alert upgrades to HIGH IMPEACHMENT RISK
8. Session ends — Brief Generation animation plays
9. Opens Brief: score 79/100 (+35 pts from Session 1), coach voice narrates
10. Recharts Weakness Map: Financial axis is lowest (34/100)
11. "This is why attorneys choose VERDICT"
```

**Demo Scenario B — Sponsor Prize Moments (woven in):**
- ElevenLabs: "Listen to the coach brief in your own language" → switch coach voice locale
- Databricks: "Here's our Delta Live Tables real-time dashboard" → show Databricks workspace tab
- Claude: "Four agents, all orchestrated by Claude Sonnet 4" → show architecture slide

**Pre-staged demo data (load before presentation):**
```bash
# Seed base firm + user
python scripts/seed.py

# Seed all 5 demo cases with rich interrogation context
python scripts/seed_cases.py
# Creates the 5 demo cases from verdict-backend/data/verdict_cases.json:
# 1. Lyman v. Capital City Transit District (Personal Injury)
# 2. State of Utah v. Derek Gunn (Securities Fraud)
# 3. Atlantis Property Group v. Tamontes Construction (Breach of Contract)
# 4. Reyes v. Haller Medical Group (Medical Malpractice)
# 5. Chen v. Meridian Financial Advisors (Elder Financial Abuse)
```

---

### Step 6.2 — Production Deployment

**Owner:** [Member 4]  
**Duration:** 30 minutes

```bash
# 1. Final environment variable audit
python -c "
import os
from dotenv import load_dotenv
load_dotenv('verdict-backend/.env')
filled = [k for k, v in os.environ.items() if v and 'VERDICT' not in k]
print(f'{len(filled)} env vars set')
"
# Verify all vars match Railway dashboard

# 2. Run database migration on production
DATABASE_URL=$PRODUCTION_DATABASE_URL alembic upgrade head

# 3. Seed production with demo data
railway run python scripts/seed.py
railway run python scripts/seed_cases.py

# 4. Deploy backend to Railway
# Railway auto-deploys on push to main — just push:
git add -A && git commit -m "feat: hackathon submission - all P0 features complete"
git push origin main

# 5. Verify Railway build succeeds (watch build logs)
# 6. Verify Vercel build succeeds
# 7. Run smoke tests on production URLs

# Smoke test checklist:
curl https://api.verdict.law/api/v1/health
# → { "status": "ok" }

curl -X POST https://api.verdict.law/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"sarah.chen@demo.com","password":"Demo!Pass123"}'
# → 200 + JWT

# 8. Pre-load demo case in production browser session
# Open verdict.law/dashboard → confirm case "Chen v. Metropolitan Hospital" visible
# Click into witness Dr. Emily Chen → confirm 3 session history visible
# Navigate to brief #3 → confirm score 79/100, radar chart, audio plays
```

---

### Step 6.3 — Backup Demo Recording

**Owner:** All team members  
**Duration:** 30 minutes  
**Goal:** Record a 5-minute demo video in case of live demo failure.

```bash
# Tools: OBS Studio or QuickTime (Mac)
# Recording checklist:
# - Use production URL (not localhost)
# - 1920×1080 minimum
# - Record audio via screen capture
# - Show: login → case → live session → contradiction alert → brief → radar chart
# - No hesitations; rehearse 3× before recording
# - Upload to Google Drive, have direct URL ready on phone

# Backup URL in Devpost submission:
# "Demo video: https://drive.google.com/file/d/..."
```

---

### Step 6.4 — Devpost Submission

**Owner:** Aman  
**Deadline:** 30 minutes before judging  
**Duration:** 45 minutes

```markdown
## Devpost Submission Checklist

### Required Fields
- [ ] Project name: VERDICT
- [ ] Tagline: "AI-powered deposition coaching. From 16 hours of prep to 6."
- [ ] Description: 400-word summary (see PRD §1 for narrative)
- [ ] Demo video link: [production demo URL]
- [ ] Live app URL: https://verdict.law
- [ ] GitHub repo: https://github.com/voiceflow-intelligence/verdict

### Sponsor Prize Categories to Select
- [ ] August.law AI Automation Track (primary)
- [ ] ElevenLabs Best Use of Voice AI
- [ ] Databricks Best Use of Delta Lake / Delta Live Tables
- [ ] Anthropic Best Use of Claude SDK

### Tech Stack Tags to Add
- ElevenLabs, Anthropic Claude, NVIDIA Nemotron, Databricks
- Vite+React, FastAPI, PostgreSQL, Redis, WebSocket
- MediaPipe, Framer Motion, Recharts

### Architecture Diagram
Include: 4-agent system diagram (from PRD Appendix)
Show: data flow from document upload → Databricks Vector Search → session → alerts → brief

### Sponsor Prize Justification (include in description)
ElevenLabs: Dual use — Interrogator voice + Coach narration. Real-time STT for witness answers.
Databricks: Delta Live Tables streaming emotion vectors. Weakness Map powered by Databricks SQL.
Claude: Orchestrates all 4 agents. Streaming question generation. Brief synthesis.
```

---

### Step 6.5 — Pitch Rehearsal (×3)

**Schedule:** Hour 46, 47, and 30 min before judging

```
Pitch Structure (5 minutes):
  0:00 — Hook: "What does a litigation partner do the night before a deposition?"
  0:30 — Problem: 16 hours of manual roleplay. No consistency scoring. No coaching.
  1:00 — Solution: VERDICT. 4 AI agents working together.
  1:30 — LIVE DEMO (Scenario A — 2.5 minutes)
  4:00 — Sponsor integrations: "Built on ElevenLabs, Databricks, Claude, Nemotron"
  4:30 — Traction: "August.law's exact use case. $14,400 addressable market at AmLaw 200."
  5:00 — Ask: "This is the future of trial preparation."

Key moments to nail:
  • The $217 inconsistency detection moment — pause, let the alert land
  • The HIGH IMPEACHMENT RISK upgrade — explain Behavioral Sentinel in one sentence
  • The radar chart — "Financial axis: 34/100. We know exactly where to coach next."
  • The coach voice narrating the brief — "This is ElevenLabs running in production"

Questions to prep for:
  Q: "Is this a lie detector?"
  A: "No. It's a consistency scorer. Same as what a skilled attorney notices — we just do it in 4 seconds."
  
  Q: "What about attorney-client privilege?"
  A: "All data lives within the firm's tenant. Encrypted at rest and in transit. Optionally self-hosted."
  
  Q: "Why wouldn't attorneys just use GPT?"
  A: "GPT can't hear the hesitation, can't cross-reference 500 pages in 4 seconds, and can't generate an ElevenLabs coaching brief. VERDICT is built for this specific workflow."
```

---

## 9. MILESTONES & TIMELINE

### Milestone 1: Foundation Complete ✅
**Target:** Hour 4 (Fri 10 PM)
- [ ] Monorepo initialized, all 4 members building
- [ ] FastAPI health check live (`uvicorn app.main:app --reload --port 4000`)
- [ ] PostgreSQL: all 11 tables created via `alembic upgrade head`
- [ ] Redis connected
- [ ] S3 connected
- [ ] Login endpoint returning JWT
- [ ] Vercel auto-deploying frontend

### Milestone 2: Agents Live ✅
**Target:** Hour 12 (Sat 6 AM)
- [ ] Interrogator Agent streaming questions via Claude
- [ ] ElevenLabs TTS delivering audio to witness browser
- [ ] ElevenLabs STT transcribing witness answers
- [ ] Objection Copilot firing within 1.5s
- [ ] Databricks Vector Search endpoint online; fre_rules_index queryable for Objection Copilot
- [ ] Databricks prior_statements_index created and ready for document ingestion upserts
- [ ] WebSocket session room: attorney + witness connected

### Milestone 3: Full Pipeline ✅
**Target:** Hour 24 (Sat 6 PM)
- [ ] Document upload → S3 → text extraction → Databricks Vector Search upsert → READY in <3 min
- [ ] Extracted facts displayed in Fact Review screen
- [ ] Inconsistency Detector: demo contradiction ($200 vs $217) detected
- [ ] Nemotron confidence score ≥0.75 triggering live alert
- [ ] Full session flow functional end-to-end
- [ ] All frontend screens navigable (design may still be rough)

### Milestone 4: MVP Demo-Ready ✅
**Target:** Hour 36 (Sun 6 AM)
- [ ] P0.5 Coaching Brief generated with Claude narrative
- [ ] ElevenLabs Coach voice narrating flagged moments
- [ ] Recharts radar chart rendering in brief viewer
- [ ] Brief PDF downloadable
- [ ] All animations and transitions smooth
- [ ] No blocking console errors in demo flow

### Milestone 5: Submission-Ready ✅
**Target:** Hour 48 (Sun 6 PM)
- [ ] All P0 features demoable in production (verdict.law)
- [ ] P1.4 Behavioral Sentinel: composure alerts fire on camera
- [ ] Databricks Delta Live Tables: session events streaming
- [ ] Multi-session witness profile: score trend chart working
- [ ] Devpost submission complete
- [ ] Backup demo video recorded and uploaded
- [ ] Pitch rehearsed ×3 with all team members

---

## 10. RISK MITIGATION

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| ElevenLabs TTS latency >2s | Medium | High — core UX | Use `eleven_turbo_v2_5` model. Test latency in Phase 2. Fallback: text-only questions |
| Nemotron API rate limit hit | Medium | Medium — affects Inconsistency Detector | Cache embeddings in Redis. Use batch calls. Fallback: Claude-only scoring at threshold 0.85 |
| Databricks Vector Search endpoint cold start | Medium | Medium — delays first query | Pre-warm endpoint before demo; disable Scale to Zero in endpoint settings |
| MediaPipe WASM not loading | Low | Low — P1.4 only | Host face_landmarker.task in /public/models. CDN fallback. Feature can be skipped |
| Databricks warehouse cold start | Medium | Low — demo only | Warm warehouse before demo. Keep alternative pre-queried static data |
| WebSocket drops on demo laptop WiFi | Medium | High — live demo failure | Test on hackathon venue WiFi. Have hotspot backup. Record demo video |
| Alembic migration fails in production | Low | Critical | Test migration on staging DB first. Pre-deploy snapshot. Rollback: `alembic downgrade -1` |
| JWT secret mismatch between frontend/backend | Low | High | Single source of truth: Railway env vars. Verify before demo |
| Claude API rate limit (heavy agent use) | Low | Medium | Queue requests. Distribute across session. Use streaming to reduce apparent latency |

### Timeline Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Phase 2 agents take 2× estimated time | All subsequent phases slip | Cut Behavioral Sentinel entirely if Phase 2 is late. Focus on P0 only |
| Frontend screens too rough for judges | Perception of incomplete product | Dhanush focuses on live session screen first — that's what judges see |
| Brief generation >3 min in demo | Demo dead air is fatal | Pre-generate brief in demo seed data. Just "reload" the brief page |
| Team member gets sick/unavailable | 25% capacity loss | Each member writes a 1-paragraph handoff doc for their module after Phase 2 |
| Demo laptop battery dies | Demo fails | Both demo laptops fully charged. Chargers on table. App is deployed — use any laptop |

### Scope Risks

| Temptation | Decision |
|-----------|---------|
| "Let's add voice-to-text real-time transcript display" | ❌ Cut if not already built. Shows aren't scored on features not in PRD |
| "Let's integrate iManage Matter Management" | ❌ P2. Not started |
| "Let's add multi-jurisdiction FRE rules" | ❌ P2. Databricks `fre_rules_index` is sufficient |
| "Let's make a native iOS app" | ❌ Web only. No time |
| "Let's add LangChain" | ❌ Claude SDK is sufficient. Dependency risk not worth it |
| "Let's polish the marketing landing page" | ⚠️ Only if all P0 features are shipped with time remaining |

---

## 11. SUCCESS CRITERIA

### P0 — Minimum Viable Demo (must all be true to submit)

| # | Criterion | Test |
|---|-----------|------|
| 1 | Interrogator Agent asks legally appropriate questions via ElevenLabs voice | Manual: Start session, hear question audio within 2s |
| 2 | Objection Copilot fires within 1.5s for a leading question | Manual: Ask "Isn't it true..." → alert in <1500ms |
| 3 | Inconsistency Detector detects $200 vs $217 contradiction at ≥0.75 confidence | Manual: Demo script → see INCONSISTENCY alert |
| 4 | Document upload → S3 → Databricks Vector Search upsert → READY in <3 min for 50-page PDF | Automated timing test |
| 5 | Coaching Brief generated with Claude narrative + ElevenLabs coach voice | Manual: End session → wait → hear coach voice in brief |
| 6 | Full session flow navigable without errors: login → case → session → brief | Manual E2E walkthrough |
| 7 | Attorney alert rail shows objection and inconsistency alerts in real-time | Manual: Live session with witness browser open |
| 8 | Brief deployed at production URL (verdict.law) | `curl https://verdict.law` → 200 |

### Performance Targets (from PRD §8.1)

| Metric | Target | Test Method |
|--------|--------|-------------|
| Objection Copilot response | ≤ 1,500ms | `processingMs` field in response |
| Inconsistency Detector response | ≤ 4,000ms | `processingMs` field in response |
| ElevenLabs TTS to audio start | ≤ 2,000ms | `audio_latency_ms` in session_events |
| Document ingestion (50 pages) | ≤ 3 minutes | Ingestion status polling |
| Concurrent WebSocket sessions | ≥ 5 simultaneous | Artillery load test |
| Brief generation | ≤ 3 minutes | Timer from session end to brief.generation_status = COMPLETE |

### Sponsor Prize Criteria Met

| Sponsor | What's Required | Our Implementation |
|---------|----------------|-------------------|
| **August.law** (primary) | End-to-end AI legal workflow | 4-agent deposition prep pipeline + optional Behavioral Sentinel module |
| **ElevenLabs** | Voice AI as core feature | Interrogator TTS + STT + Coach narration |
| **Databricks** | Delta Lake or Delta Live Tables used meaningfully | Session events + emotion vectors streamed to Delta |
| **Anthropic** | Claude SDK with meaningful orchestration | 4 agents all using Claude; streaming; tool use |

---

## 12. POST-MVP ROADMAP

### Immediate Post-Hackathon (Feb 23 – Mar 7)

1. **Production hardening** — Add comprehensive error boundaries, retry logic, connection pooling
2. **August.law partnership call** — Discuss integration requirements, compliance review
3. **AmLaw 200 pilot outreach** — 5 firms for paid pilot at $2,500/month
4. **SAML SSO** — Full Okta/AzureAD integration for enterprise pilot firms
5. **Enhanced PDF export** — Full brief PDF with branded letterhead (extends `app/services/pdf_report.py`)
6. **WCAG 2.1 AA audit** — Accessibility compliance for enterprise legal tools

### P1 Feature Completion (Q2 2026)

| Feature | PRD Reference | Priority |
|---------|--------------|---------|
| P1.1 Cross-session witness profile — full UI | BACKEND_STRUCTURE §witnesses | High |
| P1.2 Weakness Map — Databricks SQL-powered | PRD §P1.2 | High |
| P1.3 Argument Strength Scoring — Nemotron per answer | PRD §P1.3 | Medium |
| P1.4 Behavioral Sentinel — firm-wide rollout | PRD §P1.4 | Medium |
| Firm Admin Panel — full user management | APP_FLOW §2.7 | High |
| Multi-language Interrogator voices | ElevenLabs locale API | Medium |

### P2 Feature Roadmap (Q3 2026)

| Feature | Description |
|---------|-------------|
| **P2.1 Whisper-in-Ear Mode** | Real-time coaching cues to attorney earpiece via ElevenLabs spatial audio |
| **P2.2 Multi-Jurisdiction FRE** | Databricks Vector Search-indexed state evidence rules (CA, NY, TX, FL) |
| **P2.3 Case Outcome Analytics** | MLflow-powered prediction: deposition score → trial outcome correlation |
| **P2.4 Telephony Integration** | Twilio-based remote deposition support |
| **P2.5 Matter Management** | iManage + Clio integration for case file sync |

### User Feedback Loop

```
Week 1 post-launch:
  → 5 pilot attorney interviews (2 partners, 2 associates, 1 paralegal)
  → NPS survey after first session
  → Session recording review (with consent): where do attorneys click most?

Month 1:
  → Track: ingestion success rate, brief generation time, score improvement across 3 sessions
  → Track: which alert types get confirmed vs rejected (calibrate Nemotron threshold)
  → Track: Behavioral Sentinel opt-in rate (measures comfort with feature)
```

### Revenue Model Post-Hackathon

| Tier | Price | Seats | Features |
|------|-------|-------|---------|
| **Starter** | $500/month | 5 | P0 features, email auth |
| **Professional** | $2,500/month | 25 | P0+P1, SSO, Databricks |
| **Enterprise** | $10,000/month | Unlimited | Full stack, self-hosted option, SLA |

**Target ARR at 12 months:** 20 firms × $2,500/month × 12 = $600,000

---

*IMPLEMENTATION_PLAN.md — VERDICT v1.0.0 — Hackathon Edition*  
*B2B Deposition Coaching Platform — Team VoiceFlow Intelligence*  
*NYU Startup Week Buildathon 2026 | AI Automation — August.law Sponsor Track*
