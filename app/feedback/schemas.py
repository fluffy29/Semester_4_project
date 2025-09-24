from pydantic import BaseModel, Field
from typing import Optional


class FeedbackRequest(BaseModel):
    conversationId: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    accepted: bool
    count: int
    average: float
