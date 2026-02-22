from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, AsyncSessionLocal
from app.routers import auth, cases, sessions, briefs, tts, conversations, documents, witnesses
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="VERDICT API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "https://verdict-io.lovable.app",
        "https://*.vercel.app",
        "https://*.up.railway.app",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "x-request-id"],
)

app.include_router(auth.router,     prefix="/api/v1/auth")
app.include_router(cases.router,    prefix="/api/v1/cases")
app.include_router(sessions.router, prefix="/api/v1/sessions")
app.include_router(briefs.router,   prefix="/api/v1/briefs")
app.include_router(tts.router, prefix="/api/v1/tts")
app.include_router(conversations.router, prefix="/api/v1/conversations")
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
