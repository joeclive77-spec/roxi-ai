"""API request/response models."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"] = "user"
    content: str
    # Optional inline image for multimodal (data URL or a public URL)
    image_url: Optional[str] = None


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(..., min_length=1)
    session_id: str = ""
    user_id: str = ""
    stream: bool = True
    search: bool = True  # dynamically ground answers with live web search
    temperature: float = Field(0.7, ge=0.0, le=2.0)


class SearchResultItem(BaseModel):
    title: str
    url: str
    content: str
    score: Optional[float] = None


class ImageGenRequest(BaseModel):
    prompt: str
    n: int = 1
    size: str = "1024x1024"
    quality: str = "standard"


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0