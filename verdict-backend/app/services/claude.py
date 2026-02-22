from anthropic import AsyncAnthropic
from typing import AsyncGenerator
from app.config import settings

client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def claude_chat(system_prompt: str, user_message: str, max_tokens: int = 1024) -> str:
    response = await client.messages.create(
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
    async with client.messages.stream(
        model=settings.ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
