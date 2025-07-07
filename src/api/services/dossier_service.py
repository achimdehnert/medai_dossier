"""Dossier service implementation."""

from typing import List, Optional
import uuid
from datetime import datetime

from ..models.dossier import (
    DossierCreate,
    DossierResponse,
    DossierUpdate,
    DossierStatus
)


class DossierService:
    """Service for managing value dossiers."""
    
    def __init__(self):
        """Initialize dossier service."""
        # In-memory storage for demo purposes
        # In production, this would use a database
        self._dossiers: dict[str, DossierResponse] = {}
    
    async def get_dossiers(
        self,
        status: Optional[DossierStatus] = None,
        framework: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DossierResponse]:
        """Get list of dossiers with optional filtering."""
        dossiers = list(self._dossiers.values())
        
        # Apply filters
        if status:
            dossiers = [d for d in dossiers if d.status == status]
        
        if framework:
            dossiers = [d for d in dossiers if d.hta_framework == framework]
        
        # Apply pagination
        return dossiers[skip:skip + limit]
    
    async def get_dossier(self, dossier_id: str) -> Optional[DossierResponse]:
        """Get a specific dossier by ID."""
        return self._dossiers.get(dossier_id)
    
    async def create_dossier(self, dossier_data: DossierCreate) -> DossierResponse:
        """Create a new dossier."""
        dossier_id = str(uuid.uuid4())
        now = datetime.now()
        
        # Create dossier response object
        dossier = DossierResponse(
            id=dossier_id,
            title=dossier_data.title,
            description=dossier_data.description,
            hta_framework=dossier_data.hta_framework,
            product_profile=dossier_data.product_profile,
            target_price=dossier_data.target_price,
            target_population_size=dossier_data.target_population_size,
            launch_date=dossier_data.launch_date,
            status=DossierStatus.DRAFT,
            version="1.0.0",
            created_at=now,
            updated_at=now,
            clinical_evidence=dossier_data.clinical_evidence,
            economic_evidence=dossier_data.economic_evidence,
            patient_perspective=dossier_data.patient_perspective
        )
        
        # Store dossier
        self._dossiers[dossier_id] = dossier
        
        return dossier
    
    async def update_dossier(
        self, 
        dossier_id: str, 
        update_data: DossierUpdate
    ) -> Optional[DossierResponse]:
        """Update an existing dossier."""
        if dossier_id not in self._dossiers:
            return None
        
        dossier = self._dossiers[dossier_id]
        
        # Update fields that are provided
        update_dict = update_data.dict(exclude_unset=True)
        
        for field, value in update_dict.items():
            if hasattr(dossier, field):
                setattr(dossier, field, value)
        
        # Update timestamp
        dossier.updated_at = datetime.now()
        
        return dossier
    
    async def delete_dossier(self, dossier_id: str) -> bool:
        """Delete a dossier."""
        if dossier_id in self._dossiers:
            del self._dossiers[dossier_id]
            return True
        return False
    
    async def export_dossier(
        self, 
        dossier_id: str, 
        format: str = "pdf"
    ) -> Optional[dict]:
        """Export a dossier to specified format."""
        if dossier_id not in self._dossiers:
            return None
        
        dossier = self._dossiers[dossier_id]
        
        # In production, this would generate actual export files
        return {
            "dossier_id": dossier_id,
            "format": format,
            "filename": f"{dossier.title}_{dossier.version}.{format}",
            "export_date": datetime.now().isoformat(),
            "status": "generated"
        }
    
    async def submit_dossier(
        self, 
        dossier_id: str, 
        submission_data: dict
    ) -> Optional[dict]:
        """Submit a dossier for review or to HTA authority."""
        if dossier_id not in self._dossiers:
            return None
        
        dossier = self._dossiers[dossier_id]
        
        # Update status to submitted
        dossier.status = DossierStatus.SUBMITTED
        dossier.updated_at = datetime.now()
        
        # Add to submission history
        submission_entry = {
            "submission_date": datetime.now().isoformat(),
            "authority": submission_data.get("authority", "Unknown"),
            "submission_type": submission_data.get("type", "Standard"),
            "reference_number": f"SUB-{dossier_id[:8]}"
        }
        
        dossier.submission_history.append(submission_entry)
        
        return {
            "dossier_id": dossier_id,
            "submission_status": "submitted",
            "reference_number": submission_entry["reference_number"],
            "submission_date": submission_entry["submission_date"]
        }
