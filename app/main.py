"""Application entrypoint."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.db.database import Base, engine

app = FastAPI(title="Gymyo Adaptive Training API", version="0.2.0")
app.include_router(router, prefix="/api")


@app.on_event("startup")
def startup() -> None:
    """Initialize schema."""
    Base.metadata.create_all(bind=engine)


WEB_DIST = Path(__file__).resolve().parents[1] / "web" / "dist"
if WEB_DIST.exists():
    app.mount("/assets", StaticFiles(directory=WEB_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str) -> FileResponse:
        """Serve built single-page app in production."""
        requested = WEB_DIST / full_path
        if full_path and requested.exists() and requested.is_file():
            return FileResponse(requested)
        return FileResponse(WEB_DIST / "index.html")
