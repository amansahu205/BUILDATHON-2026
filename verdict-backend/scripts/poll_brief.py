"""Poll brief status for session that auto-triggered brief."""
import httpx, asyncio, json

BASE = "https://verdict-backend-production.up.railway.app/api/v1"
SID = "83c0180e-c18d-4b0b-81ff-f2f23d9cd80e"


async def main():
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as c:
        r = await c.post(f"{BASE}/auth/login", json={"email": "sarah.chen@demo.com", "password": "Demo!Pass123"})
        token = r.json()["data"]["tokens"]["accessToken"]
        h = {"Authorization": f"Bearer {token}"}

        for i in range(10):
            await asyncio.sleep(5)
            r4 = await c.get(f"{BASE}/briefs/generate/{SID}/status", headers=h)
            d = r4.json()["data"]
            print(f"[{i+1}] progress={d['progress']} eta={d['eta']} briefId={d['briefId']}")
            if d["briefId"]:
                print("✅ Brief generated! ID:", d["briefId"])
                r5 = await c.get(f"{BASE}/briefs/{d['briefId']}", headers=h)
                brief = r5.json()["data"]
                print(f"  Score: {brief['sessionScore']}/100")
                print(f"  Recs: {brief['topRecommendations'][:2]}")
                print(f"  Narrative: {(brief['narrativeText'] or '')[:200]}")
                break

asyncio.run(main())
