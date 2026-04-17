# Meeting Minute Agent

m4a 음성메모를 업로드하면,

1. OpenAI Whisper 모델로 전사하고
2. Gemini 3.1 Pro 모델로 한국어 회의록을 생성하는

빠른 프로토타입 웹앱입니다.

## 빠른 시작

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env에 API 키 입력
python app.py
```

브라우저에서 `http://localhost:8000` 접속.

## 환경 변수

- `OPENAI_API_KEY`: OpenAI API 키
- `OPENAI_WHISPER_MODEL`: 기본 `whisper-1`
- `GEMINI_API_KEY`: Gemini API 키
- `GEMINI_MODEL`: 기본 `gemini-3.1-pro`

## 참고

- 업로드 파일 포맷: `.m4a`, `.mp3`, `.wav`, `.mp4`
- 기본 언어 힌트: `ko`
