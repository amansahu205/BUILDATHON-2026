import json
from app.services.claude import claude_chat
from app.services.nia import search_index
from app.config import settings

OBJECTION_SYSTEM = """You are an expert attorney specializing in evidence law and Federal Rules of Evidence.
Analyze the given deposition question for objectionable content.
Respond ONLY with valid JSON. No preamble, no markdown.

JSON format:
{
  "isObjectionable": boolean,
  "category": "LEADING" | "HEARSAY" | "COMPOUND" | "ASSUMES_FACTS" | "SPECULATION" | null,
  "freRule": string | null,
  "explanation": string | null,
  "confidence": number
}"""


async def analyze_for_objections(question_text: str, session_id: str) -> dict:
    fre_context = ""
    if settings.NIA_FRE_CORPUS_INDEX_ID:
        fre_results = await search_index(
            index_id=settings.NIA_FRE_CORPUS_INDEX_ID,
            query=question_text,
            top_k=2,
        )
        if fre_results:
            fre_context = "\n".join(r.get("content", "") for r in fre_results)

    prompt = f'Analyze this deposition question for FRE objections:\n\n"{question_text}"'
    if fre_context:
        prompt += f"\n\nRelevant FRE rules:\n{fre_context}"

    raw = await claude_chat(OBJECTION_SYSTEM, prompt, max_tokens=256)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "isObjectionable": False,
            "category": None,
            "freRule": None,
            "explanation": None,
            "confidence": 0.0,
        }
