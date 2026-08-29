"""LLM orchestrator: chat completions + token streaming.

Streams via OpenAI-compatible SSE. The `messages` list already includes the
search-grounded system context from the router; here we just forward and
yield deltas. Works with any OpenAI-compatible endpoint (OpenAI, vLLM, Ollama).
"""
import json
from collections.abc import AsyncIterator

import httpx

from app.core.config import settings


def _chat_url() -> str:
    return f"{settings.llm_base_url.rstrip('/')}/chat/completions"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }


async def _nonstream(messages: list[dict], temperature: float) -> dict:
    payload = {
        "model": settings.llm_chat_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": settings.llm_max_tokens,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0)) as client:
        resp = await client.post(_chat_url(), json=payload, headers=_headers())
        resp.raise_for_status()
        return resp.json()


def parse_usage(data: dict) -> dict:
    """Normalize usage dict -> {prompt, completion, total}."""
    u = (data.get("usage") or {}).get("prompt", {}) if isinstance(
        data.get("usage"), dict
    ) and "prompt" in data["usage"] else (data.get("usage") or {})
    if isinstance(u, dict) and "prompt_tokens" not in u and "prompt" in u:
        u = u["prompt"]
    if isinstance(u, dict) and "total_tokens" not in u:
        return {
            "prompt_tokens": u.get("prompt_tokens", 0),
            "completion_tokens": u.get("completion_tokens", 0),
            "total_tokens": u.get("total_tokens", 0),
        }
    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    }


async def stream_chat(messages: list[dict], temperature: float = 0.7) -> AsyncIterator[str]:
    """Yield content deltas as they arrive from the LLM (SSE)."""
    payload = {
        "model": settings.llm_chat_model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": settings.llm_max_tokens,
        "stream": True,
    }
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=10.0)
    ) as client:
        async with client.stream("POST", _chat_url(), json=payload, headers=_headers()) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line or not line.startswith("data:"):
                    continue
                data = line[len("data:"):].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content