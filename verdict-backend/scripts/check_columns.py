import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import AsyncSessionLocal
from sqlalchemy import text

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='Case' ORDER BY column_name"))
        cols = [r[0] for r in result.fetchall()]
        print('Columns in Case table:', cols)
        for col in ['extractedFacts', 'priorStatements', 'exhibitList', 'focusAreas']:
            assert col in cols, f'MISSING {col}'
        print('All 4 columns confirmed in DB')

asyncio.run(check())
