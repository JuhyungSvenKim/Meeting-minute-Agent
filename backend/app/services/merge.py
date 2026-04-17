"""Merge Gemini diarization (speaker boundaries) with Whisper STT text.

Strategy: keep Gemini's segment time spans + speaker labels, but replace each
segment's `text` with the concatenation of Whisper segments whose midpoint
falls within the Gemini span. Falls back to Gemini text when no Whisper
segment overlaps.
"""
from __future__ import annotations

from typing import Any


def _whisper_segments(whisper: dict[str, Any]) -> list[dict[str, Any]]:
    segs = whisper.get("segments") or []
    out = []
    for s in segs:
        try:
            out.append(
                {
                    "start": float(s.get("start", 0.0)),
                    "end": float(s.get("end", 0.0)),
                    "text": (s.get("text") or "").strip(),
                }
            )
        except (TypeError, ValueError):
            continue
    return out


def merge_gemini_with_whisper(
    gemini: dict[str, Any], whisper: dict[str, Any]
) -> dict[str, Any]:
    w_segs = _whisper_segments(whisper)
    g_segs = list(gemini.get("segments") or [])
    if not w_segs or not g_segs:
        return gemini

    merged_segments = []
    for g in g_segs:
        try:
            g_start = float(g.get("start_time", 0.0))
            g_end = float(g.get("end_time", g_start))
        except (TypeError, ValueError):
            merged_segments.append(g)
            continue

        bucket: list[str] = []
        for w in w_segs:
            mid = (w["start"] + w["end"]) / 2.0
            if g_start <= mid <= g_end and w["text"]:
                bucket.append(w["text"])

        merged_text = " ".join(bucket).strip() if bucket else (g.get("text") or "")
        merged_segments.append({**g, "text": merged_text})

    out = dict(gemini)
    out["segments"] = merged_segments
    out.setdefault("language", whisper.get("language"))
    return out
