from typing import Literal

from pydantic import BaseModel, Field


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
    aggression_level: Literal["Low", "Medium", "High"]


class CaseCreate(BaseModel):
    """Body for creating a new case. ID is auto-generated if omitted."""

    id: str | None = None
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
    aggression_level: Literal["Low", "Medium", "High"]


class CaseUpdate(BaseModel):
    """Partial update — every field is optional."""

    case_name: str | None = None
    case_type: str | None = None
    opposing_party: str | None = None
    deposition_date: str | None = None
    witness_name: str | None = None
    witness_role: str | None = None
    extracted_facts: str | None = None
    prior_statements: str | None = None
    exhibit_list: str | None = None
    focus_areas: str | None = None
    aggression_level: Literal["Low", "Medium", "High"] | None = None


class SessionRequest(BaseModel):
    """Request to start a deposition session for a given case."""

    case_id: str


class SessionResponse(BaseModel):
    """Signed conversation token + metadata returned to the frontend."""

    conversation_token: str
    agent_id: str
    case_id: str
    case_name: str
    witness_name: str
    conversation_config_override: dict | None = None


class ConversationSummary(BaseModel):
    conversation_id: str
    agent_id: str | None = None
    status: str | None = None
    start_time: str | None = None
    end_time: str | None = None
    metadata: dict | None = None


class ConversationDetail(BaseModel):
    conversation_id: str
    agent_id: str | None = None
    status: str | None = None
    transcript: list[dict] = Field(default_factory=list)
    metadata: dict | None = None
    analysis: dict | None = None


class ReportRequest(BaseModel):
    """Request to generate a deposition report."""

    conversation_id: str | None = None
    case_id: str | None = None
    transcript: str | None = None
    witness_name: str | None = None
    aggression_level: str | None = None


class ReportSummary(BaseModel):
    report_id: str
    case_name: str
    witness_name: str
    overall_score: int
    overall_rating: str
    generated_at: str


class HealthResponse(BaseModel):
    status: str = "ok"
    agent_id: str
    cases_loaded: int
