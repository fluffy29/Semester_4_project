from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class ConversationMeta(BaseModel):
    id: str
    title: str
    createdAt: datetime
    updatedAt: datetime


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: List[dict]
    redacted: bool = False


class DeleteResponse(BaseModel):
    deleted: bool


class RenameRequest(BaseModel):
    title: str

class RenameResponse(BaseModel):
    renamed: bool
