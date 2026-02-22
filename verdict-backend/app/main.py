import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import engine, AsyncSessionLocal
from app.routers import auth, cases, sessions, briefs, documents, witnesses
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="VERDICT API", version="1.0.0", lifespan=lifespan)

# Explicit origins required when allow_credentials=True (browser rejects "*")
_cors_origins = [
    settings.FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
    "https://verdict-io.lovable.app",
]
app.add_middleware(
    CORSMiddleware,
<<<<<<< Updated upstream
<<<<<<< Updated upstream
    allow_origins=[
        settings.FRONTEND_URL,
        "https://verdict-io.lovable.app",
        "https://*.vercel.app",
    ],
=======
    allow_origins=[o for o in _cors_origins if o],
>>>>>>> Stashed changes
=======
    allow_origins=[o for o in _cors_origins if o],
>>>>>>> Stashed changes
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "x-request-id"],
)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Return 500 as JSON with message so login/auth errors are debuggable."""
    logging.exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content={"detail": {"code": "SERVER_ERROR", "message": str(exc)}},
    )

app.include_router(auth.router,     prefix="/api/v1/auth")
app.include_router(cases.router,    prefix="/api/v1/cases")
app.include_router(sessions.router, prefix="/api/v1/sessions")
app.include_router(briefs.router,   prefix="/api/v1/briefs")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(witnesses.router, prefix="/api/v1/cases")


@app.get("/api/v1")
async def root():
    return {"message": "VERDICT API", "version": "v1"}


@app.get("/api/v1/health")
async def health():
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "ok", "timestamp": __import__("datetime").datetime.utcnow().isoformat(), "version": "1.0.0", "db": "connected"}
    except Exception:
        return {"status": "degraded", "timestamp": __import__("datetime").datetime.utcnow().isoformat(), "version": "1.0.0", "db": "disconnected"}
