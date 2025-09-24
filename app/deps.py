from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from passlib.context import CryptContext

from .config import get_settings, Settings
from .auth.service import UserService, User
from .ai.base import AIClient
from .ai.openai_client import OpenAIClient
from .ai.gpt4all_client import GPT4AllClient
from .ai.fallback_client import FallbackAIClient
from .ai.mock_client import MockAIClient
from .ai.gemini_client import GeminiClient
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer(auto_error=False)

_user_service = UserService(pwd_context=pwd_context)


def get_user_service() -> UserService:
    return _user_service


def get_ai_client(settings: Settings = Depends(get_settings)) -> AIClient:
    provider = settings.ai_provider.lower()
    if provider == "mock":
        return MockAIClient()
    if provider == "openai":
        # If no API key or a placeholder key (contains '...'), use mock directly.
        key = settings.openai_api_key or os.getenv("OPENAI_API_KEY") or ""
        if (not key) or ("..." in key):
            return MockAIClient()
        primary = OpenAIClient(settings)
        # Build a fallback chain: OpenAI -> (optional GPT4All) -> Mock
        client: AIClient = primary
        # Try GPT4All
        try:
            gpt4all_client = GPT4AllClient(settings)
            client = FallbackAIClient(client, gpt4all_client)
        except Exception:
            pass
        # Always add Mock as final safety net so chatting works offline / on API errors
        client = FallbackAIClient(client, MockAIClient())
        return client
    if provider == "gpt4all":
        return GPT4AllClient(settings)
    if provider == "gemini":
        key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY") or ""
        if (not key) or ("..." in key):
            return MockAIClient()
        try:
            primary: AIClient = GeminiClient(settings)
        except Exception:
            return MockAIClient()
        # Add Mock fallback always for resilience
        return FallbackAIClient(primary, MockAIClient())
    raise HTTPException(status_code=500, detail="Unknown AI_PROVIDER")


def create_access_token(sub: str, role: str, settings: Settings) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expires_min)
    payload = {"sub": sub, "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    settings: Settings = Depends(get_settings),
    user_service: UserService = Depends(get_user_service),
) -> User:
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = creds.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_role(role: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency
