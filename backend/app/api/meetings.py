from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from ..db import get_supabase
from ..models import Meeting, MeetingCreate, MeetingUpdate

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.get("", response_model=list[Meeting])
def list_meetings():
    sb = get_supabase()
    res = sb.table("meetings").select("*").order("created_at", desc=True).execute()
    return res.data or []


@router.post("", response_model=Meeting, status_code=201)
def create_meeting(payload: MeetingCreate):
    sb = get_supabase()
    row = {
        "title": payload.title,
        "meeting_date": payload.meeting_date.isoformat() if payload.meeting_date else None,
        "status": "created",
    }
    res = sb.table("meetings").insert(row).execute()
    if not res.data:
        raise HTTPException(500, "Failed to create meeting")
    return res.data[0]


@router.get("/{meeting_id}", response_model=Meeting)
def get_meeting(meeting_id: str):
    sb = get_supabase()
    res = sb.table("meetings").select("*").eq("id", meeting_id).maybe_single().execute()
    if not res.data:
        raise HTTPException(404, "Meeting not found")
    return res.data


@router.patch("/{meeting_id}", response_model=Meeting)
def update_meeting(meeting_id: str, payload: MeetingUpdate):
    sb = get_supabase()
    update = {k: v for k, v in payload.model_dump(exclude_none=True).items()}
    if "meeting_date" in update and isinstance(update["meeting_date"], datetime):
        update["meeting_date"] = update["meeting_date"].isoformat()
    if not update:
        raise HTTPException(400, "No fields to update")
    res = sb.table("meetings").update(update).eq("id", meeting_id).execute()
    if not res.data:
        raise HTTPException(404, "Meeting not found")
    return res.data[0]


@router.delete("/{meeting_id}", status_code=204)
def delete_meeting(meeting_id: str):
    sb = get_supabase()
    # Best-effort: remove audio files from storage too
    audio = sb.table("audio_files").select("storage_path").eq("meeting_id", meeting_id).execute()
    paths = [r["storage_path"] for r in (audio.data or []) if r.get("storage_path")]
    if paths:
        try:
            sb.storage.from_("meeting-audio").remove(paths)
        except Exception:
            pass
    sb.table("meetings").delete().eq("id", meeting_id).execute()
    return None
