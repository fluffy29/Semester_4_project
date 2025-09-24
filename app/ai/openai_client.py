import os
import httpx
from typing import Any
from ..config import Settings
from .base import AIClient


class OpenAIClient(AIClient):
    def __init__(self, settings: Settings):
        self.api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        self.model = settings.openai_model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def chat(self, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.base_url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        try:
            choice = data["choices"][0]["message"]["content"]
        except Exception:
            raise ValueError(f"Unexpected OpenAI response: {data}")
        usage = data.get("usage", {})
        return {
            "reply": choice,
            "usage": {
                "promptTokens": usage.get("prompt_tokens", 0),
                "completionTokens": usage.get("completion_tokens", 0),
                "totalTokens": usage.get("total_tokens", 0),
            },
        }
