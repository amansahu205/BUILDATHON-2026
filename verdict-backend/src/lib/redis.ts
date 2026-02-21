import { Redis } from 'ioredis';

if (!process.env.REDIS_URL) {
  throw new Error('REDIS_URL environment variable is required');
}

export const redis = new Redis(process.env.REDIS_URL, {
  maxRetriesPerRequest: 3,
  enableReadyCheck: true,
  reconnectOnError: (err) => {
    console.error('Redis reconnect on error:', err.message);
    return true;
  },
});

redis.on('connect', () => console.log('✅ Redis connected'));
redis.on('error',   (err) => console.error('❌ Redis error:', err));
