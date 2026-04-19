"""Gemini client for audio transcription + summary.

Uses the `google-genai` SDK. For files >= 20 MB we upload via the Files API
first, then reference it; smaller files are sent inline for lower latency.
"""
from __future__ import annotations

import io
import json
import re
import time
from typing import Any

from google import genai
from google.genai import types

from ..config import get_settings
from .prompts import GEMINI_TRANSCRIBE_PROMPT

# Default model; frontend can override per-request.
GEMINI_AUDIO_MODEL = "gemini-3.1-flash"
GEMINI_TEXT_MODEL = "gemini-3.1-flash"

AVAILABLE_AUDIO_MODELS = [
    "gemini-3.0-flash",
    "gemini-3.0-pro",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash",
    "gemini-3.1-pro",
]

# Gemini's inline request body is ~20 MB; go through the Files API beyond that.
INLINE_LIMIT_BYTES = 18 * 1024 * 1024


def _client() -> genai.Client:
    s = get_settings()
    if not s.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")
    return genai.Client(api_key=s.GEMINI_API_KEY)


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _parse_json(text: str) -> dict[str, Any]:
    cleaned = _strip_code_fences(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def _upload_and_wait(client: genai.Client, audio_bytes: bytes, mime_type: str):
    """Upload via Files API and poll until ACTIVE."""
    bio = io.BytesIO(audio_bytes)
    uploaded = client.files.upload(file=bio, config={"mime_type": mime_type})
    # Poll state until ACTIVE (or FAILED).
    deadline = time.time() + 600  # 10 min
    while True:
        f = client.files.get(name=uploaded.name)
        state = getattr(f.state, "name", str(f.state))
        if state == "ACTIVE":
            return f
        if state == "FAILED":
            raise RuntimeError(f"Gemini file upload failed: {f}")
        if time.time() > deadline:
            raise TimeoutError("Timed out waiting for Gemini file to become ACTIVE")
        time.sleep(2)


def transcribe_audio(
    audio_bytes: bytes,
    mime_type: str,
    model: str | None = None,
) -> dict[str, Any]:
    """Send audio to Gemini and parse the JSON response.

    Uses inline bytes for small files and the Files API for large ones.
    """
    client = _client()
    model_name = model or GEMINI_AUDIO_MODEL

    if len(audio_bytes) <= INLINE_LIMIT_BYTES:
        audio_part: Any = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    else:
        audio_part = _upload_and_wait(client, audio_bytes, mime_type)

    response = client.models.generate_content(
        model=model_name,
        contents=[audio_part, GEMINI_TRANSCRIBE_PROMPT],
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    text = response.text or ""
    return _parse_json(text)


def generate_text(system: str, user: str, model: str | None = None) -> str:
    client = _client()
    response = client.models.generate_content(
        model=model or GEMINI_TEXT_MODEL,
        contents=[user],
        config=types.GenerateContentConfig(
            temperature=0.3,
            system_instruction=system,
            response_mime_type="application/json",
        ),
    )
    return response.text or ""
