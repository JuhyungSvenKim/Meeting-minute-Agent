# Meeting Minute Agent

회의 오디오를 업로드하면 화자 분리 트랜스크립트와 LLM 요약 회의록을 자동으로 생성하는 풀스택 애플리케이션입니다.

## 구성

- **Backend**: FastAPI + Supabase (Postgres + Storage)
- **Frontend**: Vue 3 + Vite + TypeScript + Tailwind CSS
- **AI**: Gemini (오디오 처리·요약), OpenAI Whisper (STT 보정), Claude/GPT-4o (요약)

## 파이프라인

1. `gemini` — Gemini만 사용. 빠르고 저렴.
2. `gemini_whisper` — Gemini의 화자 분리 + Whisper의 STT 텍스트로 보정.

## 빠른 시작

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일을 채워주세요 (최소 SUPABASE_*, GEMINI_API_KEY)

# 2. Supabase 마이그레이션
# supabase/migrations/0001_init.sql 을 Supabase SQL Editor에서 실행

# 3. Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 4. Frontend (다른 터미널)
cd frontend
npm install
npm run dev
```

`http://localhost:5173` 접속.

## 디렉토리

```
.
├── backend/                # FastAPI 서버
│   └── app/
│       ├── api/            # 라우터
│       ├── services/       # Gemini/Whisper/LLM/Export
│       ├── config.py
│       ├── db.py
│       ├── models.py
│       └── main.py
├── frontend/               # Vue 3 SPA
│   └── src/
│       ├── views/
│       ├── components/
│       ├── stores/
│       ├── services/
│       ├── types/
│       └── router/
└── supabase/
    └── migrations/
```

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| POST/GET/PATCH/DELETE | `/api/meetings` | 회의 CRUD |
| POST | `/api/meetings/{id}/audio` | 오디오 업로드 |
| POST | `/api/meetings/{id}/process` | 파이프라인 시작 |
| GET  | `/api/meetings/{id}/process/status` | 진행 상태 폴링 |
| GET  | `/api/meetings/{id}/transcript` | 트랜스크립트 조회 |
| PATCH| `/api/meetings/{id}/speakers/{label}` | 화자 이름 수정 |
| POST | `/api/meetings/{id}/summarize` | 요약 생성/재생성 |
| GET  | `/api/meetings/{id}/export/{pdf\|md\|txt}` | 회의록 내보내기 |
