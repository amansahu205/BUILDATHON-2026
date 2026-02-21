/**
 * Inconsistency Detector — Nemotron scoring, Nia prior statements (ref: IMPLEMENTATION_PLAN Step 3.1)
 */
import { searchIndex } from '../services/nia.js';
import { scoreContradiction } from '../services/nemotron.js';
import { claudeChat } from '../services/claude.js';

const CONFIDENCE_THRESHOLD_LIVE = 0.75;
const CONFIDENCE_THRESHOLD_SECONDARY = 0.5;
const CONFIDENCE_THRESHOLD_CLAUDE_FALLBACK = 0.85;

export async function detectInconsistency(params: {
  questionText: string;
  answerText: string;
  sessionId: string;
  niaSessionContextId: string;
  caseType: string;
}): Promise<{
  flagFound: boolean;
  isLiveFired: boolean;
  contradictionConfidence: number;
  priorQuote: string | null;
  priorDocumentPage: number | null;
  priorDocumentLine: number | null;
  impeachmentRisk: 'STANDARD' | 'HIGH';
}> {
  const priorStatements = await searchIndex({
    indexId: params.niaSessionContextId,
    query: params.answerText,
    topK: 5,
  }).then((r) => r.map((x) => ({ content: x.content, metadata: x.metadata ?? {} })));

  if (priorStatements.length === 0) {
    return {
      flagFound: false,
      isLiveFired: false,
      contradictionConfidence: 0,
      priorQuote: null,
      priorDocumentPage: null,
      priorDocumentLine: null,
      impeachmentRisk: 'STANDARD',
    };
  }

  let score: { contradiction_confidence: number; best_match_index: number };
  let usingFallback = false;

  try {
    score = await scoreContradiction({
      witnessAnswer: params.answerText,
      priorStatements,
      caseContext: `${params.caseType} deposition`,
    });
  } catch {
    usingFallback = true;
    const claudeResult = await claudeChat(
      'Score contradiction confidence 0-1. Return only JSON: {"contradiction_confidence": number, "best_match_index": number}',
      `Answer: "${params.answerText}"\nPrior statements:\n${priorStatements.map((s, i) => `[${i}] ${s.content}`).join('\n')}`
    );
    score = JSON.parse(claudeResult);
  }

  const threshold = usingFallback ? CONFIDENCE_THRESHOLD_CLAUDE_FALLBACK : CONFIDENCE_THRESHOLD_LIVE;
  const confidence = score.contradiction_confidence;
  const bestMatch = priorStatements[score.best_match_index];

  if (confidence < CONFIDENCE_THRESHOLD_SECONDARY) {
    return {
      flagFound: false,
      isLiveFired: false,
      contradictionConfidence: confidence,
      priorQuote: null,
      priorDocumentPage: null,
      priorDocumentLine: null,
      impeachmentRisk: 'STANDARD',
    };
  }

  const isLiveFired = confidence >= threshold;

  return {
    flagFound: true,
    isLiveFired,
    contradictionConfidence: confidence,
    priorQuote: bestMatch?.content ?? null,
    priorDocumentPage: (bestMatch?.metadata?.page as number) ?? null,
    priorDocumentLine: (bestMatch?.metadata?.line as number) ?? null,
    impeachmentRisk: 'STANDARD',
  };
}
