from typing import Any
from .base import AIClient


class FallbackAIClient(AIClient):
    """Try primary model; on failure, try fallback (if provided)."""

    def __init__(self, primary: AIClient, fallback: AIClient | None = None):
        self.primary = primary
        self.fallback = fallback

    async def chat(self, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> dict[str, Any]:
        chain: list[str] = []
        try:
            chain.append(type(self.primary).__name__)
            result = await self.primary.chat(messages, max_tokens, temperature)
            result.setdefault("usage", {})["provider_chain"] = chain
            return result
        except Exception:
            if not self.fallback:
                raise
            chain.append(type(self.fallback).__name__)
            result = await self.fallback.chat(messages, max_tokens, temperature)
            result.setdefault("usage", {})["provider_chain"] = chain
            return result
