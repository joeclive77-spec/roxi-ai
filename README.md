# AI Assistant

A cross-platform, multimodal conversational AI assistant with real-time web
search, streaming chat, image generation, and voice — Python/FastAPI backend
plus an Expo (React Native) mobile client.

## Repo layout
```
ai-assistant/
├── backend/                 # FastAPI streaming API
│   ├── app/routes/          #   chat (SSE), media (image/tts/stt)
│   ├── app/services/        #   search (Tavily), llm, openai_client, usage
│   └── tests/               #   SSE streaming + rate-limit tests
├── mobile/                  # Expo / React Native chat app
│   └── src/services/        #   SSE streaming client
└── docs/
    ├── architecture.md      # system design & request lifecycle
    └── deployment.md        # run, deploy, and secure
```

## Quick start
### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env          # add LLM_API_KEY, TAVILY_API_KEY
uvicorn app.main:app --reload
```
### Mobile
```bash
cd mobile
npm install
npx expo start
```

## Endpoints
| Method | Path         | Description                              |
|--------|--------------|------------------------------------------|
| GET    | `/health`    | liveness                                  |
| POST   | `/api/chat`  | SSE chat stream (`sources`/`token`/`done`) |
| POST   | `/api/image` | image generation                          |
| POST   | `/api/tts`   | text → speech                             |
| POST   | `/api/stt`   | speech → text (multipart upload)          |

## Docs
- [Architecture](docs/architecture.md) — components, request lifecycle, SSE format.
- [Deployment](docs/deployment.md) — local setup, production topology, security.

## Status
Backend streaming, grounding, rate/cost limits, and media endpoints are
implemented and the test suite passes. See `docs/` for the production roadmap.