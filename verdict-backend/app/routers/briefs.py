import logging
from datetime import datetime, timedelta
from nanoid import generate as nanoid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db, AsyncSessionLocal
from app.middleware.auth import require_auth
from app.models.user import User
from app.models.session import Session
from app.models.brief import Brief
from app.models.alert import Alert
from app.models.session_event import SessionEvent
from app.agents.orchestrator import generate_brief
from app.services.report_generator import generate_rule_based_report
from app.services.pdf_report import generate_pdf
from app.services.s3 import upload_bytes

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate/{session_id}")
async def trigger_brief_generation(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Trigger coaching brief generation for a completed session.

    This endpoint:
      1. Validates the session exists and is COMPLETE (or forces completion)
      2. Kicks off background brief generation via the Review Orchestrator
      3. Returns immediately with a brief ID for polling
    """
    result = await db.execute(
        select(Session)
        .where(Session.id == session_id, Session.firm_id == user.firm_id)
        .options(selectinload(Session.brief))
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(404, detail={"code": "SESSION_NOT_FOUND"})

    if session.brief:
        return {
            "success": True,
            "data": {
                "briefId": session.brief.id,
                "status": "ALREADY_EXISTS",
                "message": "Brief already generated for this session.",
            },
        }

    if session.status not in ("COMPLETE", "ACTIVE"):
        raise HTTPException(400, detail={
            "code": "INVALID_SESSION_STATUS",
            "message": f"Session is in {session.status} state. Must be ACTIVE or COMPLETE.",
        })

    if session.status == "ACTIVE":
        session.status = "COMPLETE"
        session.ended_at = datetime.utcnow()
        await db.commit()

    brief = Brief(
        session_id=session_id,
        firm_id=user.firm_id,
        witness_id=session.witness_id,
        session_score=0,
        consistency_rate=0.0,
        confirmed_flags=0,
        objection_count=0,
        composure_alerts=0,
        top_recommendations=[],
        narrative_text="Generating...",
    )
    db.add(brief)
    await db.commit()
    await db.refresh(brief)

    background_tasks.add_task(_generate_brief_background, session_id, brief.id)

    return {
        "success": True,
        "data": {
            "briefId": brief.id,
            "status": "GENERATING",
            "message": "Brief generation started. Poll GET /briefs/{briefId} for status.",
        },
    }


async def _generate_brief_background(session_id: str, brief_id: str):
    """Run the full brief generation pipeline in a background task."""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(Session)
                .where(Session.id == session_id)
                .options(
                    selectinload(Session.case),
                    selectinload(Session.witness),
                    selectinload(Session.alerts),
                    selectinload(Session.events),
                )
            )
            session = result.scalar_one_or_none()
            if not session:
                return

            result = await db.execute(select(Brief).where(Brief.id == brief_id))
            brief = result.scalar_one_or_none()
            if not brief:
                return

            events = sorted(
                (session.events or []),
                key=lambda e: (e.question_number or 0, e.created_at or datetime.utcnow()),
            )
            transcript = []
            timeline = []
            transcript_lines = []

            for e in events:
                if not e.content:
                    continue
                speaker = e.speaker_role or "UNKNOWN"
                transcript.append({"speaker": speaker, "content": e.content})
                transcript_lines.append(f"[{speaker}]: {e.content}")
                timeline.append(
                    {
                        "eventId": e.id,
                        "questionNumber": e.question_number,
                        "eventType": e.event_type,
                        "speaker": speaker,
                        "content": e.content,
                        "createdAt": e.created_at.isoformat() if e.created_at else None,
                    }
                )

            if not transcript and session.transcript_raw:
                for line in session.transcript_raw.strip().split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("["):
                        bracket_end = line.find("]")
                        if bracket_end > 0:
                            speaker = line[1:bracket_end]
                            content = line[bracket_end + 1 :].lstrip(": ")
                            transcript.append({"speaker": speaker, "content": content})
                            transcript_lines.append(f"[{speaker}]: {content}")
                            timeline.append(
                                {
                                    "eventId": None,
                                    "questionNumber": None,
                                    "eventType": "UNKNOWN",
                                    "speaker": speaker,
                                    "content": content,
                                    "createdAt": None,
                                }
                            )
                        else:
                            transcript.append({"speaker": "UNKNOWN", "content": line})
                            transcript_lines.append(f"[UNKNOWN]: {line}")
                    else:
                        transcript.append({"speaker": "UNKNOWN", "content": line})
                        transcript_lines.append(f"[UNKNOWN]: {line}")

            alerts_data = [
                {
                    "alertType": a.alert_type,
                    "questionNumber": a.question_number,
                    "currentQuote": a.current_quote or "",
                    "priorQuote": a.prior_quote or "",
                    "confidence": a.confidence or 0,
                    "freRule": a.fre_rule,
                    "classification": a.fre_classification,
                    "impeachmentRisk": a.impeachment_risk,
                    "status": a.status,
                }
                for a in (session.alerts or [])
            ]

            case_type = session.case.case_type if session.case else "OTHER"
            witness_role = session.witness.role if session.witness else "OTHER"

            brief_data = await generate_brief(
                session_id=session_id,
                transcript=transcript,
                alerts=alerts_data,
                case_type=case_type,
                witness_role=witness_role,
                aggression_level=session.aggression or "STANDARD",
                duration_minutes=session.duration_minutes or 30,
                question_count=session.question_count or 0,
            )

            brief.session_score = brief_data.get("sessionScore", 0)
            brief.consistency_rate = brief_data.get("consistencyRate", 0.0)
            brief.confirmed_flags = brief_data.get("confirmedFlags", 0)
            brief.objection_count = brief_data.get("objectionCount", 0)
            brief.composure_alerts = brief_data.get("composureAlerts", 0)
            brief.top_recommendations = brief_data.get("topRecommendations", [])
            brief.narrative_text = brief_data.get("narrativeText", "")
            brief.weakness_map_scores = brief_data.get("weaknessMapScores")

            session.session_score = brief.session_score
            session.consistency_rate = brief.consistency_rate

            if session.witness:
                witness = session.witness
                if witness.baseline_score is None:
                    witness.baseline_score = brief.session_score
                    brief.delta_vs_baseline = None
                else:
                    brief.delta_vs_baseline = brief.session_score - witness.baseline_score
                witness.latest_score = brief.session_score

            try:
                report = generate_rule_based_report(
                    transcript_text="\n".join(transcript_lines),
                    case_name=session.case.case_name if session.case else "Unknown",
                    witness_name=session.witness.name if session.witness else "Unknown",
                    aggression_level=session.aggression or "Medium",
                    timeline=timeline,
                    alerts=alerts_data,
                )
                pdf_buf = generate_pdf(report)
                pdf_key = f"briefs/{session.firm_id}/{brief.id}.pdf"
                upload_bytes(pdf_key, pdf_buf.read(), "application/pdf")
                brief.pdf_s3_key = pdf_key
            except Exception as exc:
                logger.warning("PDF generation failed: %s", exc)

            if brief_data.get("coachAudioBytes"):
                try:
                    audio_key = f"briefs/{session.firm_id}/{brief.id}_coach.mp3"
                    upload_bytes(audio_key, brief_data["coachAudioBytes"], "audio/mpeg")
                except Exception:
                    pass

            await db.commit()
            logger.info("Brief %s generated for session %s", brief_id, session_id)

        except Exception as exc:
            logger.error("Brief generation failed for session %s: %s", session_id, exc)
            try:
                result = await db.execute(select(Brief).where(Brief.id == brief_id))
                brief = result.scalar_one_or_none()
                if brief:
                    brief.narrative_text = f"Generation failed: {exc}"
                    await db.commit()
            except Exception:
                pass


@router.post("/{brief_id}/share")
async def generate_share_token(
    brief_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Generate a 7-day share token for a brief.

    The share token allows witnesses to view a read-only subset
    of the brief without logging in.
    """
    result = await db.execute(
        select(Brief).where(Brief.id == brief_id, Brief.firm_id == user.firm_id)
    )
    brief = result.scalar_one_or_none()
    if not brief:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    token = nanoid(size=24)
    brief.share_token = token
    brief.share_token_expires_at = datetime.utcnow() + timedelta(days=7)
    await db.commit()

    return {
        "success": True,
        "data": {
            "shareToken": token,
            "expiresAt": brief.share_token_expires_at.isoformat(),
            "shareUrl": f"/briefs/share/{token}",
        },
    }


@router.get("/{brief_id}/pdf")
async def download_brief_pdf(
    brief_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_auth),
):
    """Get a presigned download URL for the brief PDF."""
    result = await db.execute(
        select(Brief).where(Brief.id == brief_id, Brief.firm_id == user.firm_id)
    )
    brief = result.scalar_one_or_none()
    if not brief:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})

    if not brief.pdf_s3_key:
        raise HTTPException(404, detail={
            "code": "PDF_NOT_AVAILABLE",
            "message": "PDF has not been generated yet.",
        })

    from app.services.s3 import generate_presigned_download
    url = generate_presigned_download(brief.pdf_s3_key)

    return {"success": True, "data": {"downloadUrl": url}}


@router.get("/share/{share_token}")
async def get_shared_brief(share_token: str, db: AsyncSession = Depends(get_db)):
    """Get a brief via share token (no auth required, witness-safe view)."""
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
    """Get full brief details (attorney view, auth required)."""
    result = await db.execute(select(Brief).where(Brief.id == brief_id, Brief.firm_id == user.firm_id))
    brief = result.scalar_one_or_none()
    if not brief:
        raise HTTPException(404, detail={"code": "NOT_FOUND"})
    return {
        "success": True,
        "data": {
            "id": brief.id,
            "sessionId": brief.session_id,
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
