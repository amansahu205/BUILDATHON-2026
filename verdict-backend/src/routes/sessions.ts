import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import { db } from '../lib/db.js';
import { requireAuth } from '../middleware/auth.js';
import { generateQuestion } from '../agents/interrogator.js';
import { analyzeForObjections } from '../agents/objection.js';
import { detectInconsistency } from '../agents/detector.js';

const createSessionBody = z.object({
  durationMinutes: z.union([z.literal(15), z.literal(30), z.literal(45), z.literal(60)]),
  focusAreas: z.array(z.string()).min(1).max(6),
  aggression: z.enum(['STANDARD', 'ELEVATED', 'HIGH_STAKES']),
  objectionCopilotEnabled: z.boolean(),
  sentinelEnabled: z.boolean(),
});

export async function sessionsRoutes(app: FastifyInstance) {
  app.get<{ Params: { sessionId: string } }>(
    '/:sessionId',
    { preHandler: [requireAuth] },
    async (request, reply) => {
      const user = request.user!;
      const { sessionId } = request.params;
      const session = await db.session.findFirst({
        where: { id: sessionId, firmId: user.firmId },
      });
      if (!session)
        return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });
      return reply.send({
        success: true,
        data: {
          id: session.id,
          status: session.status,
          sessionNumber: session.sessionNumber,
          durationMinutes: session.durationMinutes,
          startedAt: session.startedAt,
          questionCount: session.questionCount,
        },
      });
    }
  );

  app.post<{ Params: { sessionId: string } }>(
    '/:sessionId/start',
    { preHandler: [requireAuth] },
    async (request, reply) => {
      const user = request.user!;
      const { sessionId } = request.params;
      const session = await db.session.findFirst({
        where: { id: sessionId, firmId: user.firmId },
      });
      if (!session)
        return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });
      await db.session.update({
        where: { id: sessionId },
        data: { status: 'ACTIVE', startedAt: new Date() },
      });
      return reply.send({
        success: true,
        data: { sessionId, status: 'ACTIVE', startedAt: new Date().toISOString() },
      });
    }
  );

  app.post<{ Params: { sessionId: string } }>(
    '/:sessionId/agents/question',
    { preHandler: [requireAuth] },
    async (request, reply) => {
      const user = request.user!;
      const { sessionId } = request.params;
      const body = request.body as {
        questionNumber: number;
        priorAnswer?: string;
        hesitationDetected?: boolean;
        recentInconsistencyFlag?: boolean;
        currentTopic?: string;
      };
      const session = await db.session.findFirst({
        where: { id: sessionId, firmId: user.firmId },
        include: { case: true },
      });
      if (!session)
        return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });

      reply.raw.setHeader('Content-Type', 'text/event-stream');
      reply.raw.setHeader('Cache-Control', 'no-cache');
      reply.raw.setHeader('Connection', 'keep-alive');
      let fullText = '';
      try {
        reply.raw.write(
          `data: ${JSON.stringify({ type: 'QUESTION_START', questionNumber: body.questionNumber ?? 1 })}\n\n`
        );
        const stream = generateQuestion({
          caseType: session.case.caseType,
          witnessRole: 'DEFENDANT',
          currentTopic: body.currentTopic ?? 'PRIOR_STATEMENTS',
          aggressionLevel: (session.aggression as 'STANDARD' | 'ELEVATED' | 'HIGH_STAKES') ?? 'STANDARD',
          priorAnswer: body.priorAnswer,
          questionNumber: body.questionNumber ?? 1,
          hesitationDetected: body.hesitationDetected ?? false,
          recentInconsistencyFlag: body.recentInconsistencyFlag ?? false,
          niaSessionContextId: session.niaSessionContextId ?? session.id,
          priorWeakAreas: [],
        });
        for await (const chunk of stream) {
          fullText += chunk;
          reply.raw.write(`data: ${JSON.stringify({ type: 'QUESTION_CHUNK', text: chunk })}\n\n`);
        }
        reply.raw.write(
          `data: ${JSON.stringify({ type: 'QUESTION_END', fullText, latencyMs: 0 })}\n\n`
        );
      } finally {
        reply.raw.end();
      }
    }
  );

  app.post<{ Params: { sessionId: string } }>(
    '/:sessionId/agents/objection',
    { preHandler: [requireAuth] },
    async (request, reply) => {
      const user = request.user!;
      const { sessionId } = request.params;
      const body = request.body as { questionNumber: number; questionText: string };
      const session = await db.session.findFirst({
        where: { id: sessionId, firmId: user.firmId },
      });
      if (!session)
        return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });
      const start = Date.now();
      const result = await analyzeForObjections({
        questionText: body.questionText,
        sessionId,
      });
      const processingMs = Date.now() - start;
      return reply.send({
        success: true,
        data: { ...result, processingMs },
      });
    }
  );

  app.post<{ Params: { sessionId: string } }>(
    '/:sessionId/agents/inconsistency',
    { preHandler: [requireAuth] },
    async (request, reply) => {
      const user = request.user!;
      const { sessionId } = request.params;
      const body = request.body as {
        questionNumber: number;
        questionText: string;
        answerText: string;
      };
      const session = await db.session.findFirst({
        where: { id: sessionId, firmId: user.firmId },
      });
      if (!session)
        return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });
      const result = await detectInconsistency({
        questionText: body.questionText,
        answerText: body.answerText,
        sessionId,
        niaSessionContextId: session.niaSessionContextId ?? session.id,
        caseType: 'MEDICAL_MALPRACTICE',
      });
      return reply.send({ success: true, data: result });
    }
  );
}
