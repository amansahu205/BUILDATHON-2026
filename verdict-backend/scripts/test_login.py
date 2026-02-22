"""Quick login test — run from verdict-backend/ dir"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging; logging.disable(logging.CRITICAL)

from app.database import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def test_login():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "sarah.chen@demo.com"))
        user = result.scalar_one_or_none()
        if not user:
            print("ERROR: user sarah.chen@demo.com not found in DB")
            return
        print(f"✅ Found user: id={user.id} email={user.email} role={user.role}")
        print(f"   is_active={user.is_active}")
        print(f"   password_hash present: {bool(user.password_hash)}")
        if user.password_hash:
            ok = pwd_context.verify("Demo!Pass123", user.password_hash)
            print(f"   password verify: {ok}")
        else:
            print("   ERROR: password_hash is NULL — user can't log in")

asyncio.run(test_login())
