from fastapi import APIRouter, Depends
from .schemas import FeedbackRequest, FeedbackResponse
from .service import feedback_store
from ..deps import get_current_user, require_role
from ..auth.service import User

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest, user: User = Depends(get_current_user)):
    feedback_store.add(user.id, payload.conversationId, payload.rating, payload.comment)
    count, avg = feedback_store.stats()
    return FeedbackResponse(accepted=True, count=count, average=avg)


@router.get("/stats")
async def feedback_stats(user: User = Depends(require_role("admin"))):
    count, avg = feedback_store.stats()
    return {"count": count, "average": avg}
