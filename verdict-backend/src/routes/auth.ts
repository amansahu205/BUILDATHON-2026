import type { FastifyInstance, FastifyRequest, FastifyReply } from 'fastify';
import { z } from 'zod';
import { db } from '../lib/db.js';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { nanoid } from 'nanoid';
import { requireAuth } from '../middleware/auth.js';

const loginBody = z.object({
  email: z.string().email().max(255).toLowerCase().trim(),
  password: z.string().min(1).max(128),
});

export async function authRoutes(app: FastifyInstance) {
  app.post('/login', async (request: FastifyRequest, reply: FastifyReply) => {
    const parsed = loginBody.safeParse(request.body);
    if (!parsed.success) {
      return reply.code(400).send({
        success: false,
        error: { code: 'VALIDATION_ERROR', message: 'Invalid body', details: parsed.error.flatten() },
      });
    }
    const { email, password } = parsed.data;

    const user = await db.user.findUnique({
      where: { email },
      include: { firm: { select: { id: true } } },
    });
    if (!user || !user.passwordHash) {
      return reply.code(401).send({
        success: false,
        error: { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password', statusCode: 401 },
      });
    }
    if (!user.isActive) {
      return reply.code(403).send({
        success: false,
        error: { code: 'ACCOUNT_INACTIVE', message: 'Account inactive', statusCode: 403 },
      });
    }

    const valid = await bcrypt.compare(password, user.passwordHash);
    if (!valid) {
      await db.user.update({
        where: { id: user.id },
        data: { loginAttempts: { increment: 1 } },
      });
      return reply.code(401).send({
        success: false,
        error: { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password', statusCode: 401 },
      });
    }

    const secret = process.env.JWT_SECRET ?? '';
    const refreshSecret = process.env.JWT_REFRESH_SECRET ?? '';
    const accessToken = jwt.sign(
      { sub: user.id, firmId: user.firmId, role: user.role, email: user.email },
      secret,
      { expiresIn: 8 * 60 * 60 } // 8h in seconds
    );
    const jti = nanoid(16);
    const refreshToken = jwt.sign(
      { sub: user.id, firmId: user.firmId, jti },
      refreshSecret,
      { expiresIn: 30 * 24 * 60 * 60 } // 30d in seconds
    );

    const crypto = await import('crypto');
    const tokenHash = crypto.createHash('sha256').update(refreshToken).digest('hex');
    await db.refreshToken.create({
      data: {
        userId: user.id,
        tokenHash,
        expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
      },
    });

    await db.user.update({
      where: { id: user.id },
      data: { lastLoginAt: new Date(), loginAttempts: 0 },
    });

    return reply.send({
      success: true,
      data: {
        user: {
          id: user.id,
          firmId: user.firmId,
          email: user.email,
          name: user.name,
          role: user.role,
        },
        accessToken,
        refreshToken,
      },
    });
  });

  app.post('/logout', { preHandler: [requireAuth] }, async (request: FastifyRequest, reply: FastifyReply) => {
    // In full impl: revoke refresh token from body/cookie
    return reply.send({ success: true, message: 'Logged out successfully' });
  });
}
