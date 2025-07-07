"""Dossier management API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from ..models.dossier import (
    DossierCreate,
    DossierResponse,
    DossierUpdate,
    DossierStatus
)
from ..services.dossier_service import DossierService

router = APIRouter()


@router.get("/", response_model=List[DossierResponse])
async def get_dossiers(
    status: Optional[DossierStatus] = None,
    framework: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    dossier_service: DossierService = Depends()
):
    """Get list of value dossiers with optional filtering."""
    return await dossier_service.get_dossiers(
        status=status,
        framework=framework,
        skip=skip,
        limit=limit
    )


@router.post("/", response_model=DossierResponse)
async def create_dossier(
    dossier: DossierCreate,
    dossier_service: DossierService = Depends()
):
    """Create a new value dossier."""
    return await dossier_service.create_dossier(dossier)


@router.get("/{dossier_id}", response_model=DossierResponse)
async def get_dossier(
    dossier_id: str,
    dossier_service: DossierService = Depends()
):
    """Get a specific value dossier by ID."""
    dossier = await dossier_service.get_dossier(dossier_id)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return dossier


@router.put("/{dossier_id}", response_model=DossierResponse)
async def update_dossier(
    dossier_id: str,
    dossier_update: DossierUpdate,
    dossier_service: DossierService = Depends()
):
    """Update a value dossier."""
    dossier = await dossier_service.update_dossier(dossier_id, dossier_update)
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return dossier


@router.delete("/{dossier_id}")
async def delete_dossier(
    dossier_id: str,
    dossier_service: DossierService = Depends()
):
    """Delete a value dossier."""
    success = await dossier_service.delete_dossier(dossier_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return {"message": "Dossier deleted successfully"}


@router.post("/{dossier_id}/export")
async def export_dossier(
    dossier_id: str,
    format: str = "pdf",
    dossier_service: DossierService = Depends()
):
    """Export a value dossier to specified format."""
    export_result = await dossier_service.export_dossier(dossier_id, format)
    if not export_result:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return export_result


@router.post("/{dossier_id}/submit")
async def submit_dossier(
    dossier_id: str,
    submission_data: dict,
    dossier_service: DossierService = Depends()
):
    """Submit a value dossier for review or to HTA authority."""
    result = await dossier_service.submit_dossier(dossier_id, submission_data)
    if not result:
        raise HTTPException(status_code=404, detail="Dossier not found")
    return result
