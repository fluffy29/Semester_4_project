from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
import uuid


@dataclass
class Message:
    id: str
    user_id: str | None
    role: str
    content: str | None
    timestamp: datetime


@dataclass
class Conversation:
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Message] = field(default_factory=list)

    @staticmethod
    def new(user_id: str, title: str) -> Conversation:
        now = datetime.now(timezone.utc)
        return Conversation(id=str(uuid.uuid4()), user_id=user_id, title=title, created_at=now, updated_at=now)
