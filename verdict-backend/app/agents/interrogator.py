from typing import AsyncGenerator

from app.services.claude import claude_stream
from app.services.databricks_vector import search_prior_statements
from .models import VerdictCase

_INTERROGATOR_SYSTEM = """You are an elite deposition attorney conducting a high-stakes mock deposition.
Your sole job is to generate ONE sharp, focused deposition question to ask the witness right now.

Rules:
- Output ONLY the question text — no preamble, no JSON, no labels, no quotes around it.
- The question must be a single, non-compound question (one fact per question).
- Use the case facts, prior statements, and exhibits provided to trap the witness in contradictions.
- Calibrate aggression to the instruction given.
- Questions should reference specific exhibits, dates, or quotes when available.
- Never ask two things at once."""


async def generate_question(
    case: VerdictCase,
    current_topic: str,
    question_number: int,
    prior_answer: str | None = None,
    hesitation_detected: bool = False,
    recent_inconsistency_flag: bool = False,
    prior_weak_areas: list[str] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream the next deposition question token-by-token."""
    system_prompt = _INTERROGATOR_SYSTEM

    prior_context: list[dict] = []
    if prior_answer:
        prior_context = await search_prior_statements(
            case_id=case.id,
            query=prior_answer,
            top_k=3,
        )

    aggression_instructions = {
        "STANDARD":    "Ask methodically. Allow witness to elaborate.",
        "ELEVATED":    "Press on contradictions. Use controlled silence.",
        "HIGH_STAKES": "Maximum pressure. Expose inconsistencies directly. Demand specifics.",
        "Low":         "Ask methodically. Allow witness to elaborate.",
        "Medium":      "Press on contradictions. Use controlled silence.",
        "High":        "Maximum pressure. Expose inconsistencies directly. Demand specifics.",
    }.get(case.aggression_level, "Ask methodically.")

    prior_lines = ""
    if prior_context:
        prior_lines = "Relevant prior sworn statements:\n" + "\n".join(
            f'- "{r.get("content", "")}"' for r in prior_context
        )

    user_message = f"""CASE: {case.case_name} ({case.case_type})
WITNESS: {case.witness_name} — {case.witness_role}
OPPOSING PARTY: {case.opposing_party}
KEY FACTS: {case.extracted_facts[:600] if case.extracted_facts else 'N/A'}
PRIOR STATEMENTS TO CHALLENGE: {case.prior_statements[:400] if case.prior_statements else 'N/A'}
EXHIBITS: {case.exhibit_list[:300] if case.exhibit_list else 'N/A'}
FOCUS AREAS: {case.focus_areas}

Current focus topic: {current_topic}
Question number: {question_number}
{f'Witness last answered: "{prior_answer}"' if prior_answer else 'First question on this topic.'}
{'⚠️ Witness hesitated significantly before answering.' if hesitation_detected else ''}
{'🚨 Inconsistency detected in last answer — probe harder.' if recent_inconsistency_flag else ''}
{prior_lines}
Prior weak areas: {', '.join(prior_weak_areas) if prior_weak_areas else 'None (first session)'}
Aggression instruction: {aggression_instructions}

Generate the next deposition question:""".strip()

    async for chunk in claude_stream(system_prompt, user_message, max_tokens=200):
        yield chunk
