"""AI Assistant API entrypoint.

Run:  uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db import init_db
from app.routes.chat import router as chat_router
from app.routes.media import router as media_router

app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(media_router)


@app.on_event("startup")
async def on_startup():
    init_db()


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.app_name}