import asyncio, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import AsyncSessionLocal
from app.models.case import Case
from sqlalchemy import select

async def check():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Case).where(Case.id == 'utah_v_gunn'))
        case = result.scalar_one_or_none()
        assert case is not None, 'Case not found'
        assert case.extracted_facts and len(case.extracted_facts) > 50, 'extracted_facts empty'
        assert case.prior_statements and len(case.prior_statements) > 50, 'prior_statements empty'
        assert case.exhibit_list and len(case.exhibit_list) > 50, 'exhibit_list empty'
        assert case.focus_areas and len(case.focus_areas) > 50, 'focus_areas empty'
        print(f'Case: {case.name}')
        print(f'Facts: {case.extracted_facts[:100]}...')
        print(f'Prior statements: {case.prior_statements[:100]}...')
        print(f'Exhibit list: {case.exhibit_list[:100]}...')
        print(f'Focus areas: {case.focus_areas[:100]}...')
        print('ALL CHECKS PASSED - interrogator has data to work with')

        # Also show all cases
        all_result = await db.execute(select(Case.id, Case.name, Case.extracted_facts).order_by(Case.name))
        rows = all_result.fetchall()
        print(f'\nAll {len(rows)} cases in DB:')
        for row in rows:
            status = "[OK]" if row[2] else "[NO FACTS]"
            print(f'  {status} {row[1]} ({row[0]})')

asyncio.run(check())
