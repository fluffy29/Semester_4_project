from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        populate_by_name=True,
        env_file=".env"
    )
    
    app_env: str = Field("dev", alias="APP_ENV")
    app_port: int = Field(8000, alias="APP_PORT")
    jwt_secret: str = Field("change_me", alias="JWT_SECRET")
    jwt_expires_min: int = Field(60, alias="JWT_EXPIRES_MIN")
    ai_provider: str = Field("openai", alias="AI_PROVIDER")
    openai_api_key: str | None = Field(None, alias="OPENAI_API_KEY")
    openai_model: str = Field("gpt-4o-mini", alias="OPENAI_MODEL")
    gpt4all_model_path: str = Field("./models/q4_0-orca-mini-3b.gguf", alias="GPT4ALL_MODEL_PATH")
    max_tokens: int = Field(512, alias="MAX_TOKENS")
    temperature: float = Field(0.4, alias="TEMPERATURE")
    privacy_store_messages: bool = Field(False, alias="PRIVACY_STORE_MESSAGES")


@lru_cache
def get_settings() -> Settings:
    return Settings(
        APP_ENV=os.getenv("APP_ENV", "dev"),
        APP_PORT=int(os.getenv("APP_PORT", "8000")),
        JWT_SECRET=os.getenv("JWT_SECRET", "change_me"),
        JWT_EXPIRES_MIN=int(os.getenv("JWT_EXPIRES_MIN", "60")),
        AI_PROVIDER=os.getenv("AI_PROVIDER", "openai"),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
        OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        GPT4ALL_MODEL_PATH=os.getenv("GPT4ALL_MODEL_PATH", "./models/q4_0-orca-mini-3b.gguf"),
        MAX_TOKENS=int(os.getenv("MAX_TOKENS", "512")),
        TEMPERATURE=float(os.getenv("TEMPERATURE", "0.4")),
    PRIVACY_STORE_MESSAGES=os.getenv("PRIVACY_STORE_MESSAGES", "false").lower() in {"1", "true", "yes", "on"},
    )
