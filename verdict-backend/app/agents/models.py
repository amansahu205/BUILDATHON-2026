"""
Pydantic models used by the agents layer.

VerdictCase is the runtime data contract passed into prompt builders and
scoring engines. It is populated from the DB (Case + Witness + Session rows)
by the router before calling any agent function.

aggression_level accepts both the main-backend enum values
(STANDARD / ELEVATED / HIGH_STAKES) and the voiceagents values
(Low / Medium / High) — build_system_prompt uses it as a plain string.
"""

from pydantic import BaseModel


class VerdictCase(BaseModel):
    id: str
    case_name: str
    case_type: str
    opposing_party: str
    deposition_date: str
    witness_name: str
    witness_role: str
    extracted_facts: str
    prior_statements: str
    exhibit_list: str
    focus_areas: str
    aggression_level: str  # STANDARD | ELEVATED | HIGH_STAKES (or Low | Medium | High)
