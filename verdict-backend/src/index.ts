/**
 * VERDICT API — Fastify entry point
 * Ref: ../docs/BACKEND_STRUCTURE.md, TECH_STACK.md
 */
import 'dotenv/config';
import Fastify from 'fastify';
import cors from '@fastify/cors';
import rateLimit from '@fastify/rate-limit';
import { db } from './lib/db.js';
import { errorHandler } from './middleware/error.js';
import { authRoutes } from './routes/auth.js';
import { casesRoutes } from './routes/cases.js';
import { sessionsRoutes } from './routes/sessions.js';
import { briefsRoutes } from './routes/briefs.js';

const app = Fastify({
  logger: true,
  requestIdHeader: 'x-request-id',
  genReqId: () => `req_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
});

// ── CORS ──────────────────────────────────────────────────────────────────────
await app.register(cors, {
  origin: process.env.FRONTEND_URL ?? '*',
  credentials: true,
  methods: ['GET', 'POST', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'x-request-id'],
});

// ── Rate limit ────────────────────────────────────────────────────────────────
await app.register(rateLimit, {
  max: 100,
  timeWindow: '1 minute',
});

// ── Error handler ─────────────────────────────────────────────────────────────
app.setErrorHandler(errorHandler);

// ── System routes ─────────────────────────────────────────────────────────────
app.get('/api/v1', async () => ({
  message: 'VERDICT API',
  version: 'v1',
  docs: '/api/v1/health',
}));

app.get('/api/v1/health', async (_request, reply) => {
  try {
    await db.$queryRaw`SELECT 1`;
    return reply.send({
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      db: 'connected',
    });
  } catch {
    return reply.code(503).send({
      status: 'degraded',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      db: 'disconnected',
    });
  }
});

// ── API routes ────────────────────────────────────────────────────────────────
await app.register(authRoutes,    { prefix: '/api/v1/auth' });
await app.register(casesRoutes,   { prefix: '/api/v1/cases' });
await app.register(sessionsRoutes,{ prefix: '/api/v1/sessions' });
await app.register(briefsRoutes,  { prefix: '/api/v1/briefs' });

// ── Start ─────────────────────────────────────────────────────────────────────
const port = parseInt(process.env.PORT ?? '4000', 10);
const host = process.env.HOST ?? '0.0.0.0';

const start = async () => {
  try {
    await app.listen({ port, host });
    app.log.info(`VERDICT API listening on http://${host}:${port}`);
  } catch (err) {
    app.log.error(err);
    process.exit(1);
  }
};

// ── Graceful shutdown ─────────────────────────────────────────────────────────
const shutdown = async (signal: string) => {
  app.log.info(`${signal} received — shutting down gracefully`);
  await app.close();
  await db.$disconnect();
  process.exit(0);
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT',  () => shutdown('SIGINT'));

start();
