import type { FastifyError, FastifyRequest, FastifyReply } from 'fastify';
import { ZodError } from 'zod';

export function errorHandler(
  error: FastifyError,
  request: FastifyRequest,
  reply: FastifyReply
) {
  const requestId = request.id;

  request.log.error({ err: error, requestId }, 'Request error');

  if (error instanceof ZodError) {
    return reply.code(400).send({
      success: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Request validation failed',
        statusCode: 400,
        details: error.flatten().fieldErrors,
        requestId,
        timestamp: new Date().toISOString(),
      },
    });
  }

  const statusCode = error.statusCode ?? 500;
  const code = (error as FastifyError & { code?: string }).code ?? 'INTERNAL_ERROR';

  return reply.code(statusCode).send({
    success: false,
    error: {
      code,
      message: statusCode >= 500 ? 'An unexpected error occurred.' : error.message,
      statusCode,
      requestId,
      timestamp: new Date().toISOString(),
    },
  });
}
