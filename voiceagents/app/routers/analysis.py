import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from ..config import settings
from ..services.aggression import score_witness, score_vulnerability

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

DEPOSITIONS_PATH = settings.cases_file.parent / "verdict_depositions.json"


def _load_depositions() -> dict:
    if not DEPOSITIONS_PATH.exists():
        raise HTTPException(404, "verdict_depositions.json not found")
    return json.loads(DEPOSITIONS_PATH.read_text())


def _process_witness(witness: dict) -> dict:
    aggression = score_witness(witness)
    vulnerability = score_vulnerability(witness, aggression["aggression_score"])

    resolved_vars = dict(witness["variables"])
    resolved_vars["aggression_level"] = f"{aggression['aggression_score']}/100 ({aggression['aggression_level']})"

    return {
        "witness_name": aggression["witness_name"],
        "side": aggression["side"],
        "role": aggression["role"],
        "aggression_assignment": {
            "score": aggression["aggression_score"],
            "level": aggression["aggression_level"],
            "reasons": aggression["scoring_reasons"],
        },
        "vulnerability_assessment": vulnerability,
        "resolved_variables": resolved_vars,
    }


@router.get("/process")
async def process_all_cases():
    """Load all cases from verdict_depositions.json, dynamically assign
    aggression scores (1-100), run vulnerability scoring, and return the
    full analysis for every witness."""

    data = _load_depositions()
    results = []

    for case in data.get("cases", []):
        case_result = {
            "case_name": case["case_name"],
            "witnesses": [_process_witness(w) for w in case.get("witnesses", [])],
        }
        results.append(case_result)

    return {"cases": results}


@router.get("/process/{case_index}")
async def process_single_case(case_index: int):
    """Process a single case by its index (0-based)."""
    data = _load_depositions()
    cases = data.get("cases", [])

    if case_index < 0 or case_index >= len(cases):
        raise HTTPException(404, f"Case index {case_index} out of range (0-{len(cases)-1})")

    case = cases[case_index]
    return {
        "case_name": case["case_name"],
        "witnesses": [_process_witness(w) for w in case.get("witnesses", [])],
    }
