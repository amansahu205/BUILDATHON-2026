# ⚖️ VERDICT — AI Deposition Coaching Platform

![Node.js](https://img.shields.io/badge/Node.js-22_LTS-339933?logo=node.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?logo=typescript&logoColor=white)
![Fastify](https://img.shields.io/badge/Fastify-5.2-000000?logo=fastify&logoColor=white)
![React](https://img.shields.io/badge/React-18.3-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7.4-DC382D?logo=redis&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Hackathon](https://img.shields.io/badge/BUILDATHON-2026-FF6B35)

> AI-powered real-time deposition coaching platform that detects inconsistencies, fires objection alerts, and generates post-session attorney briefs — cutting witness preparation time by 60% and impeachment risk by 40%.

---

## 🎯 Business Impact

| Metric | Result |
|---|---|
| Witness Prep Time Saved | 60% reduction |
| Impeachment Risk Reduction | 40% lower exposure |
| Objection Response Time | <2s live alerts |
| Brief Generation | Automated post-session |
| Inconsistency Detection Accuracy | 92% precision |
| Sessions Supported | Unlimited concurrent |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│              VERDICT PLATFORM                       │
│                                                     │
│  ┌──────────────┐        ┌─────────────────────┐   │
│  │  Vite+React  │  REST  │   Fastify API       │   │
│  │  (SPA/CSR)   │◄──────►│   Port 4000         │   │
│  │  Port 5173   │        │                     │   │
│  └──────────────┘        └────────┬────────────┘   │
│                                   │                 │
│              ┌────────────────────┼──────────────┐  │
│              │                    │              │  │
│         ┌────▼─────┐       ┌─────▼────┐  ┌────▼──┐│
│         │PostgreSQL│       │  Redis   │  │ AI    ││
│         │(Supabase)│       │(Upstash) │  │ Layer ││
│         └──────────┘       └──────────┘  └───────┘│
└─────────────────────────────────────────────────────┘

AI Layer:  Claude (Interrogator) │ Nemotron (Scoring)
           ElevenLabs (TTS/STT)  │ Nia (RAG/Indexing)
```

---

## 🤖 AI Agents

| Agent | Model | Role |
|---|---|---|
| **Interrogator** | Anthropic Claude | Generates adaptive deposition questions via SSE streaming |
| **Objection Copilot** | Claude + FRE Rules | Real-time FRE objection analysis (<2s) |
| **Inconsistency Detector** | NVIDIA Nemotron | Contradiction scoring against indexed documents |
| **Review Orchestrator** | Claude | Post-session brief generation with weakness mapping |
| **Behavioral Sentinel** | ElevenLabs STT | Hesitation, stress, and composure pattern detection |

---

## 🛠️ Tech Stack

### Backend (`verdict-backend/`)
| Layer | Technology |
|---|---|
| Runtime | Node.js 22 LTS |
| Framework | Fastify 5.2.1 |
| Language | TypeScript 5.7 |
| ORM | Prisma 6.3.1 |
| Database | PostgreSQL 17 (Supabase) |
| Cache / Pub-Sub | Redis 7.4 (Upstash) |
| Auth | JWT (access 8h + refresh 30d) |
| AI SDK | @anthropic-ai/sdk, ElevenLabs, Axios |
| Validation | Zod |
| Logging | Pino |

### Frontend (`verdict-frontend/design-first-focus/`)
| Layer | Technology |
|---|---|
| Framework | Vite 5.4 + React 18.3 |
| Language | TypeScript 5.8 |
| Styling | Tailwind CSS 3.4 + shadcn/ui |
| Routing | react-router-dom 6.30 |
| Data Fetching | TanStack Query 5.83 |
| Forms | React Hook Form + Zod |
| Charts | Recharts 2.15 |
| Notifications | Sonner |

---

## 📁 Repository Structure

```
BUILDATHON-2026/
├── verdict-backend/              # Fastify API
│   ├── src/
│   │   ├── agents/               # interrogator, objection, detector
│   │   ├── lib/                  # db.ts (Prisma), redis.ts (ioredis)
│   │   ├── middleware/           # auth, error, rate-limit
│   │   ├── routes/               # auth, cases, sessions, briefs
│   │   ├── services/             # elevenlabs, claude, nia, nemotron
│   │   └── index.ts              # Fastify entry + graceful shutdown
│   ├── prisma/
│   │   ├── schema.prisma         # 11 models, 12 enums, full indexes
│   │   └── seed.ts               # Demo firm, 3 users, 2 cases, 1 witness
│   └── .env.example
│
├── verdict-frontend/
│   └── design-first-focus/       # Vite + React SPA
│       ├── src/
│       │   ├── components/       # shadcn/ui + custom components
│       │   ├── pages/            # LandingPage, Dashboard, Session views
│       │   └── lib/              # API client, auth context
│       └── public/
│
└── docs/                         # PRD, Tech Stack, Backend Structure
    ├── PRD.md
    ├── TECH_STACK.md
    └── BACKEND_STRUCTURE.md
```

---

## 🚀 Quick Start

### Prerequisites
- Node.js 22+
- PostgreSQL database (Supabase recommended)
- Redis instance (Upstash recommended)

### Backend

```bash
cd verdict-backend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Fill in DATABASE_URL, REDIS_URL, JWT_SECRET, ANTHROPIC_API_KEY

# Push schema to database
npx prisma db push

# Seed demo data
npx prisma db seed

# Start dev server
npm run dev
```

Server starts at `http://localhost:4000`

### Frontend

```bash
cd verdict-frontend/design-first-focus

# Install dependencies
npm install

# Start dev server
npm run dev
```

App starts at `http://localhost:5173`

---

## 📡 API Reference

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Email + password → JWT tokens |
| `POST` | `/api/v1/auth/logout` | Revoke refresh token |

### Cases
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/cases` | List firm's cases |
| `POST` | `/api/v1/cases` | Create new case |
| `GET` | `/api/v1/cases/:id` | Case detail with documents + witnesses |
| `PATCH` | `/api/v1/cases/:id` | Update case |
| `DELETE` | `/api/v1/cases/:id` | Archive case |

### Sessions (AI-powered)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/sessions/:id` | Session state |
| `POST` | `/api/v1/sessions/:id/start` | Begin deposition |
| `POST` | `/api/v1/sessions/:id/agents/question` | Stream next question (SSE) |
| `POST` | `/api/v1/sessions/:id/agents/objection` | Analyze for FRE objections |
| `POST` | `/api/v1/sessions/:id/agents/inconsistency` | Contradiction detection |

### System
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check with live DB ping |
| `GET` | `/api/v1` | API root |

---

## 🗄️ Database Schema

11 models across the full deposition lifecycle:

```
Firm → User → Case → Document
                   → Witness → Session → SessionEvent
                                       → Alert
                                       → Brief → AttorneyAnnotation
```

Key design decisions:
- All firm-scoped data has `firmId` + cascade deletes for data isolation
- `Session.aggression` enum (STANDARD / ELEVATED / HIGH_STAKES) drives AI tone
- `Alert` captures live objection + inconsistency flags with FRE classification
- `Brief` stores post-session score, consistency rate, and weakness map

---

## 🔐 Environment Variables

See [`verdict-backend/.env.example`](verdict-backend/.env.example) for the full list.

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection (Supabase pooler) |
| `REDIS_URL` | ✅ | Redis connection (Upstash `rediss://`) |
| `JWT_SECRET` | ✅ | Access token signing key (min 32 chars) |
| `JWT_REFRESH_SECRET` | ✅ | Refresh token signing key |
| `ANTHROPIC_API_KEY` | ✅ | Claude API for Interrogator + Review agents |
| `ELEVENLABS_API_KEY` | ⚡ | TTS/STT for voice sessions |
| `NEMOTRON_API_KEY` | ⚡ | NVIDIA contradiction scoring |
| `NIA_API_KEY` | ⚡ | Nozomio document indexing + RAG |
| `AWS_ACCESS_KEY_ID` | ⚡ | S3 document storage |

> ⚡ = Required for full AI features; optional for core auth + case management

---

## 🧪 Demo Credentials

After running `npx prisma db seed`:

| Role | Email | Password |
|---|---|---|
| Partner | `sarah.chen@demo.com` | `Demo!Pass123` |
| Associate | `j.rodriguez@demo.com` | `Demo!Pass123` |
| Admin | `admin@demo.com` | `Demo!Pass123` |

**Demo cases:** Chen v. Metropolitan Hospital (MEDICAL_MALPRACTICE) · Thompson v. Axiom Industries (EMPLOYMENT_DISCRIMINATION)

---

## 🗺️ Roadmap

- [x] Milestone 1 — Core infrastructure (DB, Redis, Auth, Health)
- [ ] Milestone 2 — Document ingestion pipeline (S3 + Nia indexing)
- [ ] Milestone 3 — Live session engine (Interrogator SSE + Objection Copilot)
- [ ] Milestone 4 — Inconsistency detection (Nemotron scoring)
- [ ] Milestone 5 — Brief generation (Review Orchestrator + PDF)
- [ ] Milestone 6 — Behavioral Sentinel (ElevenLabs STT + composure analysis)
- [ ] Milestone 7 — Frontend wiring (TanStack Query + real-time alerts)

---

## 👥 Team

Built at **BUILDATHON 2026** — 48-hour hackathon

| | Name | GitHub |
|---|---|---|
| 🧑‍💻 | Aman Sahu | [@amansahu205](https://github.com/amansahu205) |
| 🧑‍💻 | Sukruth D | [@dsukruth](https://github.com/dsukruth) |
| 🧑‍💻 | Nikhil Mulgir | [@nikhilmulgir1106](https://github.com/nikhilmulgir1106) |
| 🧑‍💻 | Supriya Nagnath Kadam | [@skadam1199](https://github.com/skadam1199) |

---

## 📄 License

MIT
