from abc import ABC, abstractmethod
from typing import Any


class AIClient(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict[str, str]], max_tokens: int, temperature: float) -> dict[str, Any]:
        raise NotImplementedError
