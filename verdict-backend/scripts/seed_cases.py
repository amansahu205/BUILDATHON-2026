"""
Seed the 5 demo cases from verdict_cases.json into PostgreSQL.
Run from verdict-backend/: python scripts/seed_cases.py

Requires the main seed to have run first (python scripts/seed.py)
so that the demo firm (firm-demo) and users exist.
"""
import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import AsyncSessionLocal
from app.models.firm import Firm
from app.models.user import User
from app.models.case import Case
from app.models.witness import Witness
from sqlalchemy import select

CASES_FILE = Path(__file__).parent.parent / "data" / "verdict_cases.json"

CASE_TYPE_MAP = {
    "Personal Injury — Transit Negligence": "OTHER",
    "Criminal — Securities Fraud": "OTHER",
    "Civil — Breach of Contract / Construction Defect": "CONTRACT_BREACH",
    "Medical Malpractice — Informed Consent": "MEDICAL_MALPRACTICE",
    "Civil — Fiduciary Breach / Elder Financial Abuse": "COMMERCIAL_DISPUTE",
}


async def main():
    if not CASES_FILE.exists():
        raise FileNotFoundError(f"verdict_cases.json not found at {CASES_FILE}")

    cases_raw = json.loads(CASES_FILE.read_text())
    print(f"Loaded {len(cases_raw)} cases from JSON")

    async with AsyncSessionLocal() as db:
        # Find the demo firm (works regardless of which seed created it)
        firm_result = await db.execute(
            select(Firm).where(Firm.slug == "demo-law-group")
        )
        firm = firm_result.scalar_one_or_none()
        if not firm:
            # Fall back to any firm
            firm_result = await db.execute(select(Firm).limit(1))
            firm = firm_result.scalar_one_or_none()
        if not firm:
            raise RuntimeError("No firm found in DB. Run the main seed first: python scripts/seed.py")

        user_result = await db.execute(
            select(User).where(User.firm_id == firm.id).order_by(User.created_at)
        )
        owner = user_result.scalars().first()
        if not owner:
            raise RuntimeError(f"No user found for firm {firm.id}. Run the main seed first.")

        print(f"Using firm_id={firm.id}, owner_id={owner.id} ({owner.email})")

        seeded = 0
        updated = 0
        skipped = 0

        for raw in cases_raw:
            existing_result = await db.execute(select(Case).where(Case.id == raw["id"]))
            existing_case = existing_result.scalar_one_or_none()

            dep_date = None
            try:
                dep_date = datetime.strptime(raw["deposition_date"], "%Y-%m-%d")
            except (ValueError, KeyError):
                pass

            case_type = CASE_TYPE_MAP.get(raw.get("case_type", ""), "OTHER")

            if existing_case:
                # Update the existing case with full data (witness fields, facts, etc.)
                existing_case.witness_name = raw.get("witness_name", "")
                existing_case.witness_role = raw.get("witness_role", "")
                existing_case.aggression_level = raw.get("aggression_level", "Medium")
                existing_case.extracted_facts = raw.get("extracted_facts", "")
                existing_case.prior_statements = raw.get("prior_statements", "")
                existing_case.exhibit_list = raw.get("exhibit_list", "")
                existing_case.focus_areas = raw.get("focus_areas", "")
                existing_case.opposing_party = raw.get("opposing_party", existing_case.opposing_party)
                print(f"  UPDATE (exists): {raw['case_name']}")
                case = existing_case
            else:
                case = Case(
                    id=raw["id"],
                    firm_id=firm.id,
                    owner_id=owner.id,
                    case_name=raw["case_name"],
                    case_type=case_type,
                    opposing_party=raw.get("opposing_party", ""),
                    deposition_date=dep_date,
                    witness_name=raw.get("witness_name", ""),
                    witness_role=raw.get("witness_role", ""),
                    aggression_level=raw.get("aggression_level", "Medium"),
                    extracted_facts=raw.get("extracted_facts", ""),
                    prior_statements=raw.get("prior_statements", ""),
                    exhibit_list=raw.get("exhibit_list", ""),
                    focus_areas=raw.get("focus_areas", ""),
                )
                db.add(case)
            await db.flush()

            # Parse witness name (format: "Name; Role/Title")
            witness_full = raw.get("witness_name", "Unknown")
            witness_name = witness_full.split(";")[0].strip()
            witness_role_notes = raw.get("witness_role", "")
            role_lower = witness_role_notes.lower()

            if "defendant" in role_lower or "ceo" in role_lower or "owner" in role_lower or "general contractor" in role_lower:
                witness_role = "DEFENDANT"
            elif "expert" in role_lower:
                witness_role = "EXPERT"
            elif "plaintiff" in role_lower:
                witness_role = "PLAINTIFF"
            elif "corporate representative" in role_lower or "route supervisor" in role_lower:
                witness_role = "CORPORATE_REPRESENTATIVE"
            else:
                witness_role = "OTHER"

            # Upsert witness record
            existing_witness = await db.execute(
                select(Witness).where(Witness.case_id == raw["id"])
            )
            w = existing_witness.scalars().first()
            if w:
                w.name = witness_name
                w.role = witness_role
                w.notes = witness_role_notes
            else:
                w = Witness(
                    case_id=raw["id"],
                    firm_id=firm.id,
                    name=witness_name,
                    email=f"witness.{raw['id']}@verdictdemo.com",
                    role=witness_role,
                    notes=witness_role_notes,
                )
                db.add(w)

            if existing_case:
                print(f"  UPDATED: {raw['case_name']} — witness: {witness_name} ({witness_role})")
                updated += 1
            else:
                print(f"  SEEDED: {raw['case_name']} — witness: {witness_name} ({witness_role})")
                seeded += 1

        await db.commit()

    print(f"\nDone. Seeded: {seeded}, Updated: {updated}, Skipped: {skipped}")
    print("\nVerifying DB...")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Case.id, Case.case_name, Case.extracted_facts).order_by(Case.case_name)
        )
        rows = result.fetchall()
        for row in rows:
            status = "[OK]" if row[2] else "[NO FACTS]"
            print(f"  {status} {row[1]} ({row[0]})")


if __name__ == "__main__":
    asyncio.run(main())
