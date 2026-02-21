// Route-level rate limit configs (ref: BACKEND_STRUCTURE.md §8)
// Applied via @fastify/rate-limit in index.ts; override per-route in route opts if needed.
export const RATE_LIMITS = {
  authLogin: { max: 10, timeWindow: '1 minute' },
  authRefresh: { max: 30, timeWindow: '1 minute' },
  casesCreate: { max: 10, timeWindow: '1 minute' },
  agentsQuestion: { max: 120, timeWindow: '1 minute' },
  agentsObjection: { max: 120, timeWindow: '1 minute' },
  agentsInconsistency: { max: 60, timeWindow: '1 minute' },
} as const;
