/**
 * Interrogator Agent — generates next deposition question (ref: IMPLEMENTATION_PLAN Step 2.3)
 */
import { claudeStream } from '../services/claude.js';
import { searchIndex } from '../services/nia.js';

const INTERROGATOR_SYSTEM = `You are a highly skilled opposing counsel conducting a deposition.
Your goal is to expose inconsistencies in the witness's testimony.
You ask ONE focused question at a time. Questions are precise, legally professional.
You adapt based on the witness's prior answers and detected hesitations.
NEVER ask compound questions. NEVER reveal your strategy.
Format: Return only the question text, no preamble.`;

export async function* generateQuestion(params: {
  caseType: string;
  witnessRole: string;
  currentTopic: string;
  aggressionLevel: 'STANDARD' | 'ELEVATED' | 'HIGH_STAKES';
  priorAnswer?: string;
  questionNumber: number;
  hesitationDetected: boolean;
  recentInconsistencyFlag: boolean;
  niaSessionContextId: string;
  priorWeakAreas?: string[];
}): AsyncGenerator<string> {
  const niaContext = params.priorAnswer
    ? await searchIndex({
        indexId: params.niaSessionContextId,
        query: params.priorAnswer,
        topK: 3,
      })
    : [];

  const aggressionInstructions = {
    STANDARD: 'Ask methodically. Allow witness to elaborate.',
    ELEVATED: 'Press on contradictions. Use controlled silence.',
    HIGH_STAKES: 'Maximum pressure. Expose inconsistencies directly. Demand specifics.',
  }[params.aggressionLevel];

  const userMessage = `
Case type: ${params.caseType}
Witness role: ${params.witnessRole}
Current focus topic: ${params.currentTopic}
Question number: ${params.questionNumber}
${params.priorAnswer ? `Witness last answered: "${params.priorAnswer}"` : 'First question on this topic.'}
${params.hesitationDetected ? '⚠️ Witness hesitated significantly before answering.' : ''}
${params.recentInconsistencyFlag ? '🚨 Inconsistency detected in last answer — probe this area harder.' : ''}
${niaContext.length > 0 ? `Relevant prior sworn statements:\n${niaContext.map((r) => `- "${r.content}"`).join('\n')}` : ''}
Prior weak areas: ${params.priorWeakAreas?.join(', ') ?? 'None (first session)'}
Aggression instruction: ${aggressionInstructions}

Generate the next deposition question:`.trim();

  yield* claudeStream(INTERROGATOR_SYSTEM, userMessage, 200);
}
