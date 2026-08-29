"""Real-time web search grounding via Tavily.

The router calls `search_web` BEFORE sending the prompt to the LLM, so the
streamed answer is anchored in live, sourced facts rather than the model's
training cutoff. Set TAVILY_API_KEY in .env.
"""
import httpx

from app.core.config import settings
from app.models.schemas import SearchResultItem


async def search_web(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
) -> list[SearchResultItem]:
    if not settings.tavily_api_key:
        # Graceful fallback: no key yet -> return nothing, the agent just
        # answers from parametric knowledge.
        return []

    payload = {
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": False,
        "include_raw_content": False,
    }
    headers = {"Authorization": f"Bearer {settings.tavily_api_key}"}
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(settings.search_endpoint, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    items = data.get("results", [])
    return [
        SearchResultItem(
            title=it.get("title", ""),
            url=it.get("url", ""),
            content=it.get("content", ""),
            score=it.get("score"),
        )
        for it in items
    ]


def format_search_context(items: list[SearchResultItem]) -> str:
    """Flatten search results into a compact context block the LLM can cite."""
    if not items:
        return ""
    blocks = []
    for i, it in enumerate(items, 1):
        blocks.append(f"[{i}] {it.title}\nURL: {it.url}\n{it.content.strip()}")
    return "REAL-TIME SOURCES (ground your answer in these, cite as [n]):\n\n" + "\n\n".join(
        blocks
    )