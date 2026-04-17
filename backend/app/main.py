from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import audio, export, meetings, process, summarize, transcripts
from .config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Meeting Minute Agent", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(meetings.router)
    app.include_router(audio.router)
    app.include_router(process.router)
    app.include_router(transcripts.router)
    app.include_router(summarize.router)
    app.include_router(export.router)

    @app.get("/")
    def root():
        return {"service": "meeting-minute-agent", "status": "ok"}

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
