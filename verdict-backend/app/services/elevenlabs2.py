import httpx

from app.config import settings


class ElevenLabsService:
    """Async client for the ElevenLabs Conversational AI + TTS APIs."""

    def __init__(self) -> None:
        self._base = "https://api.elevenlabs.io/v1"
        self._headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json",
        }

    def _client(self, timeout: float = 30.0) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base,
            headers=self._headers,
            timeout=timeout,
        )

    # ── Signed conversation token ────────────────────────────────

    async def get_conversation_token(self, agent_id: str) -> str:
        """Get a short-lived signed URL the frontend uses to connect."""
        async with self._client() as client:
            resp = await client.get(
                "/convai/conversation/get-signed-url",
                params={"agent_id": agent_id},
            )
            resp.raise_for_status()
            return resp.json()["signed_url"]

    @staticmethod
    def build_conversation_override(
        system_prompt: str,
        first_message: str | None = None,
    ) -> dict:
        """Build a conversation_config_override dict.

        The frontend SDK passes this at connect time so the prompt is
        scoped to THIS conversation only — no shared-agent mutation,
        no race condition between concurrent sessions.
        """
        override: dict = {
            "agent": {
                "prompt": {"prompt": system_prompt},
            },
        }
        if first_message is not None:
            override["agent"]["first_message"] = first_message
        return override

    # ── Text-to-Speech (direct, non-conversational) ──────────────

    async def text_to_speech(
        self,
        text: str,
        voice_id: str | None = None,
        model_id: str | None = None,
        stability: float = 0.5,
        similarity_boost: float = 0.75,
    ) -> bytes:
        """Generate speech audio from text using a specific voice.

        Returns raw audio bytes (mpeg by default).
        """
        voice = voice_id or settings.ELEVENLABS_COACH_VOICE_ID
        model = model_id or "eleven_multilingual_v2"

        async with self._client(timeout=60.0) as client:
            resp = await client.post(
                f"/text-to-speech/{voice}",
                json={
                    "text": text,
                    "model_id": model,
                    "voice_settings": {
                        "stability": stability,
                        "similarity_boost": similarity_boost,
                    },
                },
            )
            resp.raise_for_status()
            return resp.content

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
