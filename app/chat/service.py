from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict
from ..models.conversation import Conversation, Message
from ..config import Settings


class ChatService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._conversations: Dict[str, Conversation] = {}

    def get_conversation(self, cid: str) -> Conversation | None:
        return self._conversations.get(cid)

    def get_or_raise(self, cid: str, user_id: str) -> Conversation:
        conv = self._conversations.get(cid)
        if not conv or conv.user_id != user_id:
            raise ValueError("Conversation not found")
        return conv

    def create_conversation(self, user_id: str, first_message: str) -> Conversation:
        title = "New conversation"
        if self.settings.privacy_store_messages:
            title = " ".join(first_message.split()[:7])
        conv = Conversation.new(user_id=user_id, title=title)
        self._conversations[conv.id] = conv
        return conv

    def add_message(self, conv: Conversation, user_id: str | None, role: str, content: str | None):
        msg = Message(id=str(len(conv.messages) + 1), user_id=user_id, role=role, content=content, timestamp=datetime.now(timezone.utc))
        conv.messages.append(msg)
        conv.updated_at = msg.timestamp

    def list_user_conversations(self, user_id: str):
        return [c for c in self._conversations.values() if c.user_id == user_id]

    def list_all_conversations(self):
        return list(self._conversations.values())

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        conv = self._conversations.get(conversation_id)
        if conv and conv.user_id == user_id:
            del self._conversations[conversation_id]
            return True
        return False
