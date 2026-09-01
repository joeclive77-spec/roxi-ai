"""Centralized configuration loaded from environment variables.

Use pydantic-settings so all secrets (LLM keys, Tavily key, DB URL) live in
.env, never in code. Values are accessible as typed attributes on the singleton
`settings` instance.
"""
import json

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # App
    app_name: str = "Roxi AI"
    app_env: str = "development"

    # Backend
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["*"]

    # LLM orchestrator
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_chat_model: str = ""
    llm_agent_models: List[str] = []
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

    @field_validator("llm_chat_model", mode="before")
    @classmethod
    def _resolve_chat_model(cls, v, info):
        """Default to an OpenRouter-compatible model when using an OpenRouter key."""
        if v and str(v).strip():
            return v
        key = (info.data.get("llm_api_key") or "").strip()
        return "openai/gpt-4o-mini" if key.startswith("sk-or-v1-") else "gpt-4o-mini"

    @field_validator("llm_base_url", mode="before")
    @classmethod
    def _resolve_llm_base_url(cls, v, info):
        """If base URL is unset but the key is an OpenRouter key, use OpenRouter.

        The Render blueprint only sets LLM_API_KEY; without this, new users
        who configure an OpenRouter key would silently hit OpenAI (401).
        """
        if v and str(v).strip():
            return v
        key = (info.data.get("llm_api_key") or "").strip()
        if key.startswith("sk-or-v1-"):
            return "https://openrouter.ai/api/v1"
        return "https://api.openai.com/v1"

    @field_validator("llm_agent_models", mode="before")
    @classmethod
    def _parse_agent_models(cls, v, info):
        """Accept JSON list, comma-separated string, or empty value from env.

        When an OpenRouter key is detected and no explicit models are set,
        default to a widely-available OpenRouter model.
        """
        key = (info.data.get("llm_api_key") or "").strip()
        is_or = key.startswith("sk-or-v1-")
        if v is None or v == "" or (isinstance(v, (list, tuple)) and not v):
            return ["openai/gpt-4o-mini"] if is_or else ["gpt-4o"]
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                return json.loads(s)
            return [m.strip() for m in s.split(",") if m.strip()]
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors(cls, v):
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                return json.loads(s)
            return [o.strip() for o in s.split(",") if o.strip()]
        return v


settings = Settings()