from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .dependencies import get_case_store
from .models import HealthResponse
from .routers import cases, sessions, conversations, analysis, reports, tts


@asynccontextmanager
async def lifespan(app: FastAPI):
    store = get_case_store()
    print(f"Loaded {len(store.list_all())} cases from {settings.cases_file}")
    print(f"Agent ID: {settings.agent_id}")
    yield


app = FastAPI(
    title="VERDICT API",
    description="Backend for the VERDICT AI Deposition Interrogation System",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.lovable\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(sessions.router)
app.include_router(conversations.router)
app.include_router(analysis.router)
app.include_router(reports.router)
app.include_router(tts.router)


@app.get("/api/health", response_model=HealthResponse, tags=["health"])
async def health():
    store = get_case_store()
    return HealthResponse(
        status="ok",
        agent_id=settings.agent_id,
        cases_loaded=len(store.list_all()),
    )
