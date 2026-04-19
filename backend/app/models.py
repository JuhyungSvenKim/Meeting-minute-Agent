from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

PipelineType = Literal["gemini", "gemini_whisper"]
GeminiAudioModel = Literal[
    "gemini-3.0-flash",
    "gemini-3.0-pro",
    "gemini-3.1-flash-lite",
    "gemini-3.1-flash",
    "gemini-3.1-pro",
]
MeetingStatus = Literal[
    "created", "uploaded", "processing", "transcribed", "summarized", "error"
]
LLMProvider = Literal["gemini", "openai", "anthropic"]
ExportFormat = Literal["pdf", "md", "txt"]
ProcessingStage = Literal[
    "queued", "downloading", "transcribing", "merging", "saving", "completed", "error"
]


# ----------------------------- Meetings -----------------------------
class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    meeting_date: Optional[datetime] = None


class MeetingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    meeting_date: Optional[datetime] = None
    status: Optional[MeetingStatus] = None
    pipeline_type: Optional[PipelineType] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[int] = None


class Meeting(BaseModel):
    id: str
    title: str
    meeting_date: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    status: MeetingStatus
    pipeline_type: Optional[PipelineType] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ----------------------------- Audio -----------------------------
class AudioFile(BaseModel):
    id: str
    meeting_id: str
    storage_path: str
    filename: str
    size: int
    mime_type: str
    created_at: datetime


# ----------------------------- Transcripts -----------------------------
class SpeakerSegment(BaseModel):
    id: Optional[str] = None
    transcript_id: Optional[str] = None
    speaker_label: str
    speaker_name: Optional[str] = None
    start_time: float
    end_time: float
    text: str
    confidence: Optional[float] = None
    gender_estimate: Optional[str] = None
    segment_order: int


class Transcript(BaseModel):
    id: str
    meeting_id: str
    provider: str
    raw_response: Optional[dict[str, Any]] = None
    full_text: Optional[str] = None
    confidence_score: Optional[float] = None
    language: Optional[str] = None
    created_at: datetime
    segments: list[SpeakerSegment] = []


class SpeakerNameUpdate(BaseModel):
    speaker_name: str = Field(..., min_length=1, max_length=200)


# ----------------------------- Pipeline -----------------------------
class ProcessRequest(BaseModel):
    pipeline_type: PipelineType = "gemini"
    gemini_model: GeminiAudioModel = "gemini-3.1-flash"
    compress_audio: bool = True  # auto-compress if ffmpeg is available


class ProcessStatus(BaseModel):
    meeting_id: str
    status: MeetingStatus
    stage: ProcessingStage
    progress: int = 0
    message: Optional[str] = None
    error_message: Optional[str] = None


# ----------------------------- Summary -----------------------------
class ActionItem(BaseModel):
    title: str
    owner: Optional[str] = None
    due_date: Optional[str] = None


class SummaryContent(BaseModel):
    title: Optional[str] = None
    attendees: list[str] = []
    summary: str = ""
    key_points: list[str] = []
    decisions: list[str] = []
    action_items: list[ActionItem] = []


class SummaryRequest(BaseModel):
    llm_provider: LLMProvider = "gemini"
    format_type: str = "standard"


class Summary(BaseModel):
    id: str
    meeting_id: str
    llm_provider: LLMProvider
    content: SummaryContent
    format_type: str
    created_at: datetime
