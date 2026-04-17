"""OpenAI Whisper STT client (verbose JSON for word/segment timing)."""
from __future__ import annotations

import io
from typing import Any

from openai import OpenAI

from ..config import get_settings


WHISPER_MODEL = "whisper-1"


def _client() -> OpenAI:
    s = get_settings()
    if not s.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for Whisper")
    return OpenAI(api_key=s.OPENAI_API_KEY)


def transcribe_audio(audio_bytes: bytes, filename: str) -> dict[str, Any]:
    client = _client()
    bio = io.BytesIO(audio_bytes)
    bio.name = filename or "audio.bin"
    res = client.audio.transcriptions.create(
        model=WHISPER_MODEL,
        file=bio,
        response_format="verbose_json",
        timestamp_granularities=["segment"],
    )
    if hasattr(res, "model_dump"):
        return res.model_dump()
    return dict(res)
