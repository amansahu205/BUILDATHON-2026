import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import { db } from '../lib/db.js';
import { requireAuth } from '../middleware/auth.js';

const createCaseBody = z.object({
  name: z.string().min(3).max(255).trim(),
  caseType: z.enum([
    'MEDICAL_MALPRACTICE',
    'EMPLOYMENT_DISCRIMINATION',
    'COMMERCIAL_DISPUTE',
    'CONTRACT_BREACH',
    'OTHER',
  ]),
  caseTypeCustom: z.string().max(255).optional(),
  opposingFirm: z.string().max(255).optional(),
  depositionDate: z.string().datetime().optional(),
});

export async function casesRoutes(app: FastifyInstance) {
  app.addHook('preHandler', requireAuth);

  app.get('/', async (request: FastifyRequest, reply: FastifyReply) => {
    const user = request.user!;
    const cases = await db.case.findMany({
      where: { firmId: user.firmId, isArchived: false },
      orderBy: { depositionDate: 'asc' },
      include: {
        _count: { select: { documents: true, witnesses: true } },
      },
    });
    return reply.send({
      success: true,
      data: {
        cases: cases.map((c) => {
          const count = (c as { _count: { documents: number; witnesses: number } })._count;
          return {
            id: c.id,
            name: c.name,
            caseType: c.caseType,
            depositionDate: c.depositionDate,
            documentsReady: count?.documents ?? 0,
            documentsTotal: count?.documents ?? 0,
            witnessCount: count?.witnesses ?? 0,
            createdAt: c.createdAt,
          };
        }),
        pagination: { page: 1, limit: 20, total: cases.length },
      },
    });
  });

  app.post('/', async (request: FastifyRequest, reply: FastifyReply) => {
    const user = request.user!;
    const parsed = createCaseBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({
        success: false,
        error: { code: 'VALIDATION_ERROR', message: 'Invalid body', details: parsed.error.flatten() },
      });
    }
    const { name, caseType, caseTypeCustom, opposingFirm, depositionDate } = parsed.data;
    const c = await db.case.create({
      data: {
        firmId: user.firmId,
        ownerId: user.id,
        name,
        caseType,
        caseTypeCustom,
        opposingFirm,
        depositionDate: depositionDate ? new Date(depositionDate) : null,
      },
    });
    return reply.code(201).send({
      success: true,
      data: {
        id: c.id,
        name: c.name,
        caseType: c.caseType,
        depositionDate: c.depositionDate,
        createdAt: c.createdAt,
      },
    });
  });

  app.get<{ Params: { caseId: string } }>('/:caseId', async (request, reply) => {
    const user = request.user!;
    const { caseId } = request.params;
    const c = await db.case.findFirst({
      where: { id: caseId, firmId: user.firmId },
      include: { documents: true, witnesses: true },
    });
    if (!c) return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });
    return reply.send({ success: true, data: c });
  });

  app.patch<{ Params: { caseId: string } }>('/:caseId', async (request, reply) => {
    const user = request.user!;
    const { caseId } = request.params;
    const body = request.body as Record<string, unknown>;
    const existing = await db.case.findFirst({
      where: { id: caseId, firmId: user.firmId },
    });
    if (!existing) return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });
    const updated = await db.case.update({
      where: { id: caseId },
      data: {
        ...(body.name != null && { name: String(body.name) }),
        ...(body.depositionDate != null && { depositionDate: new Date(String(body.depositionDate)) }),
      },
    });
    return reply.send({ success: true, data: updated });
  });

  app.delete<{ Params: { caseId: string } }>('/:caseId', async (request, reply) => {
    const user = request.user!;
    const { caseId } = request.params;
    const existing = await db.case.findFirst({
      where: { id: caseId, firmId: user.firmId },
    });
    if (!existing) return reply.code(404).send({ success: false, error: { code: 'NOT_FOUND', statusCode: 404 } });
    await db.case.update({ where: { id: caseId }, data: { isArchived: true } });
    return reply.send({ success: true, message: 'Case archived' });
  });
}
