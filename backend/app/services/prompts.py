"""Prompt templates for Gemini and other LLMs."""
from __future__ import annotations

GEMINI_TRANSCRIBE_PROMPT = """\
You are a meeting transcription assistant. The audio attached is a recorded
meeting that may include multiple speakers.

Tasks:
1. Diarize the speakers. Assign stable labels like "S1", "S2", ...
2. Transcribe the speech verbatim in the original language (preserve Korean
   when spoken in Korean).
3. For each speaker, infer a likely gender estimate ("male", "female", or
   "unknown").
4. Produce a high-quality structured meeting summary in the same language as
   the dominant speech.

Return ONLY a JSON object with this exact shape (no prose, no code fences):

{
  "language": "ko" | "en" | ...,
  "speakers": [
    {"speaker_label": "S1", "gender_estimate": "male|female|unknown"}
  ],
  "segments": [
    {
      "speaker_label": "S1",
      "start_time": 0.00,
      "end_time": 3.42,
      "text": "..."
    }
  ],
  "summary": {
    "title": "string",
    "attendees": ["S1", "S2"],
    "summary": "2-4 sentence overview",
    "key_points": ["..."],
    "decisions": ["..."],
    "action_items": [
      {"title": "...", "owner": "S1 or name", "due_date": "YYYY-MM-DD or null"}
    ]
  }
}

Rules:
- start_time/end_time are floats in seconds.
- segments must be ordered by start_time.
- Keep segment text natural; do not split mid-word.
- If a section has no items, return an empty array.
- Output JSON only.
"""


SUMMARIZE_SYSTEM = """\
You are an executive assistant summarizing a meeting transcript. Produce a
clear, neutral, structured summary in the SAME language as the transcript.

Output ONLY a JSON object matching:
{
  "title": "string",
  "attendees": ["..."],
  "summary": "2-5 sentence overview",
  "key_points": ["..."],
  "decisions": ["..."],
  "action_items": [
    {"title": "...", "owner": "...", "due_date": "YYYY-MM-DD or null"}
  ]
}
Empty arrays when nothing applies. No prose outside the JSON.
"""


def build_summarize_user_prompt(transcript_text: str) -> str:
    return (
        "Below is a meeting transcript with speaker labels. Produce the JSON "
        "summary as instructed.\n\n--- TRANSCRIPT ---\n"
        f"{transcript_text}\n--- END TRANSCRIPT ---"
    )
