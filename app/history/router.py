from fastapi import APIRouter, Depends, HTTPException
from ..deps import get_settings, get_current_user, require_role
from ..config import Settings
from ..auth.service import User
from ..chat.router import get_chat_service
from .service import HistoryService
from .schemas import ConversationMeta, ConversationDetail, DeleteResponse, RenameRequest, RenameResponse

router = APIRouter(prefix="/history", tags=["history"])


def get_history_service(settings: Settings = Depends(get_settings)) -> HistoryService:
    chat_service = get_chat_service(settings)
    return HistoryService(chat_service)


@router.get("", response_model=list[ConversationMeta])
async def list_history(page: int = 1, pageSize: int = 20, settings: Settings = Depends(get_settings), user: User = Depends(require_role("student"))):
    hs = get_history_service(settings)
    items = hs.list_user_conversations(user.id, page, pageSize)
    result = [
        ConversationMeta(id=c.id, title=c.title, createdAt=c.created_at, updatedAt=c.updated_at) for c in items
    ]
    return result


@router.get("/{conversationId}", response_model=ConversationDetail)
async def get_history_item(conversationId: str, settings: Settings = Depends(get_settings), user: User = Depends(require_role("student"))):
    hs = get_history_service(settings)
    c = hs.get_conversation(conversationId)
    if not c or c.user_id != user.id:
        raise HTTPException(status_code=404, detail="Not found")
    if settings.privacy_store_messages:
        messages = [
            {"id": m.id, "role": m.role, "content": m.content, "timestamp": m.timestamp.isoformat()} for m in c.messages
        ]
        return ConversationDetail(id=c.id, title=c.title, messages=messages, redacted=False)
    else:
        return ConversationDetail(id=c.id, title=c.title, messages=[], redacted=True)


@router.delete("/{conversationId}", response_model=DeleteResponse)
async def delete_history_item(conversationId: str, settings: Settings = Depends(get_settings), user: User = Depends(require_role("student"))):
    hs = get_history_service(settings)
    deleted = hs.delete_conversation(conversationId, user.id)
    return DeleteResponse(deleted=deleted)

@router.patch("/{conversationId}", response_model=RenameResponse)
async def rename_history_item(conversationId: str, payload: RenameRequest, settings: Settings = Depends(get_settings), user: User = Depends(require_role("student"))):
    hs = get_history_service(settings)
    ok = hs.rename_conversation(conversationId, user.id, payload.title)
    return RenameResponse(renamed=ok)


admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get("/conversations", response_model=list[ConversationMeta])
async def admin_list_conversations(settings: Settings = Depends(get_settings), user: User = Depends(require_role("admin"))):
    hs = get_history_service(settings)
    items = hs.list_all_conversations()
    return [
        ConversationMeta(id=c.id, title=c.title, createdAt=c.created_at, updatedAt=c.updated_at) for c in items
    ]
