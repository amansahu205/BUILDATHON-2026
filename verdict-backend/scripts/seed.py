import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.firm import Firm
from app.models.user import User
from app.models.case import Case
from app.models.witness import Witness
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PASSWORD_HASH = pwd_context.hash("Demo!Pass123")


async def get_or_create_firm(db):
    result = await db.execute(select(Firm).where(Firm.id == "firm-demo"))
    firm = result.scalar_one_or_none()
    if firm:
        print("   firm     : already exists — skipping")
        return firm
    firm = Firm(
        id="firm-demo",
        name="Demo Law Group LLP",
        slug="demo-law-group",
        seats=10,
        plan="professional",
        setup_complete=True,
        retention_days=90,
    )
    db.add(firm)
    await db.flush()
    print("   firm     : created")
    return firm


async def get_or_create_user(db, email, name, role):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        print(f"   user {email}: already exists — skipping")
        return user
    user = User(firm_id="firm-demo", email=email, name=name, role=role, password_hash=PASSWORD_HASH, email_verified=True)
    db.add(user)
    await db.flush()
    print(f"   user {email}: created ({user.id})")
    return user


async def get_or_create_case(db, case_id, owner_id, case_name, case_type, opposing_party):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if case:
        print(f"   case {case_id}: already exists — skipping")
        return case
    case = Case(id=case_id, firm_id="firm-demo", owner_id=owner_id, case_name=case_name, case_type=case_type, opposing_party=opposing_party)
    db.add(case)
    await db.flush()
    print(f"   case {case_id}: created")
    return case


async def get_or_create_witness(db, witness_id, case_id, name, email, role, notes):
    result = await db.execute(select(Witness).where(Witness.id == witness_id))
    witness = result.scalar_one_or_none()
    if witness:
        print(f"   witness {witness_id}: already exists — skipping")
        return witness
    witness = Witness(id=witness_id, case_id=case_id, firm_id="firm-demo", name=name, email=email, role=role, notes=notes)
    db.add(witness)
    await db.flush()
    print(f"   witness {witness_id}: created")
    return witness


async def main():
    async with AsyncSessionLocal() as db:
        await get_or_create_firm(db)

        sarah = await get_or_create_user(db, "sarah.chen@demo.com", "Sarah Chen", "PARTNER")
        await get_or_create_user(db, "j.rodriguez@demo.com", "James Rodriguez", "ASSOCIATE")
        await get_or_create_user(db, "admin@demo.com", "Admin User", "ADMIN")

        case1 = await get_or_create_case(db, "seed-case-chen-v-metro", sarah.id, "Chen v. Metropolitan Hospital", "MEDICAL_MALPRACTICE", "Defense Partners LLP")
        await get_or_create_case(db, "seed-case-thompson-v-axiom", sarah.id, "Thompson v. Axiom Industries", "EMPLOYMENT_DISCRIMINATION", "Axiom Legal Team")

        await get_or_create_witness(db, "seed-witness-emily-chen", case1.id, "Dr. Emily Chen", "emily.chen@metro.com", "DEFENDANT", "Known weakness: medication dosage timeline discrepancy")

        await db.commit()
        print("\n✅ Seed complete — Login: sarah.chen@demo.com / Demo!Pass123")


if __name__ == "__main__":
    asyncio.run(main())
