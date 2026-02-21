import type { FastifyRequest, FastifyReply } from 'fastify';
import jwt from 'jsonwebtoken';
import { db } from '../lib/db.js';

export interface AuthUser {
  id: string;
  firmId: string;
  role: string;
  isActive: boolean;
}

declare module 'fastify' {
  interface FastifyRequest {
    user?: AuthUser;
  }
}

export async function requireAuth(request: FastifyRequest, reply: FastifyReply) {
  const raw = request.headers.authorization?.replace(/^Bearer\s+/i, '');

  if (!raw) {
    return reply.code(401).send({
      success: false,
      error: { code: 'TOKEN_MISSING', message: 'Authentication required', statusCode: 401 },
    });
  }

  try {
    const payload = jwt.verify(raw, process.env.JWT_SECRET!) as {
      sub: string;
      firmId: string;
      role: string;
    };
    const user = await db.user.findUnique({
      where: { id: payload.sub },
      select: { id: true, firmId: true, role: true, isActive: true },
    });
    if (!user || !user.isActive) {
      return reply.code(403).send({
        success: false,
        error: { code: 'ACCOUNT_INACTIVE', message: 'Account inactive', statusCode: 403 },
      });
    }
    request.user = user as AuthUser;
  } catch {
    return reply.code(401).send({
      success: false,
      error: { code: 'TOKEN_INVALID', message: 'Invalid or expired token', statusCode: 401 },
    });
  }
}
