import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import httpx

from ..config import settings
from ..models import ReportRequest
from ..prompt import build_system_prompt
from ..dependencies import get_case_store
from ..services.elevenlabs import elevenlabs_service
from ..services.llm import analyze_transcript
from ..services.report_generator import generate_rule_based_report
from ..services.pdf_report import generate_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])


def _reports_dir() -> Path:
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    return settings.reports_dir


def _save_report(report: dict) -> None:
    path = _reports_dir() / f"{report['report_id']}.json"
    path.write_text(json.dumps(report, indent=2))


def _format_transcript(raw: list[dict]) -> str:
    """Convert ElevenLabs transcript array into tagged text lines."""
    lines = []
    for entry in raw:
        role = entry.get("role", "unknown")
        text = entry.get("message", entry.get("text", ""))
        if role in ("agent", "ai"):
            lines.append(f"[INTERROGATOR]: {text}")
        else:
            lines.append(f"[WITNESS]: {text}")
    return "\n".join(lines)


@router.post("/generate")
async def generate_report(body: ReportRequest):
    """Generate a deposition analysis report.

    Accepts EITHER:
      - conversation_id: fetches transcript from ElevenLabs history
      - transcript: raw transcript text provided directly

    Optionally provide case_id to inject case context into the analysis.
    """
    transcript_text = body.transcript
    case_name = "Unknown Case"
    witness_name = body.witness_name or "Unknown Witness"
    aggression_level = body.aggression_level or "Medium"
    case = None

    if body.case_id:
        case = get_case_store().get(body.case_id)
        if case:
            case_name = case.case_name
            witness_name = body.witness_name or case.witness_name.split(";")[0].strip()
            aggression_level = body.aggression_level or case.aggression_level

    if body.conversation_id and not transcript_text:
        if not settings.elevenlabs_api_key:
            raise HTTPException(500, "ELEVENLABS_API_KEY required to fetch conversation")
        try:
            conv = await elevenlabs_service.get_conversation(body.conversation_id)
            raw_transcript = conv.get("transcript", [])
            if not raw_transcript:
                raise HTTPException(
                    422, f"Conversation {body.conversation_id} has no transcript data"
                )
            transcript_text = _format_transcript(raw_transcript)
            if not case_name or case_name == "Unknown Case":
                meta = conv.get("metadata", {})
                case_name = meta.get("case_name", case_name)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                raise HTTPException(404, "Conversation not found in ElevenLabs")
            raise HTTPException(502, f"ElevenLabs error: {exc.response.status_code}")

    if not transcript_text:
        raise HTTPException(
            422, "Provide either 'conversation_id' or 'transcript' text"
        )

    # ── Try LLM analysis first, fall back to rule-based ──────────
    analysis = None
    analysis_method = "rule_based"

    if case and settings.anthropic_api_key:
        system_prompt = build_system_prompt(case)
        try:
            analysis = await analyze_transcript(system_prompt, transcript_text)
            if analysis:
                analysis_method = "llm_claude"
        except Exception as exc:
            print(f"LLM analysis failed, falling back to rule-based: {exc}")

    if not analysis:
        analysis = generate_rule_based_report(
            transcript_text, case_name, witness_name, aggression_level
        )

    # ── If LLM analysis, enrich with lawyer brief ────────────────
    if analysis_method == "llm_claude" and "lawyer_brief" not in analysis:
        scores = analysis.get("spider_chart_scores", {})
        coaching = analysis.get("coaching_suggestions", [analysis.get("coaching_directive", "")])
        from ..services.report_generator import _build_lawyer_brief
        analysis["lawyer_brief"] = _build_lawyer_brief(
            case_name, witness_name, aggression_level,
            scores.get("composure", 50), scores.get("tactical_discipline", 50),
            scores.get("professionalism", 50), scores.get("directness", 50),
            scores.get("consistency", 50),
            analysis.get("critical_vulnerability", {}), coaching,
            transcript_text.count("\n") + 1,
            transcript_text.lower().count("[witness]"),
        )
        if "coaching_suggestions" not in analysis:
            analysis["coaching_suggestions"] = coaching

    report_id = str(uuid.uuid4())[:12]
    report = {
        "report_id": report_id,
        "case_name": case_name,
        "witness_name": witness_name,
        "aggression_level": aggression_level,
        "analysis_method": analysis_method,
        "conversation_id": body.conversation_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        **analysis,
    }

    _save_report(report)

    return report


@router.get("")
async def list_reports():
    """List all saved reports."""
    reports_dir = _reports_dir()
    summaries = []

    for f in sorted(reports_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text())
            brief = data.get("lawyer_brief", {})
            summaries.append({
                "report_id": data.get("report_id", f.stem),
                "case_name": data.get("case_name", ""),
                "witness_name": data.get("witness_name", ""),
                "overall_score": brief.get("overall_score", 0),
                "overall_rating": brief.get("overall_rating", ""),
                "analysis_method": data.get("analysis_method", ""),
                "generated_at": data.get("generated_at", ""),
            })
        except json.JSONDecodeError:
            continue

    return {"reports": summaries, "total": len(summaries)}


@router.get("/{report_id}")
async def get_report(report_id: str):
    """Retrieve a single report by ID."""
    path = _reports_dir() / f"{report_id}.json"
    if not path.exists():
        raise HTTPException(404, f"Report '{report_id}' not found")
    return json.loads(path.read_text())


@router.get("/{report_id}/pdf")
async def download_report_pdf(report_id: str):
    """Download a previously generated report as a branded PDF."""
    path = _reports_dir() / f"{report_id}.json"
    if not path.exists():
        raise HTTPException(404, f"Report '{report_id}' not found")

    report = json.loads(path.read_text())
    pdf_buf = generate_pdf(report)

    witness_slug = report.get("witness_name", "report").replace(" ", "_").lower()
    filename = f"VERDICT_{witness_slug}_{report_id}.pdf"

    return StreamingResponse(
        pdf_buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("/generate/pdf")
async def generate_and_download_pdf(body: ReportRequest):
    """Generate a report AND immediately return it as a PDF download."""
    report = await generate_report(body)
    pdf_buf = generate_pdf(report)

    witness_slug = report.get("witness_name", "report").replace(" ", "_").lower()
    filename = f"VERDICT_{witness_slug}_{report['report_id']}.pdf"

    return StreamingResponse(
        pdf_buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
