"""Centralized configuration loaded from environment variables.

Use pydantic-settings so all secrets (LLM keys, Tavily key, DB URL) live in
.env, never in code. Values are accessible as typed attributes on the singleton
`settings` instance.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    app_name: str = "AI Assistant"
    app_env: str = "development"

    # Backend
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["*"]

    # LLM orchestrator
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_chat_model: str = "gpt-4o-mini"
    llm_agent_models: list[str] = ["gpt-4o"]
    llm_max_tokens: int = 4096

    # Search grounding
    tavily_api_key: str = ""
    search_endpoint: str = "https://api.tavily.com/search"

    # Image generation
    image_model: str = "dall-e-3"
    image_size: str = "1024x1024"

    # Voice / TTS
    tts_voice: str = "alloy"
    stt_model: str = "whisper-1"

    # Database
    database_url: str = ""

    # Limits / cost control
    rate_limit_per_min: int = 60
    rate_limit_tokens_per_day: int = 100_000


settings = Settings()