"""
Rule-based aggression-level engine (1–100 scale).

Analyzes witness metadata, role, side, prior statements, extracted facts,
and exhibit density to produce a numeric aggression score from 1 to 100.

Score bands:
   1-33   Standard      — gentle pacing, rapport-building questions
  34-66   Elevated      — pointed follow-ups, exhibit confrontations
  67-100  High-Stakes   — relentless looping, silence traps, full pressure
"""

import re

CONTRADICTION_SIGNALS = [
    "denied", "denies", "claims", "maintains", "recant",
    "not a threat", "not involved", "not material",
    "did not disclose", "never disclosed", "no written record",
    "failed to", "did not file", "not investigated",
    "open and shut", "never been wrong",
]

DUTY_FAILURE_SIGNALS = [
    "brady", "did not disclose", "never disclosed",
    "no written record", "not filed", "did not file",
    "not investigated", "without review", "marked resolved",
]

EVIDENCE_SIGNALS = [
    "fingerprint", "shoeprint", "fiber", "exhibit",
    "morsel", "trail", "footage", "report", "audit",
    "text message", "slack", "email", "invoice",
    "recantation", "plea", "warrant", "lineup",
]

THREAT_SIGNALS = [
    "threat", "regret", "pay for", "hostile", "shouting",
    "threw", "angry", "confrontation", "karma",
]


def _count_signals(text: str, signals: list[str]) -> int:
    text_lower = text.lower()
    return sum(1 for s in signals if s in text_lower)


def _label_from_score(score: int) -> str:
    if score <= 33:
        return "Standard"
    if score <= 66:
        return "Elevated"
    return "High-Stakes"


def score_witness(witness: dict) -> dict:
    meta = witness["_meta"]
    v = witness["variables"]

    side = meta.get("side", "").lower()
    role = v.get("witness_role", "").lower()
    facts = v.get("extracted_facts", "")
    prior = v.get("prior_statements", "")
    exhibits = v.get("exhibit_list", "")
    focus = v.get("focus_areas", "")
    corpus = f"{facts} {prior} {exhibits}"

    score = 0
    reasons = []

    is_defendant = "defendant" in role
    is_expert = "expert" in role
    is_prosecution_side = side == "prosecution"
    is_defense_side = side == "defense"

    focus_count = len([f for f in focus.split(",") if f.strip()])
    contradiction_hits = _count_signals(corpus, CONTRADICTION_SIGNALS)
    duty_hits = _count_signals(corpus, DUTY_FAILURE_SIGNALS)
    evidence_hits = _count_signals(corpus, EVIDENCE_SIGNALS)
    threat_hits = _count_signals(corpus, THREAT_SIGNALS)

    # ── Role baseline (0-20) ─────────────────────────────────────
    if is_defendant:
        base = 15 + min(evidence_hits * 3, 15)
        score += base
        reasons.append(f"Defendant with {evidence_hits} evidence markers (+{base})")
    elif is_prosecution_side:
        score += 12
        reasons.append("Hostile witness — opposing side (+12)")
    elif is_defense_side and is_expert:
        score += 5
        reasons.append("Friendly expert — minimal pressure needed (+5)")
    elif is_defense_side:
        score += 8
        reasons.append("Friendly fact witness (+8)")

    # ── Duty failures (0-25) ─────────────────────────────────────
    if duty_hits >= 3:
        score += 25
        reasons.append(f"Severe legal/procedural duty failures ({duty_hits} signals) (+25)")
    elif duty_hits == 2:
        score += 18
        reasons.append(f"Multiple procedural failures ({duty_hits} signals) (+18)")
    elif duty_hits == 1:
        score += 8
        reasons.append("Minor procedural concern (+8)")

    # ── Contradictions (0-20) ────────────────────────────────────
    if contradiction_hits >= 5:
        score += 20
        reasons.append(f"Extreme prior-statement inconsistencies ({contradiction_hits} hits) (+20)")
    elif contradiction_hits >= 3:
        score += 15
        reasons.append(f"Heavy prior-statement inconsistencies ({contradiction_hits} hits) (+15)")
    elif contradiction_hits >= 2:
        score += 10
        reasons.append(f"Notable contradictions ({contradiction_hits} hits) (+10)")
    elif contradiction_hits == 1:
        score += 4
        reasons.append("Minor inconsistency in prior statements (+4)")

    # ── Threat / emotional signals (0-10) ────────────────────────
    if threat_hits >= 3:
        score += 10
        reasons.append(f"Strong emotional volatility signals ({threat_hits} hits) (+10)")
    elif threat_hits >= 1:
        score += 5
        reasons.append(f"Some emotional signals ({threat_hits} hits) (+5)")

    # ── Authority figure (0-8) ───────────────────────────────────
    authority_keywords = ["sovereign", "queen", "lead", "senior", "chief", "detective", "officer"]
    if any(kw in role for kw in authority_keywords):
        score += 8
        reasons.append("Authority figure — methodology and bias attackable (+8)")

    # ── Attack surface (0-7) ─────────────────────────────────────
    if focus_count >= 4:
        score += 7
        reasons.append(f"Very wide attack surface ({focus_count} focus areas) (+7)")
    elif focus_count >= 3:
        score += 5
        reasons.append(f"Wide attack surface ({focus_count} focus areas) (+5)")
    elif focus_count >= 2:
        score += 3
        reasons.append(f"Moderate attack surface ({focus_count} focus areas) (+3)")

    # ── Exhibit density (0-10) ───────────────────────────────────
    if evidence_hits >= 6:
        score += 10
        reasons.append(f"Rich exhibit pool for confrontation ({evidence_hits} markers) (+10)")
    elif evidence_hits >= 3:
        score += 6
        reasons.append(f"Decent exhibit pool ({evidence_hits} markers) (+6)")
    elif evidence_hits >= 1:
        score += 2
        reasons.append(f"Limited exhibits ({evidence_hits} markers) (+2)")

    # ── Friendly-witness dampener (negative) ─────────────────────
    if is_defense_side and not is_defendant:
        no_prior = "no prior sworn" in prior.lower() or "has not made prior" in prior.lower()
        if is_expert:
            score -= 15
            reasons.append("Friendly expert — dampened (-15)")
        elif no_prior:
            score -= 12
            reasons.append("Friendly fact witness, no prior sworn statements — dampened (-12)")
        else:
            score -= 8
            reasons.append("Friendly fact witness — dampened (-8)")

    score = max(1, min(100, score))
    level = _label_from_score(score)

    return {
        "witness_name": meta["witness_name"],
        "side": meta["side"],
        "role": v["witness_role"],
        "aggression_score": score,
        "aggression_level": level,
        "scoring_reasons": reasons,
    }


def score_vulnerability(witness: dict, aggression_score: int) -> dict:
    """Pre-deposition vulnerability assessment on the 5 rubric dimensions.

    Since there is no transcript yet, this predicts where the witness is
    most likely to struggle based on their profile, giving the coaching
    team a baseline before the session starts.

    The aggression_score (1-100) influences how much pressure is expected
    and adjusts composure predictions accordingly.
    """
    v = witness["variables"]
    facts = v.get("extracted_facts", "")
    prior = v.get("prior_statements", "")
    role = v.get("witness_role", "").lower()
    side = witness["_meta"].get("side", "").lower()
    corpus = f"{facts} {prior}"
    corpus_lower = corpus.lower()

    composure = 70
    tactical = 70
    professionalism = 70
    directness = 70
    consistency = 70

    rationale = {}

    # --- Composure ---
    threat_count = _count_signals(corpus, THREAT_SIGNALS)
    if "defendant" in role:
        composure -= 15
    if threat_count >= 3:
        composure -= 15
    elif threat_count >= 2:
        composure -= 10
    elif threat_count >= 1:
        composure -= 5
    pressure_penalty = int((aggression_score - 50) * 0.2) if aggression_score > 50 else 0
    composure -= pressure_penalty
    rationale["composure_reasoning"] = (
        f"{'Defendant under direct scrutiny' if 'defendant' in role else 'Witness'} "
        f"with {threat_count} emotional/confrontational signals. "
        f"Aggression score {aggression_score}/100 "
        f"{'applies heavy pressure (-' + str(pressure_penalty) + ')' if pressure_penalty > 0 else 'is within comfort range'}."
    )

    # --- Tactical Discipline ---
    claim_count = len(re.findall(r"claims|maintains|states|alleges|admits", corpus_lower))
    explanation_markers = len(re.findall(r"philosophical|sensitive|acknowledges|observation", corpus_lower))
    if claim_count >= 4:
        tactical -= 20
    elif claim_count >= 3:
        tactical -= 15
    elif claim_count >= 1:
        tactical -= 5
    if explanation_markers >= 2:
        tactical -= 15
    elif explanation_markers >= 1:
        tactical -= 10
    rationale["tactical_discipline_reasoning"] = (
        f"{claim_count} voluntary-claim markers and {explanation_markers} explanation-tendency signals. "
        f"{'High risk of filling silence and over-contextualizing.' if explanation_markers >= 1 else 'Moderate volunteering risk.'}"
    )

    # --- Professionalism ---
    if "defendant" in role or threat_count >= 2:
        professionalism -= 15
    elif threat_count >= 1:
        professionalism -= 5
    if side == "prosecution" and "expert" not in role:
        professionalism += 5
    rationale["professionalism_reasoning"] = (
        f"{'History of confrontational behavior reduces baseline.' if threat_count else 'No confrontational history.'} "
        f"{'Prosecution witnesses typically maintain courtroom decorum.' if side == 'prosecution' else ''}"
    )

    # --- Directness ---
    recall_risk = len(re.findall(r"do not recall|don't recall|not recall|uncertain|reservations", corpus_lower))
    denial_count = len(re.findall(r"denies|denied|deny", corpus_lower))
    if recall_risk >= 3:
        directness -= 20
    elif recall_risk >= 2:
        directness -= 15
    elif recall_risk >= 1:
        directness -= 5
    if denial_count >= 3:
        directness -= 15
    elif denial_count >= 2:
        directness -= 10
    elif denial_count >= 1:
        directness -= 3
    rationale["directness_reasoning"] = (
        f"{recall_risk} recall-hedging signals and {denial_count} blanket denials. "
        f"{'High evasion risk — interrogator will need to loop and rephrase.' if (recall_risk + denial_count) >= 3 else 'Moderate evasion profile.'}"
    )

    # --- Consistency ---
    contradiction_count = _count_signals(corpus, CONTRADICTION_SIGNALS)
    if contradiction_count >= 5:
        consistency -= 25
    elif contradiction_count >= 4:
        consistency -= 20
    elif contradiction_count >= 3:
        consistency -= 15
    elif contradiction_count >= 2:
        consistency -= 10
    elif contradiction_count >= 1:
        consistency -= 5
    rationale["consistency_reasoning"] = (
        f"{contradiction_count} contradiction/inconsistency signals across prior statements and facts. "
        f"{'Highly vulnerable to looping questions that resurface earlier answers.' if contradiction_count >= 3 else 'Moderate endurance risk.'}"
    )

    composure = max(1, min(100, composure))
    tactical = max(1, min(100, tactical))
    professionalism = max(1, min(100, professionalism))
    directness = max(1, min(100, directness))
    consistency = max(1, min(100, consistency))

    return {
        "analysis_rationale": rationale,
        "spider_chart_scores": {
            "composure": composure,
            "tactical_discipline": tactical,
            "professionalism": professionalism,
            "directness": directness,
            "consistency": consistency,
        },
    }
