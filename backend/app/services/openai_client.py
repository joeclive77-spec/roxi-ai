"""Thin OpenAI client wrappers for image generation, TTS, and STT."""
import base64

from app.core.config import settings


async def generate_image(prompt: str, n: int = 1, size: str = "1024x1024", quality: str = "standard") -> str:
    """Return a URL for the generated image."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.llm_api_key, base_url=settings.llm_base_url
    )
    resp = await client.images.generate(
        model=settings.image_model, prompt=prompt, n=n, size=size, quality=quality
    )
    return resp.data[0].url or ""


async def synthesize_speech(text: str, voice: str = "alloy") -> str:
    """Return base64-encoded MP3 of the spoken text."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.llm_api_key, base_url=settings.llm_base_url
    )
    resp = await client.audio.speech.create(
        model="tts-1", voice=voice, input=text
    )
    return base64.b64encode(resp.content).decode()


async def recognize_audio(data: bytes, filename: str) -> str:
    """Transcribe an uploaded audio file via Whisper."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.llm_api_key, base_url=settings.llm_base_url
    )
    import uuid

    resp = await client.audio.transcriptions.create(
        model=settings.stt_model,
        file=(filename or f"{uuid.uuid4().hex}.mp3", data),
    )
    return resp.text