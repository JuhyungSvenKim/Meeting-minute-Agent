from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..db import get_supabase
from ..models import SpeakerNameUpdate, Transcript

router = APIRouter(prefix="/api/meetings", tags=["transcripts"])


@router.get("/{meeting_id}/transcript", response_model=Transcript)
def get_transcript(meeting_id: str):
    sb = get_supabase()
    tr = (
        sb.table("transcripts")
        .select("*")
        .eq("meeting_id", meeting_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not tr.data:
        raise HTTPException(404, "Transcript not found")
    transcript = tr.data[0]
    seg = (
        sb.table("speaker_segments")
        .select("*")
        .eq("transcript_id", transcript["id"])
        .order("segment_order")
        .execute()
    )
    transcript["segments"] = seg.data or []
    return transcript


@router.patch("/{meeting_id}/speakers/{label}")
def update_speaker_name(meeting_id: str, label: str, payload: SpeakerNameUpdate):
    sb = get_supabase()
    tr = (
        sb.table("transcripts")
        .select("id")
        .eq("meeting_id", meeting_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not tr.data:
        raise HTTPException(404, "Transcript not found")
    transcript_id = tr.data[0]["id"]
    res = (
        sb.table("speaker_segments")
        .update({"speaker_name": payload.speaker_name})
        .eq("transcript_id", transcript_id)
        .eq("speaker_label", label)
        .execute()
    )
    return {"updated": len(res.data or []), "speaker_label": label, "speaker_name": payload.speaker_name}
