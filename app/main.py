from fastapi import FastAPI, Depends, Request, HTTPException
from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from time import time

from .config import get_settings, Settings
from dotenv import load_dotenv
from .auth.router import router as auth_router
from .chat.router import router as chat_router
from .history.router import router as history_router, admin_router as admin_history_router
from .feedback.router import router as feedback_router

load_dotenv()
app = FastAPI(title="GenAI Chat Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

WINDOW = 60
LIMIT = 60
_buckets: dict[str, list[float]] = {}


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    ip = request.client.host if request.client else "unknown"
    now = time()
    bucket = _buckets.setdefault(ip, [])
    bucket[:] = [t for t in bucket if now - t < WINDOW]
    if len(bucket) >= LIMIT:
        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
    bucket.append(now)
    return await call_next(request)


@app.get("/api/health")
async def health(settings: Settings = Depends(get_settings)):
    return {"status": "ok", "provider": settings.ai_provider}


app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(history_router, prefix="/api")
app.include_router(admin_history_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
