"""Health economics management API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()


@router.get("/")
async def get_economic_models():
    """Get health economic models and analyses."""
    return {"message": "Health economics endpoint - to be implemented"}


@router.post("/")
async def create_economic_model():
    """Create new health economic model."""
    return {"message": "Create economic model endpoint - to be implemented"}
