import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as db:
        firms = await db.execute(text('SELECT id, name, slug FROM "Firm" LIMIT 5'))
        print("Firms:", firms.fetchall())
        users = await db.execute(text('SELECT id, email, "firmId" FROM "User" LIMIT 5'))
        print("Users:", users.fetchall())
        cases = await db.execute(text('SELECT id, name FROM "Case" LIMIT 5'))
        print("Cases:", cases.fetchall())

asyncio.run(check())
