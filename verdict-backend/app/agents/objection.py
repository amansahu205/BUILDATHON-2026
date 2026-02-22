import json
from app.services.claude import claude_chat
from app.services.databricks_vector import search_fre_rules

OBJECTION_SYSTEM = """You are an expert attorney specializing in evidence law and Federal Rules of Evidence.
Analyze the given deposition question for objectionable content.
Respond ONLY with valid JSON. No preamble, no markdown.

COMPOUND question = any question containing "and", "or", "also", "as well as", "both" that asks about TWO or more distinct facts or actions simultaneously. Flag these as COMPOUND with high confidence.
LEADING question = a question that suggests the answer or assumes a fact not in evidence.
HEARSAY = asks witness to repeat out-of-court statements for their truth.
ASSUMES_FACTS = assumes something not yet established in the record.
SPECULATION = asks witness to guess or speculate about unknown facts.

JSON format:
{
  "isObjectionable": boolean,
  "category": "LEADING" | "HEARSAY" | "COMPOUND" | "ASSUMES_FACTS" | "SPECULATION" | null,
  "freRule": string | null,
  "explanation": string | null,
  "confidence": number
}"""


async def analyze_for_objections(question_text: str, session_id: str) -> dict:
    # Retrieve the top-3 most relevant FRE rules from the Databricks index.
    # Falls back to an empty context string if Databricks is unavailable —
    # Claude can still classify without the retrieved rules.
    fre_results = await search_fre_rules(query=question_text, top_k=3)
    fre_context = "\n".join(r.get("content", "") for r in fre_results)

    prompt = f'Analyze this deposition question for FRE objections:\n\n"{question_text}"'
    if fre_context:
        prompt += f"\n\nRelevant FRE rules:\n{fre_context}"

    raw = await claude_chat(OBJECTION_SYSTEM, prompt, max_tokens=256)
    # Strip markdown code fences if Claude wrapped the JSON
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Last-ditch: find the first { ... } block
        import re
        m = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
        return {
            "isObjectionable": False,
            "category": None,
            "freRule": None,
            "explanation": None,
            "confidence": 0.0,
        }
