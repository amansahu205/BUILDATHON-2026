import json
from app.services.databricks_vector import search_prior_statements
from app.services.nemotron import score_contradiction
from app.services.claude import claude_chat

CONFIDENCE_THRESHOLD_LIVE = 0.75
CONFIDENCE_THRESHOLD_SECONDARY = 0.5
CONFIDENCE_THRESHOLD_CLAUDE_FALLBACK = 0.85

_EMPTY_RESULT = {
    "flagFound": False,
    "isLiveFired": False,
    "contradictionConfidence": 0,
    "priorQuote": None,
    "priorDocumentPage": None,
    "priorDocumentLine": None,
    "impeachmentRisk": "LOW",
}


async def detect_inconsistency(
    question_text: str,
    answer_text: str,
    session_id: str,
    case_id: str,          # used to filter Databricks prior_statements_index by case
    case_type: str,
) -> dict:
    # Pull the top-5 semantically similar prior statements for this case.
    prior_statements = await search_prior_statements(
        case_id=case_id,
        query=answer_text,
        top_k=5,
    )

    if not prior_statements:
        return _EMPTY_RESULT

    using_fallback = False
    try:
        score = await score_contradiction(
            witness_answer=answer_text,
            prior_statements=prior_statements,
            case_context=f"{case_type} deposition",
        )
    except Exception:
        # Nemotron unavailable — fall back to Claude with a raised threshold
        # (PRD §5.4 graceful degradation).
        using_fallback = True
        result = await claude_chat(
            'Score contradiction confidence 0-1. Return only JSON: {"contradiction_confidence": number, "best_match_index": number}',
            f'Answer: "{answer_text}"\nPrior:\n' + "\n".join(
                f"[{i}] {s.get('content', '')}" for i, s in enumerate(prior_statements)
            ),
        )
        score = json.loads(result)

    threshold = CONFIDENCE_THRESHOLD_CLAUDE_FALLBACK if using_fallback else CONFIDENCE_THRESHOLD_LIVE
    confidence = score.get("contradiction_confidence", 0)
    best_idx = score.get("best_match_index", -1)
    best_match = prior_statements[best_idx] if 0 <= best_idx < len(prior_statements) else None

    if confidence < CONFIDENCE_THRESHOLD_SECONDARY:
        return _EMPTY_RESULT

    return {
        "flagFound": True,
        "isLiveFired": confidence >= threshold,
        "contradictionConfidence": confidence,
        "priorQuote": best_match.get("content") if best_match else None,
        "priorDocumentPage": best_match.get("page") if best_match else None,
        "priorDocumentLine": best_match.get("line") if best_match else None,
        "impeachmentRisk": "HIGH" if confidence >= threshold else "MEDIUM",
    }
