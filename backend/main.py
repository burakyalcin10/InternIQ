"""InternIQ Backend — FastAPI Application"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers import listings, companies, cv, interview, crew

load_dotenv()

app = FastAPI(
    title="InternIQ API",
    description="AI-Powered Internship Platform Backend",
    version="1.0.0",
)

# CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(listings.router, prefix="/api/v1", tags=["Listings"])
app.include_router(companies.router, prefix="/api/v1", tags=["Companies"])
app.include_router(cv.router, prefix="/api/v1", tags=["CV"])
app.include_router(interview.router, prefix="/api/v1", tags=["Interview"])
app.include_router(crew.router, prefix="/api/v1", tags=["CrewAI"])


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
