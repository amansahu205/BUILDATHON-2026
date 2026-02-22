from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.middleware.auth import require_auth
from app.models.user import User
from app.models.case import Case
from app.models.witness import Witness

router = APIRouter()


@router.get("/{case_id}/witnesses")
async def list_witnesses(case_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    result = await db.execute(
        select(Witness).where(Witness.case_id == case_id).order_by(Witness.created_at.desc())
    )
    witnesses = result.scalars().all()
    return {
        "success": True,
        "data": {
            "witnesses": [
                {
                    "id": w.id,
                    "caseId": w.case_id,
                    "name": w.name,
                    "role": w.role,
                    "sessionCount": w.session_count,
                    "latestScore": w.latest_score,
                    "plateauDetected": w.plateau_detected,
                    "createdAt": w.created_at,
                }
                for w in witnesses
            ],
        },
    }


@router.post("/{case_id}/witnesses", status_code=201)
async def create_witness(case_id: str, body: dict, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.firm_id == user.firm_id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    w = Witness(
        case_id=case_id,
        firm_id=user.firm_id,
        name=body.get("name", ""),
        email=body.get("email", ""),
        role=body.get("role", "OTHER"),
        linked_document_ids=[],
    )
    db.add(w)
    await db.commit()
    await db.refresh(w)

    return {
        "success": True,
        "data": {
            "id": w.id,
            "caseId": w.case_id,
            "name": w.name,
            "role": w.role,
            "sessionCount": w.session_count,
            "latestScore": w.latest_score,
            "createdAt": w.created_at,
        },
    }


@router.get("/{case_id}/witnesses/{witness_id}")
async def get_witness(case_id: str, witness_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(
        select(Witness).where(Witness.id == witness_id, Witness.case_id == case_id)
    )
    w = result.scalar_one_or_none()
    if not w:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    return {
        "success": True,
        "data": {
            "id": w.id,
            "caseId": w.case_id,
            "name": w.name,
            "role": w.role,
            "sessionCount": w.session_count,
            "latestScore": w.latest_score,
            "plateauDetected": w.plateau_detected,
            "createdAt": w.created_at,
        },
    }
