from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateCaseRequest(BaseModel):
    name: str
    caseType: str
    caseTypeCustom: Optional[str] = None
    opposingFirm: Optional[str] = None
    depositionDate: Optional[str] = None


class UpdateCaseRequest(BaseModel):
    name: Optional[str] = None
    depositionDate: Optional[str] = None


class CaseOut(BaseModel):
    id: str
    name: str
    caseType: str
    depositionDate: Optional[datetime] = None
    createdAt: datetime

    model_config = {"from_attributes": True}
