from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateCaseRequest(BaseModel):
    caseName: str
    caseType: str
    caseTypeCustom: Optional[str] = None
    opposingParty: Optional[str] = None
    depositionDate: Optional[str] = None
    witnessName: Optional[str] = None
    witnessRole: Optional[str] = None
    aggressionLevel: Optional[str] = None
    extractedFacts: Optional[str] = None
    priorStatements: Optional[str] = None
    exhibitList: Optional[str] = None
    focusAreas: Optional[str] = None


class UpdateCaseRequest(BaseModel):
    caseName: Optional[str] = None
    depositionDate: Optional[str] = None
    opposingParty: Optional[str] = None
    witnessName: Optional[str] = None
    witnessRole: Optional[str] = None
    aggressionLevel: Optional[str] = None
    extractedFacts: Optional[str] = None
    priorStatements: Optional[str] = None
    exhibitList: Optional[str] = None
    focusAreas: Optional[str] = None


class CaseOut(BaseModel):
    id: str
    caseName: str
    caseType: str
    depositionDate: Optional[datetime] = None
    opposingParty: Optional[str] = None
    witnessName: Optional[str] = None
    witnessRole: Optional[str] = None
    aggressionLevel: Optional[str] = None
    extractedFacts: Optional[str] = None
    priorStatements: Optional[str] = None
    exhibitList: Optional[str] = None
    focusAreas: Optional[str] = None
    createdAt: datetime

    model_config = {"from_attributes": True}
