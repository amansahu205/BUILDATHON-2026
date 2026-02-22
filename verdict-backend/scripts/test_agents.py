"""Test the question + objection agents on Railway."""
import asyncio
import httpx
import json

BASE = "https://verdict-backend-production.up.railway.app/api/v1"
SESSION_ID = "e214022c-667b-477b-a3d4-5a2f449395cd"


async def main():
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as c:
        r = await c.post(
            f"{BASE}/auth/login",
            json={"email": "sarah.chen@demo.com", "password": "Demo!Pass123"},
        )
        token = r.json()["data"]["tokens"]["accessToken"]
        h = {"Authorization": f"Bearer {token}"}
        print("Login OK")

        # --- Question agent (SSE) ---
        print("\n=== Question Agent ===")
        question_text = ""
        async with c.stream(
            "POST",
            f"{BASE}/sessions/{SESSION_ID}/agents/question",
            headers=h,
            json={"questionNumber": 3, "currentTopic": "insider trading", "priorAnswer": None},
        ) as stream:
            async for line in stream.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = json.loads(line[6:])
                t = payload.get("type")
                if t == "QUESTION_CHUNK":
                    question_text += payload["text"]
                    print(payload["text"], end="", flush=True)
                elif t == "QUESTION_END":
                    print(f"\n[QUESTION_END] full: {payload.get('fullText','')[:80]}")
                elif t == "QUESTION_START":
                    print(f"[QUESTION_START q#{payload.get('questionNumber')}]")

        # --- Objection agent ---
        print("\n\n=== Objection Copilot ===")
        test_q = question_text or "When you directed your CFO to make the numbers work, did you know that was fraudulent AND that investors would lose money?"
        r2 = await c.post(
            f"{BASE}/sessions/{SESSION_ID}/agents/objection",
            headers=h,
            json={"questionNumber": 3, "questionText": test_q},
        )
        print("Status:", r2.status_code)
        print(json.dumps(r2.json(), indent=2))


asyncio.run(main())
