"""Unit tests for dossier service."""

import pytest
from datetime import datetime
from src.api.services.dossier_service import DossierService
from src.api.models.dossier import (
    DossierCreate,
    DossierUpdate,
    DossierStatus,
    HTAFramework,
    TherapeuticArea,
    ProductProfile
)


@pytest.fixture
def dossier_service():
    """Create dossier service instance for testing."""
    return DossierService()


@pytest.fixture
def sample_product_profile():
    """Create sample product profile for testing."""
    return ProductProfile(
        product_name="Test Drug",
        active_ingredient="Test Compound",
        indication="Test Indication",
        mechanism_of_action="Test MOA",
        therapeutic_area=TherapeuticArea.ONCOLOGY,
        orphan_designation=False,
        breakthrough_therapy=True
    )


@pytest.fixture
def sample_dossier_create(sample_product_profile):
    """Create sample dossier create data for testing."""
    return DossierCreate(
        title="Test Value Dossier",
        description="Test description",
        hta_framework=HTAFramework.NICE,
        product_profile=sample_product_profile,
        target_price=10000.0,
        target_population_size=50000
    )


class TestDossierService:
    """Test cases for DossierService."""

    @pytest.mark.asyncio
    async def test_should_create_dossier_when_valid_data(
        self, 
        dossier_service: DossierService,
        sample_dossier_create: DossierCreate
    ):
        """Test creating a dossier with valid data."""
        # When
        result = await dossier_service.create_dossier(sample_dossier_create)
        
        # Then
        assert result is not None
        assert result.title == sample_dossier_create.title
        assert result.status == DossierStatus.DRAFT
        assert result.version == "1.0.0"
        assert result.id is not None

    @pytest.mark.asyncio
    async def test_should_get_dossier_when_exists(
        self,
        dossier_service: DossierService,
        sample_dossier_create: DossierCreate
    ):
        """Test getting an existing dossier."""
        # Given
        created_dossier = await dossier_service.create_dossier(sample_dossier_create)
        
        # When
        result = await dossier_service.get_dossier(created_dossier.id)
        
        # Then
        assert result is not None
        assert result.id == created_dossier.id
        assert result.title == created_dossier.title

    @pytest.mark.asyncio
    async def test_should_return_none_when_dossier_not_exists(
        self,
        dossier_service: DossierService
    ):
        """Test getting a non-existent dossier."""
        # When
        result = await dossier_service.get_dossier("non-existent-id")
        
        # Then
        assert result is None

    @pytest.mark.asyncio
    async def test_should_update_dossier_when_exists(
        self,
        dossier_service: DossierService,
        sample_dossier_create: DossierCreate
    ):
        """Test updating an existing dossier."""
        # Given
        created_dossier = await dossier_service.create_dossier(sample_dossier_create)
        update_data = DossierUpdate(
            title="Updated Title",
            status=DossierStatus.IN_REVIEW
        )
        
        # When
        result = await dossier_service.update_dossier(created_dossier.id, update_data)
        
        # Then
        assert result is not None
        assert result.title == "Updated Title"
        assert result.status == DossierStatus.IN_REVIEW
        assert result.updated_at > result.created_at

    @pytest.mark.asyncio
    async def test_should_delete_dossier_when_exists(
        self,
        dossier_service: DossierService,
        sample_dossier_create: DossierCreate
    ):
        """Test deleting an existing dossier."""
        # Given
        created_dossier = await dossier_service.create_dossier(sample_dossier_create)
        
        # When
        result = await dossier_service.delete_dossier(created_dossier.id)
        
        # Then
        assert result is True
        
        # Verify dossier is deleted
        deleted_dossier = await dossier_service.get_dossier(created_dossier.id)
        assert deleted_dossier is None

    @pytest.mark.asyncio
    async def test_should_export_dossier_when_exists(
        self,
        dossier_service: DossierService,
        sample_dossier_create: DossierCreate
    ):
        """Test exporting an existing dossier."""
        # Given
        created_dossier = await dossier_service.create_dossier(sample_dossier_create)
        
        # When
        result = await dossier_service.export_dossier(created_dossier.id, "pdf")
        
        # Then
        assert result is not None
        assert result["dossier_id"] == created_dossier.id
        assert result["format"] == "pdf"
        assert result["status"] == "generated"

    @pytest.mark.asyncio
    async def test_should_submit_dossier_when_exists(
        self,
        dossier_service: DossierService,
        sample_dossier_create: DossierCreate
    ):
        """Test submitting an existing dossier."""
        # Given
        created_dossier = await dossier_service.create_dossier(sample_dossier_create)
        submission_data = {
            "authority": "NICE",
            "type": "Standard"
        }
        
        # When
        result = await dossier_service.submit_dossier(created_dossier.id, submission_data)
        
        # Then
        assert result is not None
        assert result["submission_status"] == "submitted"
        assert result["dossier_id"] == created_dossier.id
        
        # Verify dossier status is updated
        updated_dossier = await dossier_service.get_dossier(created_dossier.id)
        assert updated_dossier.status == DossierStatus.SUBMITTED

    @pytest.mark.asyncio
    async def test_should_filter_dossiers_by_status(
        self,
        dossier_service: DossierService,
        sample_dossier_create: DossierCreate
    ):
        """Test filtering dossiers by status."""
        # Given
        created_dossier = await dossier_service.create_dossier(sample_dossier_create)
        await dossier_service.update_dossier(
            created_dossier.id, 
            DossierUpdate(status=DossierStatus.APPROVED)
        )
        
        # When
        draft_dossiers = await dossier_service.get_dossiers(status=DossierStatus.DRAFT)
        approved_dossiers = await dossier_service.get_dossiers(status=DossierStatus.APPROVED)
        
        # Then
        assert len(draft_dossiers) == 0
        assert len(approved_dossiers) == 1
        assert approved_dossiers[0].status == DossierStatus.APPROVED
