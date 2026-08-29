"""Chat API: SSE token streaming with real-time web-search grounding.

Flow:
1. Rate-limit check for the caller.
2. If `search` is true, run Tavily search on the last user message and build
   a grounded system context block.
3. Preview the ground truth to the client (sources event), then stream LLM
   tokens via SSE.
4. Track approximate token usage in the usage tracker for cost control.
"""
import json
import uuid

from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request

from app.models.schemas import ChatRequest
from app.services import llm, search
from app.services.usage import tracker

router = APIRouter(prefix="/api", tags=["chat"])

SYSTEM_PROMPT = (
    "You are a helpful multimodal AI assistant. Answer concisely and "
    "accurately. When REAL-TIME SOURCES are provided, ground your answer in "
    "them and cite them as [1], [2], etc. If you are unsure, say so instead "
    "of guessing."
)


def _build_messages(req: ChatRequest, context: str) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.append({"role": "system", "content": context})
    for m in req.messages:
        if m.image_url:
            # Multimodal image input (vision) support.
            messages.append(
                {
                    "role": m.role,
                    "content": [
                        {"type": "text", "text": m.content},
                        {"type": "image_url", "image_url": {"url": m.image_url}},
                    ],
                }
            )
        else:
            messages.append({"role": m.role, "content": m.content})
    return messages


@router.post("/chat")
async def chat(req: ChatRequest, request: Request):
    user_id = req.user_id or request.client.host or "anonymous"
    ok, msg = tracker.check(user_id)
    if not ok:
        raise HTTPException(status_code=429, detail=msg)

    # 1. Live web search grounding on the last user message.
    last_user = next(
        (m.content for m in reversed(req.messages) if m.role == "user"), ""
    )
    results: list = []
    ground_ctx = ""
    if req.search and last_user:
        results = await search.search_web(last_user)
        ground_ctx = search.format_search_context(results)

    messages = _build_messages(req, ground_ctx)

    async def event_stream():
        # 2. Emit ground-truth sources first so the UI can render citations.
        if results:
            yield {
                "event": "sources",
                "data": json.dumps([r.model_dump() for r in results]),
            }

        # 3. Stream tokens as they arrive.
        text = ""
        try:
            async for delta in llm.stream_chat(messages, req.temperature):
                text += delta
                yield {"event": "token", "data": json.dumps({"delta": delta})}
        except Exception as exc:  # graceful, stream-safe error
            yield {
                "event": "error",
                "data": json.dumps({"message": f"LLM request failed: {exc}"}),
            }
            return

        # 4. Record usage + signal completion.
        tracker.consume(user_id, {"total_tokens": _estimate_tokens(text)})
        yield {
            "event": "done",
            "data": json.dumps(
                {"session_id": uuid.uuid4().hex, "text": text}
            ),
        }

    return EventSourceResponse(event_stream())


def _estimate_tokens(text: str) -> int:
    """Rough token estimate (chars / 4) for cost accounting without a tokenizer."""
    return max(1, len(text) // 4)