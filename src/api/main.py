"""FastAPI main application for MedAI Dossier."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from .routers import dossiers, evidence, economics, hta
from ..core.config import get_settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan management."""
    logger.info("Starting MedAI Dossier API...")
    
    # Startup tasks
    yield
    
    # Shutdown tasks
    logger.info("Shutting down MedAI Dossier API...")


# Create FastAPI application
app = FastAPI(
    title="MedAI Dossier API",
    description="Value Dossier Management System for HTA and Market Access",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    dossiers.router,
    prefix="/api/v1/dossiers",
    tags=["dossiers"]
)

app.include_router(
    evidence.router,
    prefix="/api/v1/evidence",
    tags=["evidence"]
)

app.include_router(
    economics.router,
    prefix="/api/v1/economics",
    tags=["economics"]
)

app.include_router(
    hta.router,
    prefix="/api/v1/hta",
    tags=["hta"]
)

# Mount static files (if needed)
# app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "MedAI Dossier API",
        "version": "0.1.0",
        "description": "Value Dossier Management System",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "medai-dossier-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
