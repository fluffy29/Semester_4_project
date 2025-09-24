from fastapi import APIRouter, Depends, HTTPException
from .schemas import ChatRequest, ChatResponse
from ..deps import get_settings, get_current_user, get_ai_client
from ..config import Settings
from ..auth.service import User
from ..ai.base import AIClient
from .service import ChatService
from ..ai.plugins import plugins

router = APIRouter(prefix="/chat", tags=["chat"])

_chat_service: ChatService | None = None


def get_chat_service(settings: Settings = Depends(get_settings)) -> ChatService:
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService(settings)
    return _chat_service


MAX_INPUT_LEN = 4000


@router.post("/ephemeral", response_model=ChatResponse)
async def chat_ephemeral(
    payload: ChatRequest,
    settings: Settings = Depends(get_settings),
    user: User = Depends(get_current_user),
    ai: AIClient = Depends(get_ai_client),
):
    if len(payload.message) > MAX_INPUT_LEN:
        raise HTTPException(status_code=400, detail="Message too long")
    history = [{"role": "user", "content": payload.message}]
    ctx = {"user_id": user.id, "conversation_id": None, "ephemeral": True}
    history = plugins.run_before(history, ctx)
    result = await ai.chat(history, settings.max_tokens, settings.temperature)
    reply = plugins.run_after(result["reply"], ctx)
    return ChatResponse(conversationId=None, reply=reply, usage=result.get("usage", {}), provider=settings.ai_provider, ephemeral=True)


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    settings: Settings = Depends(get_settings),
    user: User = Depends(get_current_user),
    ai: AIClient = Depends(get_ai_client),
    chat_service: ChatService = Depends(get_chat_service),
):
    if len(payload.message) > MAX_INPUT_LEN:
        raise HTTPException(status_code=400, detail="Message too long")

    if payload.conversationId:
        conv = chat_service.get_conversation(payload.conversationId)
        if not conv or conv.user_id != user.id:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv = chat_service.create_conversation(user.id, payload.message)

    if settings.privacy_store_messages:
        chat_service.add_message(conv, user.id, "user", payload.message)
    else:
        chat_service.add_message(conv, user.id, "user", None)

    if settings.privacy_store_messages:
        history_messages = [
            {"role": m.role, "content": m.content}
            for m in conv.messages
            if m.content
        ]
    else:
        history_messages = [{"role": "user", "content": payload.message}]

    ctx = {"user_id": user.id, "conversation_id": conv.id, "ephemeral": False}
    history_messages = plugins.run_before(history_messages, ctx)
    result = await ai.chat(history_messages, settings.max_tokens, settings.temperature)
    reply = plugins.run_after(result["reply"], ctx)

    if settings.privacy_store_messages:
        chat_service.add_message(conv, None, "assistant", reply)
    else:
        chat_service.add_message(conv, None, "assistant", None)

    return ChatResponse(conversationId=conv.id, reply=reply, usage=result.get("usage", {}), provider=settings.ai_provider, ephemeral=False)
