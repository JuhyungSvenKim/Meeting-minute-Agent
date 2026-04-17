from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException

from ..db import get_supabase
from ..models import ProcessRequest, ProcessStatus
from ..services.pipeline import run_pipeline
from ..state import get_progress

router = APIRouter(prefix="/api/meetings", tags=["process"])


@router.post("/{meeting_id}/process", status_code=202)
def start_processing(
    meeting_id: str, payload: ProcessRequest, background: BackgroundTasks
):
    sb = get_supabase()
    meeting = sb.table("meetings").select("*").eq("id", meeting_id).maybe_single().execute()
    if not meeting.data:
        raise HTTPException(404, "Meeting not found")

    audio = (
        sb.table("audio_files")
        .select("*")
        .eq("meeting_id", meeting_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not audio.data:
        raise HTTPException(400, "No audio file uploaded for this meeting")

    sb.table("meetings").update(
        {
            "status": "processing",
            "pipeline_type": payload.pipeline_type,
            "error_message": None,
        }
    ).eq("id", meeting_id).execute()

    background.add_task(
        run_pipeline,
        meeting_id=meeting_id,
        pipeline_type=payload.pipeline_type,
        audio_record=audio.data[0],
    )
    return {"meeting_id": meeting_id, "status": "processing"}


@router.get("/{meeting_id}/process/status", response_model=ProcessStatus)
def process_status(meeting_id: str):
    sb = get_supabase()
    meeting = sb.table("meetings").select("*").eq("id", meeting_id).maybe_single().execute()
    if not meeting.data:
        raise HTTPException(404, "Meeting not found")

    progress = get_progress(meeting_id) or {}
    status = meeting.data["status"]

    stage = progress.get("stage")
    if not stage:
        if status == "processing":
            stage = "queued"
        elif status in ("transcribed", "summarized"):
            stage = "completed"
        elif status == "error":
            stage = "error"
        else:
            stage = "queued"

    return ProcessStatus(
        meeting_id=meeting_id,
        status=status,
        stage=stage,
        progress=int(progress.get("progress") or (100 if stage == "completed" else 0)),
        message=progress.get("message"),
        error_message=progress.get("error_message") or meeting.data.get("error_message"),
    )
