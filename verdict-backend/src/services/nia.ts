/**
 * Nia API — document indexing & RAG search (ref: IMPLEMENTATION_PLAN Step 2.2, BACKEND_STRUCTURE)
 */
import axios from 'axios';

const nia = axios.create({
  baseURL: process.env.NIA_BASE_URL,
  headers: { Authorization: `Bearer ${process.env.NIA_API_KEY}` },
  timeout: 10_000,
});

export async function indexDocument(params: {
  indexId: string;
  documentId: string;
  content: string;
  metadata?: Record<string, unknown>;
}) {
  const { data } = await nia.post('/index', params);
  return data;
}

export async function searchIndex(params: {
  indexId: string;
  query: string;
  topK?: number;
  filters?: Record<string, unknown>;
}): Promise<Array<{ id: string; content: string; score: number; metadata?: Record<string, unknown> }>> {
  const { data } = await nia.post('/search', {
    ...params,
    topK: params.topK ?? 5,
  });
  return data.results ?? [];
}
