from typing import Any
import os
import httpx
from .base import AIClient
from ..config import Settings


class GeminiClient(AIClient):
    """Minimal Google Gemini (Generative Language) client using REST API.
    Expects GEMINI_API_KEY env or settings.gemini_api_key.
    Only sends the last N messages as context (simple memory window).
    """

    def __init__(self, settings: Settings, window: int = 12):
        self.api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        self.model = settings.gemini_model
        self.window = window
        # Endpoint format (public REST): https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

    async def chat(self, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> dict[str, Any]:
        # Gemini expects "contents" with role + parts. We'll take last window items.
        trimmed = messages[-self.window :]
        contents = []
        for m in trimmed:
            role = "user" if m.get("role") == "user" else "model"
            contents.append({"role": role, "parts": [{"text": m.get("content", "")}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        params = {"key": self.api_key}
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(self.base_url, params=params, json=payload)
            resp.raise_for_status()
            data = resp.json()
        try:
            reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            raise ValueError(f"Unexpected Gemini response: {data}")

        # Token accounting is approximate here since API returns metadata optionally.
        usage = {
            "promptTokens": sum(len(m.get("content", "").split()) for m in trimmed),
            "completionTokens": len(reply.split()),
        }
        usage["totalTokens"] = usage["promptTokens"] + usage["completionTokens"]
        return {"reply": reply, "usage": usage}
