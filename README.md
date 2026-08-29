# Roxi AI

[![CI](https://github.com/joeclive77-spec/test/actions/workflows/ci.yml/badge.svg)](https://github.com/joeclive77-spec/test/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](backend/requirements.txt)
[![Node 18+](https://img.shields.io/badge/node-18+-green.svg)](mobile/package.json)
[![Expo ~51](https://img.shields.io/badge/expo-~51-000020.svg)](mobile/package.json)

A cross-platform, multimodal conversational AI assistant with real-time web
search, streaming chat, image generation, and voice — Python/FastAPI backend
plus an Expo (React Native) mobile client.

## Features

- **Streaming chat** over Server-Sent Events (SSE) — `sources` → `token` → `done`
- **Web-grounded answers** via Tavily search, blended into the LLM context
- **Multimodal**: image generation, text-to-speech, speech-to-text
- **Pluggable LLM** — any OpenAI-compatible endpoint (OpenAI, vLLM, Ollama)
- **Rate + token budgets** with a thread-safe in-memory tracker (Postgres path ready)
- **Mobile-first** UX with a markdown-rendered chat surface

## Repo layout

```
roxi-ai/
├── backend/                 # FastAPI streaming API
│   ├── app/routes/          #   chat (SSE), media (image/tts/stt)
│   ├── app/services/        #   search (Tavily), llm, openai_client, usage
│   └── tests/               #   SSE streaming + rate-limit tests
├── mobile/                  # Expo / React Native chat app
│   └── src/services/        #   SSE streaming client
├── docs/
│   ├── architecture.md      # system design & request lifecycle
│   └── deployment.md        # run, deploy, and secure
├── LICENSE                  # MIT
├── CONTRIBUTING.md
└── SECURITY.md
```

## Quick start

### Prerequisites
- Python 3.11+
- Node.js 18+
- An OpenAI-compatible LLM API key
- A Tavily API key (for web grounding)

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in LLM_API_KEY, TAVILY_API_KEY
uvicorn app.main:app --reload # http://localhost:8000
```

### Mobile
```bash
cd mobile
npm install
npx expo start                # scan QR with Expo Go
```

Override the API base URL with `EXPO_PUBLIC_API_URL` when running the app.

## Environment variables

| Variable | Purpose | Required |
|---|---|---|
| `LLM_API_KEY` | OpenAI-compatible API key | yes |
| `LLM_BASE_URL` | Endpoint (default `https://api.openai.com/v1`) | no |
| `LLM_CHAT_MODEL` | Chat model (default `gpt-4o-mini`) | no |
| `LLM_AGENT_MODELS` | Comma-separated fallback models | no |
| `TAVILY_API_KEY` | Web search grounding | yes |
| `IMAGE_MODEL` | Image gen model (default `dall-e-3`) | no |
| `TTS_VOICE` | TTS voice (default `alloy`) | no |
| `STT_MODEL` | Speech-to-text model (default `whisper-1`) | no |
| `DATABASE_URL` | Postgres URL — empty = in-memory dev | no |
| `CORS_ORIGINS` | JSON list of allowed origins (default `["*"]`) | no |
| `RATE_LIMIT_PER_MIN` | Requests/minute cap | no |
| `RATE_LIMIT_TOKENS_PER_DAY` | Daily token cap | no |

## Endpoints

| Method | Path         | Description                              |
|--------|--------------|------------------------------------------|
| GET    | `/health`    | Liveness probe                            |
| POST   | `/api/chat`  | SSE chat stream (`sources` / `token` / `done`) |
| POST   | `/api/image` | Image generation                          |
| POST   | `/api/tts`   | Text → speech                             |
| POST   | `/api/stt`   | Speech → text (multipart upload)          |

## Tests

```bash
cd backend
python -m pytest
```

## Docs
- [Architecture](docs/architecture.md) — components, request lifecycle, SSE format.
- [Deployment](docs/deployment.md) — local setup, production topology, security.

## License

MIT — see [LICENSE](LICENSE).
