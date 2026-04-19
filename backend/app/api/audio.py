from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..config import get_settings
from ..db import get_supabase
from ..models import AudioFile
from ..services import audio_prep

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/meetings", tags=["audio"])

ALLOWED_MIME_PREFIXES = ("audio/", "video/")
MAX_BYTES = 500 * 1024 * 1024  # 500 MB — hard ceiling enforced by the backend

# Supabase free tier globally caps uploads at 50 MB; we compress above this
# threshold (with a safety margin) whenever ffmpeg is available.
COMPRESS_THRESHOLD_BYTES = 45 * 1024 * 1024


@router.post("/{meeting_id}/audio", response_model=AudioFile, status_code=201)
async def upload_audio(
    meeting_id: str,
    file: UploadFile = File(...),
    compress: bool = Form(True),
):
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

    original_name = file.filename or "audio"
    stored_name = original_name

    # Compress *before* uploading to Supabase — the project-level upload cap
    # (50 MB on the free tier) bites long before our 500 MB check does.
    if compress and len(data) >= COMPRESS_THRESHOLD_BYTES:
        if audio_prep.ffmpeg_available():
            before_mb = len(data) / 1024 / 1024
            try:
                data, mime, was_compressed = audio_prep.maybe_compress(data, original_name)
            except Exception as e:  # noqa: BLE001
                log.exception("ffmpeg compression failed")
                raise HTTPException(500, f"Audio compression failed: {e}")
            if was_compressed:
                after_mb = len(data) / 1024 / 1024
                log.info("Compressed %.1f MB -> %.1f MB before upload", before_mb, after_mb)
                stored_name = original_name.rsplit(".", 1)[0] + ".ogg"
        else:
            log.warning(
                "ffmpeg not available; uploading %.1f MB file as-is (may hit "
                "Supabase's plan upload limit)",
                len(data) / 1024 / 1024,
            )

    suffix = stored_name.rsplit(".", 1)[-1].lower()[:8] or "bin"
    storage_path = f"{meeting_id}/{uuid.uuid4().hex}.{suffix}"

    try:
        sb.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
            path=storage_path,
            file=data,
            file_options={"content-type": mime, "upsert": "true"},
        )
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        if "exceeded the maximum allowed size" in msg or "Payload too large" in msg:
            raise HTTPException(
                413,
                (
                    "Supabase Storage rejected the upload as too large "
                    f"({len(data) / 1024 / 1024:.1f} MB). Install ffmpeg on the "
                    "backend to enable auto-compression, raise the project upload "
                    "limit in Supabase (Settings → Storage), or upload a pre-"
                    "compressed file."
                ),
            )
        raise HTTPException(500, f"Storage upload failed: {e}")

    row = {
        "meeting_id": meeting_id,
        "storage_path": storage_path,
        "filename": stored_name,
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
