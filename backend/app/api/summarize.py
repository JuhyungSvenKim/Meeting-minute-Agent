from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..db import get_supabase
from ..models import Summary, SummaryRequest
from ..services.summarizer import generate_summary

router = APIRouter(prefix="/api/meetings", tags=["summary"])


@router.post("/{meeting_id}/summarize", response_model=Summary)
def summarize(meeting_id: str, payload: SummaryRequest):
    sb = get_supabase()
    meeting = sb.table("meetings").select("*").eq("id", meeting_id).maybe_single().execute()
    if not meeting.data:
        raise HTTPException(404, "Meeting not found")

    tr = (
        sb.table("transcripts")
        .select("*")
        .eq("meeting_id", meeting_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not tr.data:
        raise HTTPException(400, "Transcript not available; run processing first")
    transcript = tr.data[0]
    seg = (
        sb.table("speaker_segments")
        .select("*")
        .eq("transcript_id", transcript["id"])
        .order("segment_order")
        .execute()
    )

    try:
        content = generate_summary(
            provider=payload.llm_provider,
            transcript=transcript,
            segments=seg.data or [],
            format_type=payload.format_type,
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Summary generation failed: {e}")

    row = {
        "meeting_id": meeting_id,
        "llm_provider": payload.llm_provider,
        "content": content.model_dump(),
        "format_type": payload.format_type,
    }
    res = sb.table("summaries").insert(row).execute()
    if not res.data:
        raise HTTPException(500, "Failed to save summary")

    sb.table("meetings").update({"status": "summarized"}).eq("id", meeting_id).execute()
    return res.data[0]


@router.get("/{meeting_id}/summary", response_model=Summary)
def latest_summary(meeting_id: str):
    sb = get_supabase()
    res = (
        sb.table("summaries")
        .select("*")
        .eq("meeting_id", meeting_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not res.data:
        raise HTTPException(404, "Summary not found")
    return res.data[0]
