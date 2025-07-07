"""Pydantic models for Value Dossier management."""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class DossierStatus(str, Enum):
    """Dossier status enumeration."""
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class HTAFramework(str, Enum):
    """HTA Framework enumeration."""
    AMCP = "amcp"
    EUNETHTA = "eunethta"
    G_BA = "g_ba"
    NICE = "nice"
    HAS = "has"
    CADTH = "cadth"
    PBAC = "pbac"


class TherapeuticArea(str, Enum):
    """Therapeutic area enumeration."""
    ONCOLOGY = "oncology"
    CARDIOVASCULAR = "cardiovascular"
    NEUROLOGY = "neurology"
    INFECTIOUS_DISEASES = "infectious_diseases"
    IMMUNOLOGY = "immunology"
    ENDOCRINOLOGY = "endocrinology"
    RESPIRATORY = "respiratory"
    GASTROENTEROLOGY = "gastroenterology"
    DERMATOLOGY = "dermatology"
    OPHTHALMOLOGY = "ophthalmology"
    OTHER = "other"


class ProductProfile(BaseModel):
    """Product profile information."""
    product_name: str = Field(..., min_length=1, max_length=200)
    active_ingredient: str = Field(..., min_length=1, max_length=200)
    indication: str = Field(..., min_length=1, max_length=500)
    mechanism_of_action: Optional[str] = Field(None, max_length=1000)
    dosage_form: Optional[str] = Field(None, max_length=100)
    route_of_administration: Optional[str] = Field(None, max_length=100)
    therapeutic_area: TherapeuticArea
    orphan_designation: bool = Field(default=False)
    breakthrough_therapy: bool = Field(default=False)
    
    class Config:
        """Pydantic configuration."""
        frozen = True
        validate_assignment = True


class ClinicalEvidence(BaseModel):
    """Clinical evidence summary."""
    primary_endpoint: str = Field(..., min_length=1, max_length=500)
    primary_result: Optional[str] = Field(None, max_length=1000)
    secondary_endpoints: List[str] = Field(default_factory=list)
    study_population: Optional[str] = Field(None, max_length=500)
    comparator: Optional[str] = Field(None, max_length=200)
    study_design: Optional[str] = Field(None, max_length=200)
    sample_size: Optional[int] = Field(None, gt=0)
    follow_up_duration: Optional[str] = Field(None, max_length=100)
    
    class Config:
        """Pydantic configuration."""
        frozen = True
        validate_assignment = True


class EconomicEvidence(BaseModel):
    """Health economic evidence."""
    cost_effectiveness_ratio: Optional[float] = Field(None, gt=0)
    budget_impact_year_1: Optional[float] = Field(None)
    budget_impact_year_3: Optional[float] = Field(None)
    budget_impact_year_5: Optional[float] = Field(None)
    qaly_gain: Optional[float] = Field(None, gt=0)
    cost_per_qaly: Optional[float] = Field(None, gt=0)
    willingness_to_pay_threshold: Optional[float] = Field(None, gt=0)
    model_type: Optional[str] = Field(None, max_length=100)
    time_horizon: Optional[str] = Field(None, max_length=100)
    
    class Config:
        """Pydantic configuration."""
        frozen = True
        validate_assignment = True


class PatientPerspective(BaseModel):
    """Patient perspective and outcomes."""
    quality_of_life_improvement: Optional[bool] = Field(None)
    patient_reported_outcomes: List[str] = Field(default_factory=list)
    treatment_satisfaction: Optional[float] = Field(None, ge=0, le=10)
    adherence_rate: Optional[float] = Field(None, ge=0, le=1)
    convenience_factors: List[str] = Field(default_factory=list)
    unmet_need_addressed: Optional[str] = Field(None, max_length=1000)
    
    class Config:
        """Pydantic configuration."""
        frozen = True
        validate_assignment = True


class DossierBase(BaseModel):
    """Base dossier model."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    hta_framework: HTAFramework
    product_profile: ProductProfile
    target_price: Optional[float] = Field(None, gt=0)
    target_population_size: Optional[int] = Field(None, gt=0)
    launch_date: Optional[datetime] = Field(None)
    
    @validator("launch_date")
    def validate_launch_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Validate launch date is not in the past."""
        if v and v < datetime.now():
            raise ValueError("Launch date cannot be in the past")
        return v


class DossierCreate(DossierBase):
    """Model for creating a new dossier."""
    clinical_evidence: Optional[ClinicalEvidence] = Field(None)
    economic_evidence: Optional[EconomicEvidence] = Field(None)
    patient_perspective: Optional[PatientPerspective] = Field(None)


class DossierUpdate(BaseModel):
    """Model for updating a dossier."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[DossierStatus] = Field(None)
    clinical_evidence: Optional[ClinicalEvidence] = Field(None)
    economic_evidence: Optional[EconomicEvidence] = Field(None)
    patient_perspective: Optional[PatientPerspective] = Field(None)
    target_price: Optional[float] = Field(None, gt=0)
    target_population_size: Optional[int] = Field(None, gt=0)
    launch_date: Optional[datetime] = Field(None)


class DossierResponse(DossierBase):
    """Model for dossier responses."""
    id: str = Field(..., description="Unique dossier identifier")
    status: DossierStatus = Field(default=DossierStatus.DRAFT)
    version: str = Field(default="1.0.0")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: Optional[str] = Field(None, max_length=100)
    last_modified_by: Optional[str] = Field(None, max_length=100)
    
    clinical_evidence: Optional[ClinicalEvidence] = Field(None)
    economic_evidence: Optional[EconomicEvidence] = Field(None)
    patient_perspective: Optional[PatientPerspective] = Field(None)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)
    submission_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
