import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { db } from '../lib/db.js';
import { requireAuth } from '../middleware/auth.js';

export async function briefsRoutes(app: FastifyInstance) {
  app.get<{ Params: { briefId: string } }>(
    '/:briefId',
    { preHandler: [requireAuth] },
    async (request, reply) => {
      const user = request.user!;
      const { briefId } = request.params;
      const brief = await db.brief.findFirst({
        where: { id: briefId, firmId: user.firmId },
      });
      if (!brief)
        return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });

      return reply.send({
        success: true,
        data: {
          id: brief.id,
          sessionScore: brief.sessionScore,
          consistencyRate: brief.consistencyRate,
          deltaVsBaseline: brief.deltaVsBaseline,
          confirmedFlags: brief.confirmedFlags,
          objectionCount: brief.objectionCount,
          composureAlerts: brief.composureAlerts,
          topRecommendations: brief.topRecommendations,
          narrativeText: brief.narrativeText,
          weaknessMapScores: brief.weaknessMapScores,
          shareToken: brief.shareToken,
          pdfS3Key: brief.pdfS3Key,
          createdAt: brief.createdAt,
        },
      });
    }
  );

  // Public share endpoint — no auth required
  app.get<{ Params: { shareToken: string } }>(
    '/share/:shareToken',
    async (request, reply) => {
      const { shareToken } = request.params;
      const brief = await db.brief.findFirst({
        where: { shareToken },
      });
      if (!brief)
        return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });
      if (brief.shareTokenExpiresAt && brief.shareTokenExpiresAt < new Date())
        return reply.code(410).send({ success: false, error: { code: 'SHARE_LINK_EXPIRED', statusCode: 410 } });

      return reply.send({
        success: true,
        data: {
          sessionScore: brief.sessionScore,
          consistencyRate: brief.consistencyRate,
          topRecommendations: brief.topRecommendations,
          narrativeText: brief.narrativeText,
        },
      });
    }
  );
}
