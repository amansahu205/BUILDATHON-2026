from typing import AsyncGenerator
from app.services.claude import claude_stream
from app.services.nia import search_index

INTERROGATOR_SYSTEM = """You are a highly skilled opposing counsel conducting a deposition.
Your goal is to expose inconsistencies in the witness's testimony.
You ask ONE focused question at a time. Questions are precise, legally professional.
You adapt based on the witness's prior answers and detected hesitations.
NEVER ask compound questions. NEVER reveal your strategy.
Format: Return only the question text, no preamble."""


async def generate_question(
    case_type: str,
    witness_role: str,
    current_topic: str,
    aggression_level: str,
    nia_session_context_id: str,
    question_number: int,
    prior_answer: str = None,
    hesitation_detected: bool = False,
    recent_inconsistency_flag: bool = False,
    prior_weak_areas: list[str] = None,
) -> AsyncGenerator[str, None]:

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
    }.get(aggression_level, "Ask methodically.")

    nia_lines = ""
    if nia_context:
        nia_lines = "Relevant prior sworn statements:\n" + "\n".join(
            f'- "{r.get("content", "")}"' for r in nia_context
        )

    user_message = f"""Case type: {case_type}
Witness role: {witness_role}
Current focus topic: {current_topic}
Question number: {question_number}
{f'Witness last answered: "{prior_answer}"' if prior_answer else 'First question on this topic.'}
{'⚠️ Witness hesitated significantly before answering.' if hesitation_detected else ''}
{'🚨 Inconsistency detected in last answer — probe harder.' if recent_inconsistency_flag else ''}
{nia_lines}
Prior weak areas: {', '.join(prior_weak_areas) if prior_weak_areas else 'None (first session)'}
Aggression instruction: {aggression_instructions}

Generate the next deposition question:""".strip()

    async for chunk in claude_stream(INTERROGATOR_SYSTEM, user_message, max_tokens=200):
        yield chunk
