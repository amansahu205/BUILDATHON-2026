from typing import AsyncGenerator

from app.services.claude import claude_stream
from app.services.databricks_vector import search_prior_statements
from .prompt import build_system_prompt
from .models import VerdictCase


async def generate_question(
    case: VerdictCase,
    current_topic: str,
    question_number: int,
    prior_answer: str | None = None,
    hesitation_detected: bool = False,
    recent_inconsistency_flag: bool = False,
    prior_weak_areas: list[str] | None = None,
) -> AsyncGenerator[str, None]:
    """Stream the next deposition question token-by-token.

    Prior sworn statements are retrieved from Databricks filtered by case.id
    so we always query the right case's indexed documents.
    """
    system_prompt = build_system_prompt(case)

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

    user_message = f"""Case type: {case.case_type}
Witness role: {case.witness_role}
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
