from typing import Annotated

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .api.routes import alerts, auth, events, health, investigations, rules, statistics
from .config import get_settings
from .api.dependencies import current_user
from .database import engine
from .models import User
from . import models  # noqa: F401

settings = get_settings()
app = FastAPI(title=settings.app_name, version=settings.version, description="Educational defensive security monitoring platform")
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_host_list)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(alerts.router)
app.include_router(statistics.router)
app.include_router(investigations.router)
app.include_router(rules.router)


@app.get("/api/reports/{fmt}")
def generate_report(fmt: str, _: Annotated[User, Depends(current_user)]):
    from fastapi import HTTPException
    from .database import SessionLocal
    from .services.report_service import report
    if fmt not in {"json", "markdown", "html"}:
        raise HTTPException(400, "format must be json, markdown, or html")
    db = SessionLocal()
    try:
        return report(db, fmt) if fmt != "json" else {"report": report(db, fmt)}
    finally:
        db.close()
