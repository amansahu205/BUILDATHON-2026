import asyncio
import json
import logging
from app.agents.objection import analyze_for_objections, search_fre_rules
from app.config import settings

logging.basicConfig(level=logging.INFO)

async def main():
    print(f'Model config: {settings.ANTHROPIC_MODEL}')
    print(f'Databricks Host: {settings.DATABRICKS_HOST}')
    print('Testing Databricks search...')
    
    try:
        rules = await search_fre_rules('Is it true that John told you he saw the accident?', top_k=2)
        for i, r in enumerate(rules):
            content = r.get('content', '')[:100]
            print(f'Match {i+1} : {content}...')
    except Exception as e:
        print(f"Databricks search failed: {e}")
        
    print('\nTesting full Objection Copilot agent...')
    try:
        result = await analyze_for_objections('What did the doctor tell you about your condition?', 'test-session')
        print('Agent Response:')
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Agent analysis failed: {e}")

if __name__ == '__main__':
    asyncio.run(main())
