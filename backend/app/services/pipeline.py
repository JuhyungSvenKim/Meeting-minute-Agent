"""End-to-end processing pipeline: download audio → transcribe → save."""
from __future__ import annotations

import traceback
from typing import Any

from ..config import get_settings
from ..db import get_supabase
from ..models import PipelineType
from ..state import set_progress
from . import gemini_client, whisper_client
from .gemini_client import GEMINI_AUDIO_MODEL as GEMINI_AUDIO_MODEL_NAME
from .merge import merge_gemini_with_whisper


def _download_audio(storage_path: str) -> bytes:
    settings = get_settings()
    sb = get_supabase()
    return sb.storage.from_(settings.SUPABASE_STORAGE_BUCKET).download(storage_path)


def _save_transcript(
    meeting_id: str,
    provider: str,
    parsed: dict[str, Any],
    raw: dict[str, Any] | None = None,
) -> None:
    sb = get_supabase()

    segments = parsed.get("segments") or []
    full_text = "\n".join(
        f"[{s.get('speaker_label', '?')}] {(s.get('text') or '').strip()}"
        for s in segments
        if (s.get("text") or "").strip()
    )

    speakers = {s.get("speaker_label"): s for s in (parsed.get("speakers") or [])}

    tr = (
        sb.table("transcripts")
        .insert(
            {
                "meeting_id": meeting_id,
                "provider": provider,
                "raw_response": raw or parsed,
                "full_text": full_text,
                "language": parsed.get("language"),
            }
        )
        .execute()
    )
    if not tr.data:
        raise RuntimeError("Failed to insert transcript")
    transcript_id = tr.data[0]["id"]

    rows = []
    for i, seg in enumerate(segments):
        label = seg.get("speaker_label") or "S?"
        rows.append(
            {
                "transcript_id": transcript_id,
                "speaker_label": label,
                "speaker_name": None,
                "start_time": float(seg.get("start_time", 0.0)),
                "end_time": float(seg.get("end_time", 0.0)),
                "text": (seg.get("text") or "").strip(),
                "confidence": seg.get("confidence"),
                "gender_estimate": (speakers.get(label) or {}).get("gender_estimate"),
                "segment_order": i,
            }
        )
    if rows:
        sb.table("speaker_segments").insert(rows).execute()


def _save_summary_from_pipeline(meeting_id: str, parsed: dict[str, Any]) -> None:
    """Persist the summary that Gemini produced inline (so users see something
    immediately after processing). Users can re-summarize with another LLM."""
    summary = parsed.get("summary") or {}
    if not summary:
        return
    sb = get_supabase()
    sb.table("summaries").insert(
        {
            "meeting_id": meeting_id,
            "llm_provider": "gemini",
            "content": summary,
            "format_type": "standard",
        }
    ).execute()


def run_pipeline(
    meeting_id: str, pipeline_type: PipelineType, audio_record: dict[str, Any]
) -> None:
    sb = get_supabase()
    storage_path = audio_record["storage_path"]
    filename = audio_record.get("filename") or "audio.bin"
    mime_type = audio_record.get("mime_type") or "audio/mpeg"

    try:
        set_progress(meeting_id, "downloading", 5, "Downloading audio")
        audio_bytes = _download_audio(storage_path)

        size_mb = len(audio_bytes) / 1024 / 1024
        if size_mb > 18:
            set_progress(
                meeting_id,
                "transcribing",
                20,
                f"Uploading {size_mb:.0f} MB to Gemini Files API…",
            )
        set_progress(
            meeting_id,
            "transcribing",
            30,
            f"Transcribing with Gemini ({GEMINI_AUDIO_MODEL_NAME})",
        )
        parsed = gemini_client.transcribe_audio(audio_bytes, mime_type)
        provider = "gemini"

        if pipeline_type == "gemini_whisper":
            set_progress(meeting_id, "transcribing", 60, "Transcribing with Whisper")
            whisper_raw = whisper_client.transcribe_audio(audio_bytes, filename)
            set_progress(meeting_id, "merging", 75, "Merging Gemini diarization + Whisper STT")
            parsed = merge_gemini_with_whisper(parsed, whisper_raw)
            provider = "gemini+whisper"

        set_progress(meeting_id, "saving", 90, "Saving transcript")
        _save_transcript(meeting_id, provider, parsed)
        _save_summary_from_pipeline(meeting_id, parsed)

        sb.table("meetings").update(
            {"status": "summarized", "error_message": None}
        ).eq("id", meeting_id).execute()
        set_progress(meeting_id, "completed", 100, "Done")
    except Exception as e:  # noqa: BLE001
        msg = f"{e.__class__.__name__}: {e}"
        traceback.print_exc()
        sb.table("meetings").update(
            {"status": "error", "error_message": msg}
        ).eq("id", meeting_id).execute()
        set_progress(meeting_id, "error", 0, message=None, error_message=msg)
