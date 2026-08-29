"""Image generation + speech (TTS) + transcription (STT) endpoints."""
from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import settings
from app.models.schemas import ImageGenRequest
from app.services.openai_client import generate_image, recognize_audio, synthesize_speech

router = APIRouter(prefix="/api", tags=["media"])


@router.post("/image")
async def generate_image(req: ImageGenRequest):
    try:
        url = await generate_image(
            prompt=req.prompt, n=req.n, size=req.size, quality=req.quality
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Image generation failed: {exc}")
    return {"url": url}


class TTSRequest(BaseModel):
    text: str
    voice: str = settings.tts_voice


@router.post("/tts")
async def tts(req: TTSRequest):
    try:
        audio_b64 = await synthesize_speech(req.text, voice=req.voice)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"TTS failed: {exc}")
    return {"audio": audio_b64, "format": "mp3"}


@router.post("/stt")
async def stt(file: UploadFile):
    data = await file.read()
    try:
        transcript = await recognize_audio(data, filename=file.filename)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"STT failed: {exc}")
    return {"text": transcript}