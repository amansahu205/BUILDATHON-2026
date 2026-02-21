from fastapi import APIRouter, HTTPException

from ..models import VerdictCase, CaseCreate, CaseUpdate
from ..dependencies import get_case_store

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=list[VerdictCase])
async def list_cases():
    return get_case_store().list_all()


@router.get("/{case_id}", response_model=VerdictCase)
async def get_case(case_id: str):
    case = get_case_store().get(case_id)
    if not case:
        raise HTTPException(404, f"Case '{case_id}' not found")
    return case


@router.post("", response_model=VerdictCase, status_code=201)
async def create_case(body: CaseCreate):
    try:
        return get_case_store().create(body)
    except ValueError as exc:
        raise HTTPException(409, str(exc))


@router.patch("/{case_id}", response_model=VerdictCase)
async def update_case(case_id: str, body: CaseUpdate):
    updated = get_case_store().update(case_id, body)
    if not updated:
        raise HTTPException(404, f"Case '{case_id}' not found")
    return updated


@router.delete("/{case_id}", status_code=204)
async def delete_case(case_id: str):
    if not get_case_store().delete(case_id):
        raise HTTPException(404, f"Case '{case_id}' not found")
