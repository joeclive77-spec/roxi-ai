# Roxi AI — Deployment & Security Roadmap

## Prerequisites
- Python 3.11+ (3.14 supported by core deps; Postgres extras need matching wheels)
- Node.js 18+ for the Expo app
- API keys in `backend/.env` (copy from `.env.example`):
  - `LLM_API_KEY` + `LLM_BASE_URL` (any OpenAI-compatible endpoint)
  - `TAVILY_API_KEY` for web-search grounding
  - (optional) OpenAI key for image / TTS / STT

## Local backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt       # core streaming + API
pip install -r requirements-dev.txt    # pytest (optional dev)
cp .env.example .env                    # fill in keys
uvicorn app.main:app --reload           # http://localhost:8000
```
Optional persistence:
```bash
pip install -r requirements-db.txt      # psycopg + pgvector + sqlalchemy
# set DATABASE_URL in .env; app switches to Postgres automatically
```

## Local mobile
```bash
cd mobile
npm install
npx expo start                          # scan QR with Expo Go
```
Point the app at your backend via `EXPO_PUBLIC_API_URL` (see `src/services/config.js`).

## Tests
```bash
cd backend
python -m pytest                         # SSE streaming + rate-limit tests
```

## Production topology (recommended)
- **API**: Dockerized FastAPI behind an app server (Uvicorn workers + TLS).
- **Frontend**: build Expo with `npx expo export`, ship to App Store / Play (or Expo EAS).
- **DB**: managed Postgres with `pgvector` extension for RAG memory.
- **Secrets**: never commit `.env`; inject via the platform's secret manager.

## Security checklist
1. **Secrets**: all keys via environment / secret manager — `config.py` reads `.env`
   and nothing is hard-coded. Enforce `.gitignore` on `.env`.
2. **Auth**: add user scoping before production — OAuth/JWT on requests, per-user
   budgets. Current `UsageTracker` is in-memory and global.
3. **Rate limiting / cost control**: per-minute and per-day token budgets are set in
   `config.py`. Raise/harden for multi-tenant.
4. **Prompt injection**: the `search` grounding block is clearly delimited system
   context; top-of-conversation constraints + input sanitization recommended.
5. **Multipart uploads** (`/api/stt`): validate file type, size, and duration to avoid
   resource exhaustion.
6. **Transport**: terminate TLS at the edge (cloud load balancer / reversed proxy).

## Cost-control knobs (`config.py`)
| Setting                      | Default    | Meaning                          |
|------------------------------|-----------|----------------------------------|
| `llm_max_tokens`            | 4096      | cap per completion               |
| `rate_limit_per_min`        | 60        | requests / user / minute         |
| `rate_limit_tokens_per_day` | 100000    | daily token budget (global)      |

## Deferred / production-grade additions
- Persistent Postgres + `pgvector` RAG over user documents.
- WebSocket fallback for iOS background duplex voice mode.
- Token-aware usage tracking per user (replace in-memory `UsageTracker`).
- Multi-tenant auth, quotas, and distributed rate limiting via Redis.