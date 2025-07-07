"""Tests for evidence service."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.services.evidence_service import EvidenceService
from src.models.evidence import (
    EvidenceType,
    StudyDesign,
    OutcomeType,
    RiskOfBias
)


@pytest.fixture
def evidence_service():
    """Create evidence service instance."""
    return EvidenceService()


@pytest.fixture
def sample_evidence_data():
    """Create sample evidence data."""
    return {
        "id": "ev_001",
        "title": "Phase III Randomized Controlled Trial",
        "description": "Efficacy and safety study of new treatment",
        "evidence_type": EvidenceType.CLINICAL_TRIAL,
        "study_design": StudyDesign.RCT,
        "sample_size": 500,
        "study_population": "Adult patients with condition X",
        "primary_endpoint": "Overall survival",
        "secondary_endpoints": ["Progression-free survival", "Quality of life"],
        "outcome_measures": {
            OutcomeType.EFFICACY: {
                "hazard_ratio": 0.75,
                "confidence_interval": "0.65-0.87",
                "p_value": 0.001
            }
        },
        "risk_of_bias": RiskOfBias.LOW,
        "publication_status": "published",
        "citation": "Smith J, et al. J Med. 2023;45:123-135."
    }


class TestEvidenceService:
    """Test evidence service functionality."""
    
    @pytest.mark.asyncio
    async def test_should_create_evidence_when_valid_data_provided(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence creation with valid data."""
        # Act
        evidence = await evidence_service.create_evidence(sample_evidence_data)
        
        # Assert
        assert evidence.id == sample_evidence_data["id"]
        assert evidence.title == sample_evidence_data["title"]
        assert evidence.evidence_type == EvidenceType.CLINICAL_TRIAL
        assert evidence.study_design == StudyDesign.RCT
        assert evidence.sample_size == 500
        assert evidence.risk_of_bias == RiskOfBias.LOW
    
    @pytest.mark.asyncio
    async def test_should_raise_error_when_invalid_data_provided(
        self,
        evidence_service: EvidenceService
    ):
        """Test evidence creation with invalid data."""
        # Arrange
        invalid_data = {
            "title": "",  # Empty title should be invalid
            "evidence_type": "invalid_type"
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid evidence data"):
            await evidence_service.create_evidence(invalid_data)
    
    @pytest.mark.asyncio
    async def test_should_retrieve_evidence_when_exists(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence retrieval."""
        # Arrange
        created_evidence = await evidence_service.create_evidence(sample_evidence_data)
        
        # Act
        retrieved_evidence = await evidence_service.get_evidence(created_evidence.id)
        
        # Assert
        assert retrieved_evidence is not None
        assert retrieved_evidence.id == created_evidence.id
        assert retrieved_evidence.title == created_evidence.title
    
    @pytest.mark.asyncio
    async def test_should_return_none_when_evidence_not_exists(
        self,
        evidence_service: EvidenceService
    ):
        """Test evidence retrieval for non-existent ID."""
        # Act
        evidence = await evidence_service.get_evidence("non_existent_id")
        
        # Assert
        assert evidence is None
    
    @pytest.mark.asyncio
    async def test_should_list_evidence_with_filters(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence listing with filters."""
        # Arrange
        await evidence_service.create_evidence(sample_evidence_data)
        
        # Create second evidence with different type
        second_evidence = sample_evidence_data.copy()
        second_evidence["id"] = "ev_002"
        second_evidence["evidence_type"] = EvidenceType.REAL_WORLD_EVIDENCE
        await evidence_service.create_evidence(second_evidence)
        
        # Act - Filter by clinical trial type
        clinical_trials = await evidence_service.list_evidence(
            evidence_type=EvidenceType.CLINICAL_TRIAL
        )
        
        # Act - Filter by RWE type
        rwe_studies = await evidence_service.list_evidence(
            evidence_type=EvidenceType.REAL_WORLD_EVIDENCE
        )
        
        # Assert
        assert len(clinical_trials) == 1
        assert clinical_trials[0].evidence_type == EvidenceType.CLINICAL_TRIAL
        
        assert len(rwe_studies) == 1
        assert rwe_studies[0].evidence_type == EvidenceType.REAL_WORLD_EVIDENCE
    
    @pytest.mark.asyncio
    async def test_should_update_evidence_when_valid_data_provided(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence update."""
        # Arrange
        evidence = await evidence_service.create_evidence(sample_evidence_data)
        
        updates = {
            "title": "Updated Phase III RCT",
            "sample_size": 600
        }
        
        # Act
        updated_evidence = await evidence_service.update_evidence(
            evidence.id, updates
        )
        
        # Assert
        assert updated_evidence is not None
        assert updated_evidence.title == "Updated Phase III RCT"
        assert updated_evidence.sample_size == 600
        assert updated_evidence.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_should_return_none_when_updating_non_existent_evidence(
        self,
        evidence_service: EvidenceService
    ):
        """Test update of non-existent evidence."""
        # Act
        result = await evidence_service.update_evidence(
            "non_existent_id", {"title": "Updated"}
        )
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_should_delete_evidence_when_exists(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence deletion."""
        # Arrange
        evidence = await evidence_service.create_evidence(sample_evidence_data)
        
        # Act
        deleted = await evidence_service.delete_evidence(evidence.id)
        
        # Assert
        assert deleted is True
        
        # Verify deletion
        retrieved = await evidence_service.get_evidence(evidence.id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_should_return_false_when_deleting_non_existent_evidence(
        self,
        evidence_service: EvidenceService
    ):
        """Test deletion of non-existent evidence."""
        # Act
        result = await evidence_service.delete_evidence("non_existent_id")
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_should_search_evidence_by_text_query(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence search functionality."""
        # Arrange
        await evidence_service.create_evidence(sample_evidence_data)
        
        second_evidence = sample_evidence_data.copy()
        second_evidence["id"] = "ev_002"
        second_evidence["title"] = "Observational Cohort Study"
        second_evidence["description"] = "Long-term follow-up study"
        await evidence_service.create_evidence(second_evidence)
        
        # Act - Search by title keyword
        results1 = await evidence_service.search_evidence("randomized")
        
        # Act - Search by description keyword
        results2 = await evidence_service.search_evidence("observational")
        
        # Assert
        assert len(results1) == 1
        assert "randomized" in results1[0].title.lower()
        
        assert len(results2) == 1
        assert "observational" in results2[0].title.lower()
    
    @pytest.mark.asyncio
    async def test_should_assess_evidence_quality(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence quality assessment."""
        # Arrange
        evidence = await evidence_service.create_evidence(sample_evidence_data)
        
        # Act
        assessment = await evidence_service.assess_quality(evidence.id)
        
        # Assert
        assert assessment["evidence_id"] == evidence.id
        assert "overall_score" in assessment
        assert "criteria" in assessment
        assert "recommendations" in assessment
        assert assessment["overall_score"] > 0
        
        # Check criteria structure
        criteria = assessment["criteria"]
        assert "study_design" in criteria
        assert "sample_size" in criteria
        assert "risk_of_bias" in criteria
        assert "publication_status" in criteria
        
        # Each criterion should have score and weight
        for criterion in criteria.values():
            assert "score" in criterion
            assert "weight" in criterion
    
    @pytest.mark.asyncio
    async def test_should_raise_error_when_assessing_non_existent_evidence(
        self,
        evidence_service: EvidenceService
    ):
        """Test quality assessment for non-existent evidence."""
        # Act & Assert
        with pytest.raises(ValueError, match="Evidence not found"):
            await evidence_service.assess_quality("non_existent_id")
    
    @pytest.mark.asyncio
    async def test_should_get_statistics(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence statistics."""
        # Arrange
        await evidence_service.create_evidence(sample_evidence_data)
        
        second_evidence = sample_evidence_data.copy()
        second_evidence["id"] = "ev_002"
        second_evidence["evidence_type"] = EvidenceType.REAL_WORLD_EVIDENCE
        second_evidence["study_design"] = StudyDesign.COHORT
        await evidence_service.create_evidence(second_evidence)
        
        # Act
        stats = await evidence_service.get_statistics()
        
        # Assert
        assert stats["total_evidence"] == 2
        assert "by_type" in stats
        assert "by_design" in stats
        assert "average_quality_score" in stats
        assert "quality_distribution" in stats
        
        # Check type distribution
        assert stats["by_type"]["clinical_trial"] == 1
        assert stats["by_type"]["real_world_evidence"] == 1
        
        # Check design distribution
        assert stats["by_design"]["rct"] == 1
        assert stats["by_design"]["cohort"] == 1
    
    @pytest.mark.asyncio
    async def test_should_apply_pagination_correctly(
        self,
        evidence_service: EvidenceService,
        sample_evidence_data: Dict[str, Any]
    ):
        """Test evidence listing pagination."""
        # Arrange - Create multiple evidence entries
        for i in range(5):
            evidence_data = sample_evidence_data.copy()
            evidence_data["id"] = f"ev_{i:03d}"
            evidence_data["title"] = f"Study {i}"
            await evidence_service.create_evidence(evidence_data)
        
        # Act - Test pagination
        page1 = await evidence_service.list_evidence(limit=2, offset=0)
        page2 = await evidence_service.list_evidence(limit=2, offset=2)
        page3 = await evidence_service.list_evidence(limit=2, offset=4)
        
        # Assert
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1  # Only 5 total, so last page has 1
        
        # Verify no overlap
        page1_ids = {e.id for e in page1}
        page2_ids = {e.id for e in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
