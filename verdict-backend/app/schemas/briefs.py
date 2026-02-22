from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BriefOut(BaseModel):
    id: str
    sessionScore: int
    consistencyRate: float
    deltaVsBaseline: Optional[int] = None
    confirmedFlags: int
    objectionCount: int
    composureAlerts: int
    topRecommendations: list[str]
    narrativeText: str
    weaknessMapScores: Optional[dict] = None
    shareToken: Optional[str] = None
    pdfS3Key: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}
