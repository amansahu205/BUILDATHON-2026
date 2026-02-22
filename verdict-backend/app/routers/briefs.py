from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.middleware.auth import require_auth
from app.models.user import User
from app.models.brief import Brief

router = APIRouter()


@router.get("/share/{share_token}")
async def get_shared_brief(share_token: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Brief).where(Brief.share_token == share_token))
    brief = result.scalar_one_or_none()
    if not brief:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    if brief.share_token_expires_at and brief.share_token_expires_at < datetime.utcnow():
        raise HTTPException(410, detail={"code": "SHARE_LINK_EXPIRED"})
    return {
        "success": True,
        "data": {
            "sessionScore": brief.session_score,
            "consistencyRate": brief.consistency_rate,
            "topRecommendations": brief.top_recommendations,
            "narrativeText": brief.narrative_text,
        },
    }


@router.get("/{brief_id}")
async def get_brief(brief_id: str, db: AsyncSession = Depends(get_db), user: User = Depends(require_auth)):
    result = await db.execute(select(Brief).where(Brief.id == brief_id, Brief.firm_id == user.firm_id))
    brief = result.scalar_one_or_none()
    if not brief:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    return {
        "success": True,
        "data": {
            "id": brief.id,
            "sessionScore": brief.session_score,
            "consistencyRate": brief.consistency_rate,
            "deltaVsBaseline": brief.delta_vs_baseline,
            "confirmedFlags": brief.confirmed_flags,
            "objectionCount": brief.objection_count,
            "composureAlerts": brief.composure_alerts,
            "topRecommendations": brief.top_recommendations,
            "narrativeText": brief.narrative_text,
            "weaknessMapScores": brief.weakness_map_scores,
            "shareToken": brief.share_token,
            "pdfS3Key": brief.pdf_s3_key,
            "createdAt": brief.created_at,
        },
    }
