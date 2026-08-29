"""Integration test for the streaming chat endpoint.

Uses FastAPI TestClient + SSE parsing. The LLM and Tavily calls are stubbed
out by monkeypatching so no real API keys are needed.
"""
import json

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import llm, search
from app.models.schemas import SearchResultItem


@pytest.fixture
def client(monkeypatch):
    # Stub search -> one fake source
    async def fake_search(_q, **_):
        return [SearchResultItem(title="Test Source", url="https://x.test", content="Facts")]
    monkeypatch.setattr(search, "search_web", fake_search)

    # Stub LLM -> stream two tokens then done (text-only content)
    async def fake_stream(_messages, temperature=0.7):
        yield "Hello"
        yield " world"
    monkeypatch.setattr(llm, "stream_chat", fake_stream)

    return TestClient(app)


def test_stream_chat_emits_sources_and_tokens(client):
    resp = client.post(
        "/api/chat",
        json={
            "messages": [{"role": "user", "content": "What's the weather?"}],
            "search": True,
        },
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/event-stream")

    # Normalize CRLF separators (starlette emits \r\n\r\n) before parsing.
    events = []
    for raw in resp.text.replace("\r\n", "\n").split("\n\n"):
        if not raw:
            continue
        evt = None
        data = None
        for line in raw.split("\n"):
            if line.startswith("event:"):
                evt = line[6:].strip()
            elif line.startswith("data:"):
                data = line[5:].strip()
        if evt is not None:
            events.append((evt, data))

    names = [e[0] for e in events]
    assert "sources" in names, events
    assert "token" in names, events
    assert "done" in names, events
    # Ensure tokens concatenate
    text = "".join(json.loads(d)["delta"] for e, d in events if e == "token")
    assert text == "Hello world"


def test_chat_rate_limit_429(client, monkeypatch):
    from app.core.config import settings
    monkeypatch.setattr(settings, "rate_limit_per_min", 1)
    client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    r2 = client.post("/api/chat", json={"messages": [{"role": "user", "content": "hi"}]})
    assert r2.status_code == 429