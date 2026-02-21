import httpx

from ..config import settings


class ElevenLabsService:
    """Async client for the ElevenLabs Conversational AI REST API."""

    def __init__(self) -> None:
        self._base = settings.elevenlabs_base_url
        self._headers = {
            "xi-api-key": settings.elevenlabs_api_key,
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base,
            headers=self._headers,
            timeout=30.0,
        )

    # ── Agent prompt patching ────────────────────────────────────

    async def patch_agent_prompt(
        self,
        agent_id: str,
        system_prompt: str,
        first_message: str | None = None,
    ) -> dict:
        """PATCH the agent's system prompt (and optionally first message)
        so the next conversation uses case-specific context."""

        body: dict = {
            "conversation_config": {
                "agent": {
                    "prompt": {
                        "prompt": system_prompt,
                    },
                },
            },
        }
        if first_message is not None:
            body["conversation_config"]["agent"]["first_message"] = first_message

        async with self._client() as client:
            resp = await client.patch(f"/convai/agents/{agent_id}", json=body)
            resp.raise_for_status()
            return resp.json()

    # ── Signed conversation token ────────────────────────────────

    async def get_conversation_token(self, agent_id: str) -> str:
        """Get a short-lived signed URL / token the frontend can use
        to start a WebRTC session without exposing the API key."""

        async with self._client() as client:
            resp = await client.get(
                "/convai/conversation/get-signed-url",
                params={"agent_id": agent_id},
            )
            resp.raise_for_status()
            return resp.json()["signed_url"]

    # ── Conversation history ─────────────────────────────────────

    async def list_conversations(
        self,
        agent_id: str,
        cursor: str | None = None,
        page_size: int = 20,
    ) -> dict:
        params: dict = {"agent_id": agent_id, "page_size": page_size}
        if cursor:
            params["cursor"] = cursor

        async with self._client() as client:
            resp = await client.get("/convai/conversations", params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_conversation(self, conversation_id: str) -> dict:
        async with self._client() as client:
            resp = await client.get(f"/convai/conversations/{conversation_id}")
            resp.raise_for_status()
            return resp.json()

    # ── Agent info ───────────────────────────────────────────────

    async def get_agent(self, agent_id: str) -> dict:
        async with self._client() as client:
            resp = await client.get(f"/convai/agents/{agent_id}")
            resp.raise_for_status()
            return resp.json()


elevenlabs_service = ElevenLabsService()
