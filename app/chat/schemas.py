from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    conversationId: Optional[str] = None
    maxTokens: Optional[int] = None
    temperature: Optional[float] = None


class ChatResponse(BaseModel):
    conversationId: str | None
    reply: str
    usage: dict
    provider: str
    ephemeral: bool = False
