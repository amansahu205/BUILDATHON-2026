import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext
from app.database import AsyncSessionLocal
from app.models.firm import Firm
from app.models.user import User
from app.models.case import Case
from app.models.witness import Witness
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PASSWORD_HASH = pwd_context.hash("Demo!Pass123")


async def main():
    async with AsyncSessionLocal() as db:
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

        sarah = User(firm_id="firm-demo", email="sarah.chen@demo.com", name="Sarah Chen", role="PARTNER", password_hash=PASSWORD_HASH, email_verified=True)
        james = User(firm_id="firm-demo", email="j.rodriguez@demo.com", name="James Rodriguez", role="ASSOCIATE", password_hash=PASSWORD_HASH, email_verified=True)
        admin = User(firm_id="firm-demo", email="admin@demo.com", name="Admin User", role="ADMIN", password_hash=PASSWORD_HASH, email_verified=True)
        db.add_all([sarah, james, admin])
        await db.flush()

        case1 = Case(id="seed-case-chen-v-metro", firm_id="firm-demo", owner_id=sarah.id, case_name="Chen v. Metropolitan Hospital", case_type="MEDICAL_MALPRACTICE", opposing_party="Defense Partners LLP")
        case2 = Case(id="seed-case-thompson-v-axiom", firm_id="firm-demo", owner_id=sarah.id, case_name="Thompson v. Axiom Industries", case_type="EMPLOYMENT_DISCRIMINATION", opposing_party="Axiom Legal Team")
        db.add_all([case1, case2])
        await db.flush()

        witness = Witness(id="seed-witness-emily-chen", case_id=case1.id, firm_id="firm-demo", name="Dr. Emily Chen", email="emily.chen@metro.com", role="DEFENDANT", notes="Known weakness: medication dosage timeline discrepancy")
        db.add(witness)

        await db.commit()
        print("✅ Seed complete")
        print(f"   firm_id : firm-demo")
        print(f"   users   : {sarah.id}, {james.id}, {admin.id}")
        print(f"   cases   : {case1.id}, {case2.id}")
        print(f"   witness : {witness.id}")
        print("\nLogin: sarah.chen@demo.com / Demo!Pass123")


if __name__ == "__main__":
    asyncio.run(main())
