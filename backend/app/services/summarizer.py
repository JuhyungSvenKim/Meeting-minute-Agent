"""Multi-LLM summarizer (Gemini, OpenAI GPT-4o, Anthropic Claude)."""
from __future__ import annotations

import json
import re
from typing import Any

from ..config import get_settings
from ..models import LLMProvider, SummaryContent
from . import gemini_client
from .prompts import SUMMARIZE_SYSTEM, build_summarize_user_prompt


def _strip_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z0-9]*\n?", "", text)
        text = re.sub(r"\n?```\s*$", "", text)
    return text.strip()


def _to_summary(text: str) -> SummaryContent:
    cleaned = _strip_json(text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", cleaned, re.S)
        if not m:
            raise
        data = json.loads(m.group(0))
    return SummaryContent.model_validate(data)


def _format_transcript(segments: list[dict[str, Any]]) -> str:
    lines = []
    for s in segments:
        label = s.get("speaker_name") or s.get("speaker_label") or "?"
        txt = (s.get("text") or "").strip()
        if not txt:
            continue
        lines.append(f"[{label}] {txt}")
    return "\n".join(lines)


def _summarize_gemini(transcript_text: str) -> SummaryContent:
    out = gemini_client.generate_text(
        system=SUMMARIZE_SYSTEM,
        user=build_summarize_user_prompt(transcript_text),
    )
    return _to_summary(out)


def _summarize_openai(transcript_text: str) -> SummaryContent:
    from openai import OpenAI

    s = get_settings()
    if not s.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=s.OPENAI_API_KEY)
    res = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SUMMARIZE_SYSTEM},
            {"role": "user", "content": build_summarize_user_prompt(transcript_text)},
        ],
    )
    return _to_summary(res.choices[0].message.content or "{}")


def _summarize_anthropic(transcript_text: str) -> SummaryContent:
    import anthropic

    s = get_settings()
    if not s.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    client = anthropic.Anthropic(api_key=s.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        temperature=0.3,
        system=SUMMARIZE_SYSTEM,
        messages=[
            {"role": "user", "content": build_summarize_user_prompt(transcript_text)}
        ],
    )
    text = "".join(
        block.text for block in msg.content if getattr(block, "type", None) == "text"
    )
    return _to_summary(text)


def generate_summary(
    provider: LLMProvider,
    transcript: dict[str, Any],
    segments: list[dict[str, Any]],
    format_type: str = "standard",
) -> SummaryContent:
    transcript_text = _format_transcript(segments) or (transcript.get("full_text") or "")
    if not transcript_text.strip():
        raise ValueError("Empty transcript; nothing to summarize")
    if provider == "gemini":
        return _summarize_gemini(transcript_text)
    if provider == "openai":
        return _summarize_openai(transcript_text)
    if provider == "anthropic":
        return _summarize_anthropic(transcript_text)
    raise ValueError(f"Unknown provider: {provider}")
