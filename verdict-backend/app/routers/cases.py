from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.middleware.auth import require_auth
from app.models.user import User
from app.models.case import Case
from app.schemas.cases import CreateCaseRequest, UpdateCaseRequest

router = APIRouter()


@router.get("/")
async def list_cases(db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(
        select(Case)
        .where(Case.firm_id == user.firm_id, Case.is_archived == False)
        .order_by(Case.deposition_date.asc())
    )
    cases = result.scalars().all()
    return {
        "success": True,
        "data": {
            "cases": [
                {
                    "id": c.id,
                    "caseName": c.case_name,
                    "caseType": c.case_type,
                    "opposingParty": c.opposing_party,
                    "witnessName": c.witness_name,
                    "witnessRole": c.witness_role,
                    "aggressionLevel": c.aggression_level,
                    "depositionDate": c.deposition_date,
                    "createdAt": c.created_at,
                }
                for c in cases
            ],
            "pagination": {"page": 1, "limit": 20, "total": len(cases)},
        },
    }


@router.post("/", status_code=201)
async def create_case(body: CreateCaseRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    c = Case(
        firm_id=user.firm_id,
        owner_id=user.id,
        case_name=body.caseName,
        case_type=body.caseType,
        case_type_custom=body.caseTypeCustom,
        opposing_party=body.opposingParty,
        deposition_date=datetime.fromisoformat(body.depositionDate).replace(tzinfo=None) if body.depositionDate else None,
        witness_name=body.witnessName,
        witness_role=body.witnessRole,
        aggression_level=body.aggressionLevel,
        extracted_facts=body.extractedFacts,
        prior_statements=body.priorStatements,
        exhibit_list=body.exhibitList,
        focus_areas=body.focusAreas,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return {
        "success": True,
        "data": {
            "id": c.id,
            "caseName": c.case_name,
            "caseType": c.case_type,
            "opposingParty": c.opposing_party,
            "witnessName": c.witness_name,
            "witnessRole": c.witness_role,
            "aggressionLevel": c.aggression_level,
            "depositionDate": c.deposition_date,
            "createdAt": c.created_at,
        },
    }


@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    return {
        "success": True,
        "data": {
            "id": c.id,
            "caseName": c.case_name,
            "caseType": c.case_type,
            "opposingParty": c.opposing_party,
            "witnessName": c.witness_name,
            "witnessRole": c.witness_role,
            "aggressionLevel": c.aggression_level,
            "depositionDate": c.deposition_date,
            "extractedFacts": c.extracted_facts,
            "priorStatements": c.prior_statements,
            "exhibitList": c.exhibit_list,
            "focusAreas": c.focus_areas,
            "createdAt": c.created_at,
        },
    }


@router.patch("/{case_id}")
async def update_case(case_id: str, body: UpdateCaseRequest, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    if body.caseName is not None:
        c.case_name = body.caseName
    if body.depositionDate is not None:
        c.deposition_date = datetime.fromisoformat(body.depositionDate).replace(tzinfo=None)
    if body.opposingParty is not None:
        c.opposing_party = body.opposingParty
    if body.witnessName is not None:
        c.witness_name = body.witnessName
    if body.witnessRole is not None:
        c.witness_role = body.witnessRole
    if body.aggressionLevel is not None:
        c.aggression_level = body.aggressionLevel
    if body.extractedFacts is not None:
        c.extracted_facts = body.extractedFacts
    if body.priorStatements is not None:
        c.prior_statements = body.priorStatements
    if body.exhibitList is not None:
        c.exhibit_list = body.exhibitList
    if body.focusAreas is not None:
        c.focus_areas = body.focusAreas
    await db.commit()
    return {"success": True, "data": {"id": c.id, "caseName": c.case_name}}


@router.delete("/{case_id}")
async def archive_case(case_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    c.is_archived = True
    await db.commit()
    return {"success": True, "message": "Case archived"}
