from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..db import get_supabase
from ..services.exporter import export_summary

router = APIRouter(prefix="/api/meetings", tags=["export"])

MIME = {
    "pdf": "application/pdf",
    "md": "text/markdown; charset=utf-8",
    "txt": "text/plain; charset=utf-8",
}


@router.get("/{meeting_id}/export/{fmt}")
def export(meeting_id: str, fmt: str):
    if fmt not in MIME:
        raise HTTPException(400, "Unsupported format")
    sb = get_supabase()
    meeting = sb.table("meetings").select("*").eq("id", meeting_id).maybe_single().execute()
    if not meeting.data:
        raise HTTPException(404, "Meeting not found")
    summary = (
        sb.table("summaries")
        .select("*")
        .eq("meeting_id", meeting_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not summary.data:
        raise HTTPException(400, "No summary available to export")

    body, filename = export_summary(meeting.data, summary.data[0], fmt)
    return Response(
        content=body,
        media_type=MIME[fmt],
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
