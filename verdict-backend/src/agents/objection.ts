/**
 * Objection Copilot — FRE classification ≤1.5s (ref: IMPLEMENTATION_PLAN Step 2.5)
 */
import { claudeChat } from '../services/claude.js';
import { searchIndex } from '../services/nia.js';

const OBJECTION_SYSTEM = `You are an expert attorney specializing in evidence law and Federal Rules of Evidence.
Analyze the given deposition question for objectionable content.
Respond ONLY with valid JSON. No preamble, no markdown.

JSON format:
{
  "isObjectionable": boolean,
  "category": "LEADING" | "HEARSAY" | "COMPOUND" | "ASSUMES_FACTS" | "SPECULATION" | null,
  "freRule": string | null,
  "explanation": string | null,
  "confidence": number
}`;

export async function analyzeForObjections(params: {
  questionText: string;
  sessionId: string;
}): Promise<{
  isObjectionable: boolean;
  category: string | null;
  freRule: string | null;
  explanation: string | null;
  confidence: number;
}> {
  const niaIndexId = process.env.NIA_FRE_CORPUS_INDEX_ID;
  if (niaIndexId) {
    await searchIndex({
      indexId: niaIndexId,
      query: params.questionText,
      topK: 2,
    });
  }

  const raw = await claudeChat(
    OBJECTION_SYSTEM,
    `Analyze this deposition question for FRE objections:\n\n"${params.questionText}"`,
    256
  );
  const result = JSON.parse(raw) as {
    isObjectionable: boolean;
    category: string | null;
    freRule: string | null;
    explanation: string | null;
    confidence: number;
  };
  return result;
}
