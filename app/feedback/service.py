from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import uuid4


@dataclass
class FeedbackItem:
    id: str
    user_id: str
    conversation_id: str | None
    rating: int
    comment: str | None
    created_at: datetime


class FeedbackStore:
    def __init__(self) -> None:
        self.items: List[FeedbackItem] = []

    def add(self, user_id: str, conversation_id: str | None, rating: int, comment: str | None):
        self.items.append(
            FeedbackItem(
                id=str(uuid4()),
                user_id=user_id,
                conversation_id=conversation_id,
                rating=rating,
                comment=comment,
                created_at=datetime.utcnow(),
            )
        )

    def stats(self) -> tuple[int, float]:
        if not self.items:
            return 0, 0.0
        total = len(self.items)
        avg = sum(i.rating for i in self.items) / total
        return total, round(avg, 2)


feedback_store = FeedbackStore()
