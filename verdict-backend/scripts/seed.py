import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from app.database import AsyncSessionLocal
from app.models.firm import Firm
from app.models.user import User
from app.models.case import Case
from app.models.witness import Witness
import uuid

# Use bcrypt directly to avoid passlib/bcrypt version clashes (passlib still verifies this)
PASSWORD_HASH = bcrypt.hashpw("Demo!Pass123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def main():
    from sqlalchemy import select, update
    async with AsyncSessionLocal() as db:
        # Idempotent: if firm already exists (by id or slug), just reset demo user passwords so login works
        existing = await db.execute(select(Firm).where((Firm.id == "firm-demo") | (Firm.slug == "demo-law-group")))
        if existing.scalar_one_or_none():
            # Update password hashes for demo users (in case they were created with broken passlib)
            r = await db.execute(
                select(User).where(
                    User.email.in_(["sarah.chen@demo.com", "j.rodriguez@demo.com", "admin@demo.com"]),
                )
            )
            for user in r.scalars().all():
                user.password_hash = PASSWORD_HASH
            await db.commit()
            print("✅ Demo user passwords reset. Login: sarah.chen@demo.com / Demo!Pass123")
            return

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

        case1 = Case(id="seed-case-chen-v-metro", firm_id="firm-demo", owner_id=sarah.id, name="Chen v. Metropolitan Hospital", case_type="MEDICAL_MALPRACTICE", opposing_firm="Defense Partners LLP")
        case2 = Case(id="seed-case-thompson-v-axiom", firm_id="firm-demo", owner_id=sarah.id, name="Thompson v. Axiom Industries", case_type="EMPLOYMENT_DISCRIMINATION", opposing_firm="Axiom Legal Team")
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
