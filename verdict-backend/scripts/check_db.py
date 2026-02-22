import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import AsyncSessionLocal
from sqlalchemy import text
import logging
logging.disable(logging.CRITICAL)

async def check():
    async with AsyncSessionLocal() as db:
        firms = await db.execute(text('SELECT id, name, slug FROM "Firm" LIMIT 5'))
        print("Firms:", firms.fetchall())

        users = await db.execute(text('SELECT id, email, "firmId" FROM "User" LIMIT 5'))
        print("Users:", users.fetchall())

        # Check what columns Case table actually has now
        cols = await db.execute(text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'Case' ORDER BY ordinal_position
        """))
        print("Case columns:", [r[0] for r in cols.fetchall()])

        cases = await db.execute(text('SELECT id, "caseName", "caseType" FROM "Case" LIMIT 5'))
        print("Cases:", cases.fetchall())

asyncio.run(check())
