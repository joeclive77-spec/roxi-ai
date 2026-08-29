# Roxi AI — System Architecture

A cross-platform, multimodal conversational AI assistant. This document describes
the two components scaffolded in this repo: a **FastAPI streaming backend** and an
**Expo (React Native) mobile app**.

```
                         ┌────────────────────────────────────────────┐
                         │              MOBILE (Expo / RN)            │
                         │  ChatScreen ── streamChat() ── sseClient.js│
                         │   FlatList + Markdown renderer             │
                         └───────────────────┬────────────────────────┘
                                             │ POST /api/chat  (SSE)
                                             ▼
                         ┌────────────────────────────────────────────┐
                         │              BACKEND (FastAPI)             │
                         │  rate limit ── search (Tavily) ── LLM      │
                         │  SSE stream: sources → token → done        │
                         │  /api/image · /api/tts · /api/stt          │
                         └───────┬──────────────┬────────────┬────────┘
                                 ▼              ▼            ▼
                         Tavily          OpenAI-compatible      FFmpeg/
                         Web Search       LLM (stream)          Whisper
```

## Components

### Backend (`backend/`)

| Layer              | Module                      | Responsibility                                  |
|--------------------|-----------------------------|-------------------------------------------------|
| Config             | `app/core/config.py`        | pydantic-settings singleton; all keys from `.env` |
| Schemas            | `app/models/schemas.py`     | Pydantic request/response models                |
| Chat streaming     | `app/routes/chat.py`        | `/api/chat` SSE: `sources` → `token` → `done`     |
| Media              | `app/routes/media.py`       | `/api/image`, `/api/tts`, `/api/stt`             |
| Web search         | `app/services/search.py`    | Tavily search + context formatting                |
| LLM orchestrator   | `app/services/llm.py`       | OpenAI-compatible streaming via httpx            |
| OpenAI wrappers    | `app/services/openai_client.py` | image gen, TTS, Whisper STT                  |
| Cost control       | `app/services/usage.py`     | per-minute + per-day token budget                 |
| DB (optional)      | `app/db.py`                 | async SQLAlchemy; in-memory fallback if no DB URL |

### Mobile (`mobile/`)
| File                          | Responsibility                        |
|-------------------------------|---------------------------------------|
| `App.js`                      | Root wrapper (SafeAreaView + StatusBar) |
| `src/screens/ChatScreen.js`   | Streaming chat UI (FlatList + Markdown) |
| `src/services/sseClient.js`   | `streamChat(body, handlers)` SSE client |
| `src/services/config.js`      | Base URL + SSE endpoint                |

## Request lifecycle (`POST /api/chat`)
1. **Rate / budget check** — reject with HTTP 429 if over per-minute or per-day limits.
2. **Grounding** — if `search: true`, query Tavily with the last user message;
   inject results as a system context block.
3. **Stream** — call the LLM with `stream:True`, yield raw SSE frames.
   The route emits four event types:
   - `sources` — bibliographic citations (`Array<SearchResultItem>`)
   - `token`    — a text delta (`{delta}`)
   - `done`     — full text + optional `{usage}`
   - `error`    — `{message}`
4. **Usage accounting** — estimate tokens and decrement the daily budget.

## Grounding prompt template
When search is on, the router prepends a system message:

```
REAL-TIME SOURCES (you must answer from these when relevant):
1. <title> — <url>
   <content>
...
```

## SSE event format
Starlette emits `\r\n\r\n`-separated frames:

```
event: sources
data: [{"title":"…","url":"…","content":"…"}]

event: token
data: {"delta":"Hello"}

event: done
data: {"text":"Hello world","usage":{"total_tokens":…}}
```

## Context-provided notes
- With no LLM/API key set, `/api/chat` returns an `error` event
  (`Illegal header value b'Bearer…'`) — expected; set `llm_api_key` in `backend/.env`.
- The DB layer intentionally has an **in-memory fallback**: the app runs with zero
  external infra for prototyping, and upgrades to Postgres/pgvector RAG when a
  `database_url` is provided (see `requirements-db.txt`).