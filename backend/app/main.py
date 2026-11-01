from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import alerts, events, health, investigations, statistics
from .config import get_settings
from .database import Base, engine
from . import models  # noqa: F401

settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version=settings.version, description="Educational defensive security monitoring platform")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router); app.include_router(events.router); app.include_router(alerts.router); app.include_router(statistics.router); app.include_router(investigations.router)


@app.get("/api/reports/{fmt}")
def generate_report(fmt: str):
    from fastapi import HTTPException
    from .database import SessionLocal
    from .services.report_service import report
    if fmt not in {"json", "markdown", "html"}: raise HTTPException(400, "format must be json, markdown, or html")
    db = SessionLocal()
    try:
        return report(db, fmt) if fmt != "json" else {"report": report(db, fmt)}
    finally:
        db.close()
