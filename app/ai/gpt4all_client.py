from typing import Any
from .base import AIClient
from ..config import Settings

try:
    from gpt4all import GPT4All
except Exception:
    GPT4All = None


class GPT4AllClient(AIClient):
    def __init__(self, settings: Settings):
        if GPT4All is None:
            raise RuntimeError("gpt4all package not installed. Install to use local model.")
        self.model_path = settings.gpt4all_model_path
        self._model = GPT4All(model_name=self.model_path)

    async def chat(self, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> dict[str, Any]:
        user_texts = [m["content"] for m in messages if m["role"] == "user"]
        prompt = user_texts[-1] if user_texts else "Hello"
        reply = self._model.generate(prompt, max_tokens=max_tokens, temp=temperature)
        prompt_tokens = sum(len(t.split()) for t in user_texts)
        completion_tokens = len(reply.split())
        return {
            "reply": reply,
            "usage": {
                "promptTokens": prompt_tokens,
                "completionTokens": completion_tokens,
                "totalTokens": prompt_tokens + completion_tokens,
            },
        }
