"""Clinical evidence management API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()


@router.get("/")
async def get_evidence():
    """Get clinical evidence data."""
    return {"message": "Clinical evidence endpoint - to be implemented"}


@router.post("/")
async def create_evidence():
    """Create new clinical evidence entry."""
    return {"message": "Create evidence endpoint - to be implemented"}
