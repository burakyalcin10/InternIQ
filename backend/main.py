"""InternIQ Backend - FastAPI Application."""

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def load_local_env() -> None:
    """Load backend/.env explicitly; python-dotenv misses it on this setup."""
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    load_dotenv(env_path, override=False)

    if os.getenv("GEMINI_API_KEY"):
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


load_local_env()

from routers import auth, companies, crew, cv, interview, listings, workflow

app = FastAPI(
    title="InternIQ API",
    description="AI-Powered Internship Platform Backend",
    version="1.0.0",
)

DEFAULT_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "").split(",")
    if origin.strip()
]
origins = list(dict.fromkeys([*origins, *DEFAULT_CORS_ORIGINS]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(listings.router, prefix="/api/v1", tags=["Listings"])
app.include_router(companies.router, prefix="/api/v1", tags=["Companies"])
app.include_router(cv.router, prefix="/api/v1", tags=["CV"])
app.include_router(interview.router, prefix="/api/v1", tags=["Interview"])
app.include_router(crew.router, prefix="/api/v1", tags=["CrewAI"])
app.include_router(workflow.router, prefix="/api/v1", tags=["LangGraph Workflow"])


@app.get("/")
async def root():
    return {
        "name": "InternIQ API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "ok"}
