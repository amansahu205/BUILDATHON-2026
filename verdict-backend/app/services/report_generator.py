"""
Deposition report generator.

Two modes:
  1. LLM-powered (if Anthropic key is set) — full rich analysis via Claude
  2. Rule-based fallback — heuristic analysis from transcript text patterns

Both produce the same output schema so the frontend doesn't care which ran.
"""

import re
from datetime import datetime, timezone

from ..services.aggression import (
    _count_signals,
    CONTRADICTION_SIGNALS,
    THREAT_SIGNALS,
)


def _extract_exchanges(transcript_text: str) -> list[dict]:
    """Parse a raw transcript into a list of speaker/text pairs."""
    exchanges = []
    for line in transcript_text.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        match = re.match(r"\[([^\]]+)\]:\s*(.*)", line)
        if match:
            exchanges.append({"speaker": match.group(1), "text": match.group(2)})
        else:
            if exchanges:
                exchanges[-1]["text"] += " " + line
    return exchanges


def _find_behavioral_tags(text: str) -> list[str]:
    return re.findall(r"\[(pause|sigh|nervous laugh|nervous|throat_clear|hesitation|long pause|scoff|laugh)\]", text, re.IGNORECASE)


def generate_rule_based_report(
    transcript_text: str,
    case_name: str,
    witness_name: str,
    aggression_level: str,
    timeline: list[dict] | None = None,
    alerts: list[dict] | None = None,
) -> dict:
    """Produce a structured report using text-pattern heuristics."""

    exchanges = _extract_exchanges(transcript_text)
    timeline = timeline or []
    alerts = alerts or []
    witness_lines = [e["text"] for e in exchanges if "witness" in e["speaker"].lower() or witness_name.lower() in e["speaker"].lower()]
    interrogator_lines = [e["text"] for e in exchanges if "interrogator" in e["speaker"].lower() or "sean" in e["speaker"].lower() or "cahill" in e["speaker"].lower()]

    all_witness_text = " ".join(witness_lines)
    all_text = transcript_text

    tags = _find_behavioral_tags(all_witness_text)
    tag_counts: dict[str, int] = {}
    for t in tags:
        tag_counts[t.lower()] = tag_counts.get(t.lower(), 0) + 1

    nervous_tags = sum(tag_counts.get(t, 0) for t in ["sigh", "nervous laugh", "nervous", "throat_clear", "hesitation"])
    pause_tags = sum(tag_counts.get(t, 0) for t in ["pause", "long pause"])

    avg_witness_words = sum(len(l.split()) for l in witness_lines) / max(len(witness_lines), 1)
    long_answers = sum(1 for l in witness_lines if len(l.split()) > 30)
    short_answers = sum(1 for l in witness_lines if len(l.split()) <= 5)

    recall_uses = len(re.findall(r"(?:don't|do not|cannot|can't)\s+recall", all_witness_text, re.IGNORECASE))
    evasion_markers = len(re.findall(r"(?:I think|maybe|perhaps|possibly|I'm not sure|I believe)", all_witness_text, re.IGNORECASE))
    contradiction_hits = _count_signals(all_witness_text, CONTRADICTION_SIGNALS)
    threat_hits = _count_signals(all_witness_text, THREAT_SIGNALS)

    scoff_laugh = sum(tag_counts.get(t, 0) for t in ["scoff", "laugh"])

    # ── Composure (1-100) ────────────────────────────────────────
    composure = 85
    composure -= min(nervous_tags * 6, 35)
    composure -= min(threat_hits * 8, 20)
    if "High" in aggression_level or "high" in aggression_level.lower():
        composure -= 5
    composure = max(1, min(100, composure))

    composure_reasoning = (
        f"{nervous_tags} stress-indicating behavioral tags detected "
        f"({', '.join(f'{k}={v}' for k, v in tag_counts.items()) if tag_counts else 'none'}). "
        f"{'Witness showed visible agitation under pressure.' if nervous_tags >= 3 else 'Witness maintained reasonable composure.'} "
        f"Aggression context: {aggression_level}."
    )

    # ── Tactical Discipline (1-100) ──────────────────────────────
    tactical = 85
    tactical -= min(long_answers * 5, 25)
    tactical -= min(int(max(avg_witness_words - 15, 0) * 2), 20)
    tactical += min(short_answers * 2, 15)
    tactical -= min(pause_tags, 10)
    tactical = max(1, min(100, tactical))

    tactical_reasoning = (
        f"Average witness response: {avg_witness_words:.0f} words. "
        f"{long_answers} responses exceeded 30 words (over-explaining). "
        f"{short_answers} concise responses (<=5 words). "
        f"{'Witness frequently filled silence with unnecessary detail.' if long_answers >= 3 else 'Witness showed adequate restraint.'}"
    )

    # ── Professionalism (1-100) ──────────────────────────────────
    professionalism = 90
    professionalism -= min(scoff_laugh * 10, 25)
    professionalism -= min(threat_hits * 8, 20)
    sarcasm = len(re.findall(r"(?:obviously|clearly|as I already said|I told you)", all_witness_text, re.IGNORECASE))
    professionalism -= min(sarcasm * 7, 20)
    professionalism = max(1, min(100, professionalism))

    professionalism_reasoning = (
        f"{scoff_laugh} inappropriate vocal reactions (laugh/scoff). "
        f"{sarcasm} sarcastic or dismissive phrases detected. "
        f"{'Witness argued with the interrogator or showed contempt.' if (scoff_laugh + sarcasm) >= 3 else 'Witness maintained professional demeanor.'}"
    )

    # ── Directness (1-100) ───────────────────────────────────────
    directness = 85
    directness -= min(recall_uses * 8, 25)
    directness -= min(evasion_markers * 5, 20)
    directness += min(short_answers * 2, 10)
    directness = max(1, min(100, directness))

    directness_reasoning = (
        f"'I don't recall' used {recall_uses} time(s). "
        f"{evasion_markers} hedging phrases (I think, maybe, perhaps). "
        f"{'Witness frequently evaded direct questions.' if (recall_uses + evasion_markers) >= 4 else 'Witness was reasonably direct in responses.'}"
    )

    # ── Consistency (1-100) ──────────────────────────────────────
    consistency = 85
    consistency -= min(contradiction_hits * 6, 30)
    late_pause_increase = pause_tags > 2
    if late_pause_increase:
        consistency -= 10
    consistency = max(1, min(100, consistency))

    consistency_reasoning = (
        f"{contradiction_hits} contradiction/inconsistency signals detected in witness testimony. "
        f"{'Pause frequency increased during later questioning — possible fatigue or anxiety.' if late_pause_increase else 'Behavioral pattern remained stable throughout.'}"
    )

    # ── Critical vulnerability ───────────────────────────────────
    worst_score = min(composure, tactical, professionalism, directness, consistency)
    if worst_score == composure:
        vulnerability = {
            "interrogator_tactic_used": "Exhibit Confrontation / Pressure Escalation",
            "witness_reaction": f"Witness displayed {nervous_tags} stress indicators when confronted with evidence",
            "trial_risk": "Jury will perceive witness as unreliable and hiding information when visibly nervous under routine questioning",
        }
    elif worst_score == tactical:
        vulnerability = {
            "interrogator_tactic_used": "Strategic Silence",
            "witness_reaction": f"Witness over-explained with {long_answers} verbose answers averaging {avg_witness_words:.0f} words",
            "trial_risk": "Opposing counsel will use volunteered information to open new attack vectors at trial",
        }
    elif worst_score == directness:
        vulnerability = {
            "interrogator_tactic_used": "Direct Confrontation / Looping Questions",
            "witness_reaction": f"Witness used {recall_uses} recall hedges and {evasion_markers} evasive phrases",
            "trial_risk": "Pattern of evasion will be highlighted to jury as consciousness of guilt or deception",
        }
    elif worst_score == professionalism:
        vulnerability = {
            "interrogator_tactic_used": "Provocation / Credibility Testing",
            "witness_reaction": f"Witness broke decorum with {scoff_laugh} inappropriate reactions and {sarcasm} dismissive remarks",
            "trial_risk": "Jury will find witness unlikable and untrustworthy, undermining all testimony",
        }
    else:
        vulnerability = {
            "interrogator_tactic_used": "Looping / Contradiction Trap",
            "witness_reaction": f"Witness showed {contradiction_hits} inconsistencies across testimony",
            "trial_risk": "Opposing counsel will juxtapose contradictory answers to destroy credibility",
        }

    # ── Coaching suggestions ─────────────────────────────────────
    coaching = []
    if composure < 65:
        coaching.append(
            "Practice controlled breathing before answering — inhale for 3 counts after each "
            "question to eliminate reactive stress signals."
        )
    if tactical < 65:
        coaching.append(
            "Adopt the '10-word rule': no answer should exceed 10 words unless the question "
            "demands a narrative. If silence follows your answer, stay silent."
        )
    if professionalism < 65:
        coaching.append(
            "Treat every question as coming from a judge, not an adversary. Eliminate all "
            "editorial commentary, eye-rolls, and sarcastic inflections."
        )
    if directness < 65:
        coaching.append(
            "Replace 'I don't recall' with specific bounded statements: 'I do not have that "
            "document in front of me' or 'That was not my responsibility.' Never hedge twice "
            "on the same topic."
        )
    if consistency < 65:
        coaching.append(
            "Before the next session, write down your 3 core facts on a card. Every answer "
            "must be traceable back to one of those 3 facts. If it isn't, don't say it."
        )
    if not coaching:
        coaching.append(
            "Performance was solid. Continue using short, factual answers and maintain your "
            "current composure baseline."
        )

    coaching_directive = coaching[0]

    timeline_excerpts = [
        {
            "questionNumber": t.get("questionNumber"),
            "speaker": t.get("speaker"),
            "eventType": t.get("eventType"),
            "content": (t.get("content") or "")[:260],
            "createdAt": t.get("createdAt"),
        }
        for t in timeline[:12]
    ]
    alert_evidence = [
        {
            "alertType": a.get("alertType"),
            "questionNumber": a.get("questionNumber"),
            "classification": a.get("classification"),
            "impeachmentRisk": a.get("impeachmentRisk"),
            "confidence": a.get("confidence"),
            "currentQuote": (a.get("currentQuote") or "")[:220],
            "priorQuote": (a.get("priorQuote") or "")[:220],
            "freRule": a.get("freRule"),
        }
        for a in alerts[:12]
    ]
    io_matrix = [
        {
            "questionNumber": t.get("questionNumber"),
            "input": t.get("content"),
            "outputSummary": "Witness response captured"
            if (t.get("speaker") or "").upper() == "WITNESS"
            else "Interrogator prompt generated",
            "eventType": t.get("eventType"),
        }
        for t in timeline[:12]
    ]

    return {
        "case_name": case_name,
        "witness_name": witness_name,
        "aggression_level": aggression_level,
        "analysis_method": "rule_based",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_rationale": {
            "composure_reasoning": composure_reasoning,
            "tactical_discipline_reasoning": tactical_reasoning,
            "professionalism_reasoning": professionalism_reasoning,
            "directness_reasoning": directness_reasoning,
            "consistency_reasoning": consistency_reasoning,
        },
        "spider_chart_scores": {
            "composure": composure,
            "tactical_discipline": tactical,
            "professionalism": professionalism,
            "directness": directness,
            "consistency": consistency,
        },
        "critical_vulnerability": vulnerability,
        "coaching_directive": coaching_directive,
        "coaching_suggestions": coaching,
        "timeline_excerpts": timeline_excerpts,
        "alert_evidence": alert_evidence,
        "input_output_matrix": io_matrix,
        "lawyer_brief": _build_lawyer_brief(
            case_name, witness_name, aggression_level,
            composure, tactical, professionalism, directness, consistency,
            vulnerability, coaching, len(exchanges), len(witness_lines),
        ),
    }


def _build_lawyer_brief(
    case_name: str, witness_name: str, aggression_level: str,
    composure: int, tactical: int, professionalism: int,
    directness: int, consistency: int,
    vulnerability: dict, coaching: list[str],
    total_exchanges: int, witness_responses: int,
) -> dict:
    avg_score = (composure + tactical + professionalism + directness + consistency) / 5
    if avg_score >= 75:
        overall = "Strong"
        trial_readiness = "Witness is near trial-ready with minor refinements needed."
    elif avg_score >= 55:
        overall = "Moderate"
        trial_readiness = "Witness requires additional prep sessions before trial testimony."
    else:
        overall = "Weak"
        trial_readiness = "Witness is NOT trial-ready. Significant coaching required before any live testimony."

    weakest = min(
        ("Composure", composure), ("Tactical Discipline", tactical),
        ("Professionalism", professionalism), ("Directness", directness),
        ("Consistency", consistency),
        key=lambda x: x[1],
    )
    strongest = max(
        ("Composure", composure), ("Tactical Discipline", tactical),
        ("Professionalism", professionalism), ("Directness", directness),
        ("Consistency", consistency),
        key=lambda x: x[1],
    )

    return {
        "case_name": case_name,
        "witness_name": witness_name,
        "interrogation_intensity": aggression_level,
        "overall_rating": overall,
        "overall_score": round(avg_score),
        "trial_readiness": trial_readiness,
        "strongest_dimension": f"{strongest[0]} ({strongest[1]}/100)",
        "weakest_dimension": f"{weakest[0]} ({weakest[1]}/100)",
        "primary_risk": vulnerability["trial_risk"],
        "total_exchanges": total_exchanges,
        "witness_responses": witness_responses,
        "priority_coaching_items": coaching,
        "recommended_next_steps": [
            f"Schedule follow-up mock deposition focusing on {weakest[0].lower()}",
            "Review transcript highlights with witness before next session",
            "Prepare witness for specific exhibit confrontations identified in this session",
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
