from typing import AsyncGenerator

from app.services.claude import claude_stream
from app.services.nia import search_index
from .prompt import build_system_prompt
from .models import VerdictCase


async def generate_question(
    case: VerdictCase,
    current_topic: str,
    nia_session_context_id: str,
    question_number: int,
    prior_answer: str = None,
    hesitation_detected: bool = False,
    recent_inconsistency_flag: bool = False,
    prior_weak_areas: list[str] = None,
) -> AsyncGenerator[str, None]:

    system_prompt = build_system_prompt(case)

    nia_context = []
    if prior_answer:
        nia_context = await search_index(
            index_id=nia_session_context_id,
            query=prior_answer,
            top_k=3,
        )

    aggression_instructions = {
        "STANDARD": "Ask methodically. Allow witness to elaborate.",
        "ELEVATED": "Press on contradictions. Use controlled silence.",
        "HIGH_STAKES": "Maximum pressure. Expose inconsistencies directly. Demand specifics.",
        "Low": "Ask methodically. Allow witness to elaborate.",
        "Medium": "Press on contradictions. Use controlled silence.",
        "High": "Maximum pressure. Expose inconsistencies directly. Demand specifics.",
    }.get(case.aggression_level, "Ask methodically.")

    nia_lines = ""
    if nia_context:
        nia_lines = "Relevant prior sworn statements:\n" + "\n".join(
            f'- "{r.get("content", "")}"' for r in nia_context
        )

    user_message = f"""Case type: {case.case_type}
Witness role: {case.witness_role}
Current focus topic: {current_topic}
Question number: {question_number}
{f'Witness last answered: "{prior_answer}"' if prior_answer else 'First question on this topic.'}
{'⚠️ Witness hesitated significantly before answering.' if hesitation_detected else ''}
{'🚨 Inconsistency detected in last answer — probe harder.' if recent_inconsistency_flag else ''}
{nia_lines}
Prior weak areas: {', '.join(prior_weak_areas) if prior_weak_areas else 'None (first session)'}
Aggression instruction: {aggression_instructions}

Generate the next deposition question:""".strip()

    async for chunk in claude_stream(system_prompt, user_message, max_tokens=200):
        yield chunk
