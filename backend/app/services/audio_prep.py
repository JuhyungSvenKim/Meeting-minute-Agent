"""Optional pre-processing: re-encode large audio with ffmpeg to shrink it
below Gemini's inline limit (and speed up model processing significantly).

If ffmpeg isn't installed, this is a no-op — the original bytes are returned.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

log = logging.getLogger(__name__)

# Target: Opus 32 kbps mono — speech-optimal, ~10x smaller than typical MP3.
FFMPEG_ARGS = [
    "-vn",
    "-ac", "1",
    "-ar", "16000",
    "-c:a", "libopus",
    "-b:a", "32k",
    "-f", "ogg",
]

# Skip compression for inputs already small enough.
SKIP_IF_UNDER_BYTES = 18 * 1024 * 1024


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def maybe_compress(
    audio_bytes: bytes, filename: str
) -> tuple[bytes, str, bool]:
    """Return (bytes, mime_type, was_compressed)."""
    if len(audio_bytes) < SKIP_IF_UNDER_BYTES:
        return audio_bytes, _guess_mime(filename), False
    if not ffmpeg_available():
        log.warning("ffmpeg not installed; uploading original audio as-is")
        return audio_bytes, _guess_mime(filename), False

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / ("input" + _ext(filename))
        dst = Path(tmp) / "output.ogg"
        src.write_bytes(audio_bytes)

        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(src), *FFMPEG_ARGS, str(dst)],
                check=True,
                capture_output=True,
                timeout=60 * 10,
            )
        except subprocess.TimeoutExpired:
            log.warning("ffmpeg compression timed out; using original")
            return audio_bytes, _guess_mime(filename), False
        except subprocess.CalledProcessError as e:
            log.warning("ffmpeg failed (%s); using original", e.stderr[:300] if e.stderr else "")
            return audio_bytes, _guess_mime(filename), False

        compressed = dst.read_bytes()
        log.info(
            "Compressed audio %.1f MB -> %.1f MB",
            len(audio_bytes) / 1024 / 1024,
            len(compressed) / 1024 / 1024,
        )
        return compressed, "audio/ogg", True


def _ext(filename: str) -> str:
    if "." in filename:
        return "." + filename.rsplit(".", 1)[-1].lower()
    return ".bin"


def _guess_mime(filename: str) -> str:
    ext = _ext(filename).lower()
    return {
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".mp4": "video/mp4",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
        ".opus": "audio/ogg",
        ".webm": "audio/webm",
        ".flac": "audio/flac",
    }.get(ext, "application/octet-stream")
