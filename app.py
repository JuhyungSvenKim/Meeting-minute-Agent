import os
import tempfile
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from google import genai
from openai import OpenAI

load_dotenv()

app = FastAPI(title="Meeting Minute Agent")
templates = Jinja2Templates(directory="templates")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_WHISPER_MODEL = os.getenv("OPENAI_WHISPER_MODEL", "whisper-1")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-pro")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "error": None,
            "result": None,
            "transcript": None,
            "meeting_title": "",
            "language_hint": "ko",
        },
    )


def transcribe_with_whisper(audio_path: str, language_hint: Optional[str] = None) -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY가 설정되지 않았습니다.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=OPENAI_WHISPER_MODEL,
            file=audio_file,
            language=language_hint or None,
        )

    return response.text


def summarize_with_gemini(transcript: str, meeting_title: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다.")

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""
너는 시니어 PM 비서야. 아래 음성회의 전사본을 바탕으로 한국어 회의록을 작성해.

요구사항:
1) 핵심요약 5줄 이내
2) 논의사항(주제별 bullet)
3) 의사결정사항
4) 할일(Action Items): 담당자/기한/내용 표
5) 리스크 및 미해결 이슈
6) 다음 회의 안건 제안 3개

회의 제목: {meeting_title or '제목 미정'}

전사본:
{transcript}
"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text


@app.post("/upload", response_class=HTMLResponse)
async def upload_audio(
    request: Request,
    file: UploadFile = File(...),
    meeting_title: str = Form(default=""),
    language_hint: str = Form(default="ko"),
):
    if not file.filename.lower().endswith((".m4a", ".mp3", ".wav", ".mp4")):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "m4a/mp3/wav/mp4 파일만 업로드하세요.",
                "result": None,
                "transcript": None,
                "meeting_title": meeting_title,
                "language_hint": language_hint,
            },
            status_code=400,
        )

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_path = temp_file.name
            content = await file.read()
            temp_file.write(content)

        transcript = transcribe_with_whisper(temp_path, language_hint=language_hint)
        minutes = summarize_with_gemini(transcript, meeting_title)

        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": None,
                "result": minutes,
                "transcript": transcript,
                "meeting_title": meeting_title,
                "language_hint": language_hint,
            },
        )
    except Exception as e:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": f"처리 실패: {str(e)}",
                "result": None,
                "transcript": None,
                "meeting_title": meeting_title,
                "language_hint": language_hint,
            },
            status_code=500,
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
