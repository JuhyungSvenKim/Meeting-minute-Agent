from __future__ import annotations

import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..config import get_settings
from ..db import get_supabase
from ..models import AudioFile

router = APIRouter(prefix="/api/meetings", tags=["audio"])

ALLOWED_MIME_PREFIXES = ("audio/", "video/")
MAX_BYTES = 500 * 1024 * 1024  # 500 MB


@router.post("/{meeting_id}/audio", response_model=AudioFile, status_code=201)
async def upload_audio(meeting_id: str, file: UploadFile = File(...)):
    settings = get_settings()
    sb = get_supabase()

    meeting = sb.table("meetings").select("id").eq("id", meeting_id).maybe_single().execute()
    if not meeting.data:
        raise HTTPException(404, "Meeting not found")

    mime = file.content_type or "application/octet-stream"
    if not any(mime.startswith(p) for p in ALLOWED_MIME_PREFIXES):
        raise HTTPException(400, f"Unsupported mime type: {mime}")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File exceeds 500 MB limit")

    suffix = (file.filename or "audio").rsplit(".", 1)[-1].lower()[:8] or "bin"
    storage_path = f"{meeting_id}/{uuid.uuid4().hex}.{suffix}"

    try:
        sb.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            path=storage_path,
            file=data,
            file_options={"content-type": mime, "upsert": "true"},
        )
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Storage upload failed: {e}")

    row = {
        "meeting_id": meeting_id,
        "storage_path": storage_path,
        "filename": file.filename or "audio",
        "size": len(data),
        "mime_type": mime,
    }
    res = sb.table("audio_files").insert(row).execute()
    if not res.data:
        raise HTTPException(500, "Failed to record audio file")

    sb.table("meetings").update({"status": "uploaded", "error_message": None}).eq(
        "id", meeting_id
    ).execute()

    return res.data[0]
