from fastapi import APIRouter, Depends, HTTPException
from .schemas import LoginRequest, TokenResponse
from ..deps import get_settings, get_user_service, create_access_token
from ..config import Settings
from ..auth.service import UserService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    settings: Settings = Depends(get_settings),
    user_service: UserService = Depends(get_user_service),
) -> TokenResponse:
    """Authenticate a user and return a JWT access token."""
    user = user_service.get_user_by_email(payload.email)
    if not user or not user_service.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id, user.role, settings)
    return TokenResponse(access_token=token)
