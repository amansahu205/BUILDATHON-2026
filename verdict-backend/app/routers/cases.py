from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.middleware.auth import require_auth
from app.models.user import User
from app.models.case import Case
from app.schemas.cases import CreateCaseRequest

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
                    "name": c.name,
                    "caseType": c.case_type,
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
        name=body.name,
        case_type=body.caseType,
        case_type_custom=body.caseTypeCustom,
        opposing_firm=body.opposingFirm,
        deposition_date=datetime.fromisoformat(body.depositionDate) if body.depositionDate else None,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return {
        "success": True,
        "data": {"id": c.id, "name": c.name, "caseType": c.case_type, "depositionDate": c.deposition_date, "createdAt": c.created_at},
    }


@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    return {"success": True, "data": {"id": c.id, "name": c.name, "caseType": c.case_type, "depositionDate": c.deposition_date}}


@router.patch("/{case_id}")
async def update_case(case_id: str, body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    if "name" in body:
        c.name = body["name"]
    if "depositionDate" in body:
        c.deposition_date = datetime.fromisoformat(body["depositionDate"])
    await db.commit()
    return {"success": True, "data": {"id": c.id, "name": c.name}}


@router.delete("/{case_id}")
async def archive_case(case_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id))
    c = result.scalar_one_or_none()
    if not c:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    c.is_archived = True
    await db.commit()
    return {"success": True, "message": "Case archived"}
