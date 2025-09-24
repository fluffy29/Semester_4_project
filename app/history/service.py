from __future__ import annotations
from typing import List
from ..chat.service import ChatService
from ..models.conversation import Conversation


class HistoryService:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    def list_user_conversations(self, user_id: str, page: int, page_size: int) -> List[Conversation]:
        items = sorted(self.chat_service.list_user_conversations(user_id), key=lambda c: c.updated_at, reverse=True)
        start = (page - 1) * page_size
        return items[start : start + page_size]

    def get_conversation(self, conversation_id: str) -> Conversation | None:
        return self.chat_service.get_conversation(conversation_id)

    def list_all_conversations(self) -> List[Conversation]:
        return self.chat_service.list_all_conversations()

    def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        return self.chat_service.delete_conversation(conversation_id, user_id)
