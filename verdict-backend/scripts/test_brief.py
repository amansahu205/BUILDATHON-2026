"""Test brief generation end-to-end on Railway."""
import asyncio
import httpx
import json
import time

BASE = "https://verdict-backend-production.up.railway.app/api/v1"


async def main():
    async with httpx.AsyncClient(follow_redirects=True, timeout=120) as c:
        # Login
        r = await c.post(f"{BASE}/auth/login", json={"email": "sarah.chen@demo.com", "password": "Demo!Pass123"})
        token = r.json()["data"]["tokens"]["accessToken"]
        h = {"Authorization": f"Bearer {token}"}
        print("✅ Login OK")

        # Create + start a session with some questions
        r2 = await c.post(f"{BASE}/sessions", headers=h, json={
            "caseId": "lyman_v_cctd",
            "witnessId": "c00d435e-4f63-4e6c-8a27-69f61137adb2",
            "durationMinutes": 30,
            "focusAreas": ["shift violations", "prior statements"],
            "aggression": "ELEVATED",
            "objectionCopilotEnabled": True,
        })
        sess = r2.json()["data"]
        sid = sess["id"]
        print(f"✅ Session: {sid}")

        await c.post(f"{BASE}/sessions/{sid}/start", headers=h)
        print("✅ Started")

        # Ask 2 questions and record answers to populate transcript
        for qnum in [1, 2]:
            q_text = ""
            async with c.stream("POST", f"{BASE}/sessions/{sid}/agents/question", headers=h,
                                json={"questionNumber": qnum, "currentTopic": "shift policy violations"}) as s:
                async for line in s.aiter_lines():
                    if line.startswith("data: "):
                        p = json.loads(line[6:])
                        if p.get("type") == "QUESTION_CHUNK":
                            q_text += p["text"]
            print(f"  Q{qnum}: {q_text[:100]}...")

            # Check objection on question
            await c.post(f"{BASE}/sessions/{sid}/agents/objection", headers=h,
                         json={"questionNumber": qnum, "questionText": q_text})

        # End session
        await c.post(f"{BASE}/sessions/{sid}/end", headers=h)
        print("✅ Session ended")

        # Trigger brief generation
        r3 = await c.post(f"{BASE}/briefs/generate/{sid}", headers=h)
        print("Brief trigger status:", r3.status_code)
        brief_resp = r3.json()
        print(json.dumps(brief_resp, indent=2))
        brief_id = brief_resp["data"]["briefId"]

        # Poll until complete (max 60s)
        print(f"\nPolling brief {brief_id}...")
        for attempt in range(12):
            await asyncio.sleep(5)
            r4 = await c.get(f"{BASE}/briefs/{brief_id}", headers=h)
            brief = r4.json()["data"]
            status_text = brief.get("narrativeText", "")[:60]
            print(f"  [{attempt+1}] score={brief.get('sessionScore')} | text={status_text!r}")
            if brief.get("sessionScore", 0) > 0 and "Generating" not in (brief.get("narrativeText") or ""):
                print("\n✅ BRIEF GENERATED!")
                print(f"  Score: {brief['sessionScore']}/100")
                print(f"  Consistency: {brief['consistencyRate']}")
                print(f"  Weakness map: {brief.get('weaknessMapScores')}")
                print(f"  Recommendations:")
                for rec in (brief.get("topRecommendations") or []):
                    print(f"    - {rec}")
                print(f"\n  Narrative:\n  {brief['narrativeText'][:500]}")
                if brief.get("pdfS3Key"):
                    print(f"\n  ✅ PDF generated: {brief['pdfS3Key']}")
                break
        else:
            print("⚠️  Brief still generating after 60s — check Railway logs")
            print(f"  Raw: {json.dumps(brief, indent=2)[:500]}")


asyncio.run(main())
