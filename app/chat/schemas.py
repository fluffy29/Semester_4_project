from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str
    conversationId: Optional[str] = None


class ChatResponse(BaseModel):
    conversationId: str | None
    reply: str
    usage: dict
    provider: str
    ephemeral: bool = False
