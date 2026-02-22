from pydantic import BaseModel
from typing import Optional


class CreateSessionRequest(BaseModel):
    durationMinutes: int
    focusAreas: list[str]
    aggression: str = "STANDARD"
    objectionCopilotEnabled: bool = True
    sentinelEnabled: bool = False


class QuestionRequest(BaseModel):
    questionNumber: int = 1
    priorAnswer: Optional[str] = None
    hesitationDetected: bool = False
    recentInconsistencyFlag: bool = False
    currentTopic: str = "PRIOR_STATEMENTS"


class ObjectionRequest(BaseModel):
    questionNumber: int
    questionText: str


class InconsistencyRequest(BaseModel):
    questionNumber: int
    questionText: str
    answerText: str
