"""OpenAI Whisper STT client (verbose JSON for word/segment timing)."""
from __future__ import annotations

import io
from typing import Any

from openai import OpenAI

from ..config import get_settings


WHISPER_MODEL = "whisper-1"
# OpenAI's Whisper endpoint caps uploads at 25 MB per request.
WHISPER_MAX_BYTES = 25 * 1024 * 1024


def _client() -> OpenAI:
    s = get_settings()
    if not s.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is required for Whisper")
    return OpenAI(api_key=s.OPENAI_API_KEY)


def transcribe_audio(audio_bytes: bytes, filename: str) -> dict[str, Any]:
    if len(audio_bytes) > WHISPER_MAX_BYTES:
        raise RuntimeError(
            f"Audio is {len(audio_bytes) / 1024 / 1024:.1f} MB which exceeds "
            f"Whisper's 25 MB per-request limit. Use the 'gemini' pipeline for "
            f"large files, or pre-compress/split the audio."
        )
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
