"""Gemini 3.1 Pro client for audio transcription + summary.

Uses the `google-genai` SDK. The model handles the audio file directly.
"""
from __future__ import annotations

import json
import re
from typing import Any

from google import genai
from google.genai import types

from ..config import get_settings
from .prompts import GEMINI_TRANSCRIBE_PROMPT

# Audio transcription / diarization model — per user request: Gemini 3.1 Pro.
GEMINI_AUDIO_MODEL = "gemini-3.1-pro"
GEMINI_TEXT_MODEL = "gemini-3.1-pro"


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


def transcribe_audio(audio_bytes: bytes, mime_type: str) -> dict[str, Any]:
    """Send audio to Gemini 3.1 Pro and parse the JSON response."""
    client = _client()
    response = client.models.generate_content(
        model=GEMINI_AUDIO_MODEL,
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
            GEMINI_TRANSCRIBE_PROMPT,
        ],
        config=types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        ),
    )
    text = response.text or ""
    return _parse_json(text)


def generate_text(system: str, user: str) -> str:
    client = _client()
    response = client.models.generate_content(
        model=GEMINI_TEXT_MODEL,
        contents=[user],
        config=types.GenerateContentConfig(
            temperature=0.3,
            system_instruction=system,
            response_mime_type="application/json",
        ),
    )
    return response.text or ""
