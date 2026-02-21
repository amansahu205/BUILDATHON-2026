# VERDICT Backend

AI-powered deposition coaching API — Fastify + Prisma + AI agents.

## Structure

```
src/
├── routes/        # auth, cases, sessions, briefs
├── agents/        # interrogator, objection, detector
├── services/      # claude, elevenlabs, nia, nemotron
├── middleware/    # auth, rate-limit, error
├── lib/           # db (Prisma)
└── index.ts       # Fastify entry
prisma/
└── schema.prisma
```

## Docs (reference)

All product and API specs live in the parent `docs/` folder:

- **BACKEND_STRUCTURE.md** — API endpoints, schema, validation, errors
- **TECH_STACK.md** — Dependencies, env vars, Prisma schema details
- **IMPLEMENTATION_PLAN.md** — Phases, agents, integration steps
- **APP_FLOW.md** — User flows, screens

From repo root: `../docs/` or `docs/` if you symlink/copy.

## Setup

```bash
cp .env.example .env
# Edit .env with DATABASE_URL, JWT secrets, API keys

npm install
npx prisma generate
npx prisma migrate dev --name init
npm run dev
```

Health: `GET http://localhost:4000/api/v1/health`

## Scripts

| Command | Description |
|--------|-------------|
| `npm run dev` | Start with tsx watch |
| `npm run build` | Compile to dist/ |
| `npm run start` | Run dist/index.js |
| `npm run db:migrate` | Prisma migrate dev |
| `npm run db:studio` | Open Prisma Studio |
