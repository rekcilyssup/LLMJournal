from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.journal import router as journal_router
from core.config import settings
from core.database import Base, engine
from models import db_models  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI-Assisted Journal System API",
        version="1.0.0",
        description="Backend API for journal entries, LLM analysis, and insights.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(journal_router)

    @app.get("/health", tags=["health"])
    def health_check() -> dict:
        return {"status": "ok"}

    return app


app = create_app()


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
