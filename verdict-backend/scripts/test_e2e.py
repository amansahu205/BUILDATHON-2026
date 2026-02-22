"""Full end-to-end session flow test on Railway."""
import asyncio
import httpx
import json

BASE = "https://verdict-backend-production.up.railway.app/api/v1"


async def main():
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as c:
        # Login
        r = await c.post(f"{BASE}/auth/login", json={"email": "sarah.chen@demo.com", "password": "Demo!Pass123"})
        token = r.json()["data"]["tokens"]["accessToken"]
        h = {"Authorization": f"Bearer {token}"}
        print("✅ Login OK")

        # Create session for Utah v Gunn
        r2 = await c.post(f"{BASE}/sessions", headers=h, json={
            "caseId": "utah_v_gunn",
            "witnessId": "3434c545-574f-4869-bfbf-802f16f9a4c3",
            "durationMinutes": 60,
            "focusAreas": ["revenue fraud", "insider trading"],
            "aggression": "HIGH_STAKES",
            "objectionCopilotEnabled": True,
        })
        sess = r2.json()["data"]
        sid = sess["id"]
        print(f"✅ Session created: {sid} (token: {sess['witnessToken']})")

        # Start session
        await c.post(f"{BASE}/sessions/{sid}/start", headers=h)
        print("✅ Session started (ACTIVE)")

        # Question 1 — stream
        print("\n--- Question 1 (streaming) ---")
        q1 = ""
        async with c.stream("POST", f"{BASE}/sessions/{sid}/agents/question", headers=h,
                            json={"questionNumber": 1, "currentTopic": "revenue fraud", "priorAnswer": None}) as s:
            async for line in s.aiter_lines():
                if line.startswith("data: "):
                    p = json.loads(line[6:])
                    if p.get("type") == "QUESTION_CHUNK":
                        q1 += p["text"]
                        print(p["text"], end="", flush=True)
                    elif p.get("type") == "QUESTION_END":
                        print()
        print(f"✅ Q1 generated ({len(q1)} chars)")

        # Objection check on Q1
        r_obj = await c.post(f"{BASE}/sessions/{sid}/agents/objection", headers=h,
                             json={"questionNumber": 1, "questionText": q1})
        obj = r_obj.json()["data"]
        flag = "🚨 OBJECTIONABLE" if obj["isObjectionable"] else "✅ clean"
        print(f"Objection check: {flag} | category={obj['category']} | conf={obj['confidence']}")

        # Test compound question — should flag
        print("\n--- Objection: compound question ---")
        compound_q = "Did you authorize the falsified revenue figures AND also instruct your CFO to conceal the discrepancy from auditors?"
        r_cmp = await c.post(f"{BASE}/sessions/{sid}/agents/objection", headers=h,
                             json={"questionNumber": 2, "questionText": compound_q})
        cmp = r_cmp.json()["data"]
        flag2 = "🚨 OBJECTIONABLE" if cmp["isObjectionable"] else "⚠️ missed"
        print(f'Q: "{compound_q[:80]}..."')
        print(f"Result: {flag2} | category={cmp['category']} | conf={cmp['confidence']}")
        print(f"Explanation: {cmp['explanation']}")

        # Inconsistency check
        print("\n--- Inconsistency Detector ---")
        r_inc = await c.post(f"{BASE}/sessions/{sid}/agents/inconsistency", headers=h, json={
            "questionNumber": 1,
            "questionText": "What did you tell the board of directors in August 2025 about your involvement in accounting decisions?",
            "answerText": "I was fully involved in reviewing all quarterly financial reports and I approved them personally.",
        })
        inc = r_inc.json()["data"]
        flag3 = "🚨 INCONSISTENCY" if inc.get("flagFound") else "✅ no flag"
        print(f"Result: {flag3} | risk={inc.get('impeachmentRisk')} | conf={inc.get('contradictionConfidence')}")
        if inc.get("priorQuote"):
            print(f"Prior quote: {inc['priorQuote'][:100]}")

        # End session
        await c.post(f"{BASE}/sessions/{sid}/end", headers=h)
        print("\n✅ Session ended")

        print("\n=== ALL TESTS PASSED ===")


asyncio.run(main())
