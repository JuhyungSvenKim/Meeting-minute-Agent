"""In-memory pipeline progress tracker.

A simple per-process dict for tracking processing stage / progress per meeting.
For production deployments behind multiple workers, replace with Redis.
"""
from __future__ import annotations

import threading
from typing import Optional

from .models import ProcessingStage

_lock = threading.Lock()
_progress: dict[str, dict] = {}


def set_progress(
    meeting_id: str,
    stage: ProcessingStage,
    progress: int = 0,
    message: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    with _lock:
        _progress[meeting_id] = {
            "stage": stage,
            "progress": progress,
            "message": message,
            "error_message": error_message,
        }


def get_progress(meeting_id: str) -> Optional[dict]:
    with _lock:
        data = _progress.get(meeting_id)
        return dict(data) if data else None


def clear_progress(meeting_id: str) -> None:
    with _lock:
        _progress.pop(meeting_id, None)
