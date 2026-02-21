/**
 * NVIDIA Nemotron — contradiction scoring (ref: IMPLEMENTATION_PLAN Step 3.1, TECH_STACK §4)
 */
import axios from 'axios';

const nemotron = axios.create({
  baseURL: process.env.NEMOTRON_BASE_URL ?? 'https://integrate.api.nvidia.com/v1',
  headers: { Authorization: `Bearer ${process.env.NEMOTRON_API_KEY}` },
  timeout: parseInt(process.env.NEMOTRON_TIMEOUT_MS ?? '5000', 10),
});

export async function scoreContradiction(params: {
  witnessAnswer: string;
  priorStatements: Array<{ content: string; metadata?: Record<string, unknown> }>;
  caseContext: string;
}): Promise<{
  contradiction_confidence: number;
  best_match_index: number;
  reasoning?: string;
}> {
  const prompt = `You are analyzing a witness deposition for contradictions.

Case context: ${params.caseContext}

Witness answer just given:
"${params.witnessAnswer}"

Prior sworn statements on record:
${params.priorStatements.map((s, i) => `[${i}] "${s.content}"`).join('\n')}

Analyze whether the witness answer contradicts any prior statement.
Respond ONLY with JSON:
{
  "contradiction_confidence": <float 0.0-1.0>,
  "best_match_index": <integer index of most contradicted statement, or -1>,
  "reasoning": "<one sentence explanation>"
}`;

  const { data } = await nemotron.post('/chat/completions', {
    model: process.env.NEMOTRON_MODEL ?? 'nvidia/llama-3.1-nemotron-ultra-253b-v1',
    messages: [{ role: 'user', content: prompt }],
    max_tokens: 200,
    temperature: 0.1,
  });

  const text = data.choices?.[0]?.message?.content ?? '{}';
  return JSON.parse(text);
}
