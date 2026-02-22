from anthropic import AsyncAnthropic
from typing import AsyncGenerator
from app.config import settings

_client: AsyncAnthropic | None = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        # Strip accidental surrounding quotes added via Railway dashboard
        api_key = settings.ANTHROPIC_API_KEY.strip().strip('"').strip("'")
        _client = AsyncAnthropic(api_key=api_key)
    return _client


async def claude_chat(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    response = await _get_client().messages.create(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    block = response.content[0]
    if block.type != "text":
        raise ValueError("Unexpected Claude response type")
    return block.text


async def claude_stream(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 512,
) -> AsyncGenerator[str, None]:
    async with _get_client().messages.stream(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
