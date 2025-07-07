"""Tests for HTA service."""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.services.hta_service import HTAService
from src.models.hta import (
    HTAFramework,
    SubmissionType,
    ReviewStage,
    ComplianceStatus,
    RequirementType
)


@pytest.fixture
def hta_service():
    """Create HTA service instance."""
    return HTAService()


@pytest.fixture
def sample_framework_data():
    """Create sample HTA framework data."""
    return {
        "id": "framework_001",
        "name": "Custom HTA Framework",
        "agency": "Test Agency",
        "country": "Test Country",
        "description": "Custom framework for testing",
        "requirements": [
            {
                "id": "req_001",
                "type": RequirementType.CLINICAL_EVIDENCE,
                "title": "Clinical Trial Data",
                "description": "Phase III RCT results required",
                "mandatory": True,
                "document_types": ["clinical_study_report", "statistical_analysis"]
            },
            {
                "id": "req_002", 
                "type": RequirementType.ECONOMIC_EVIDENCE,
                "title": "Cost-Effectiveness Analysis",
                "description": "Economic evaluation required",
                "mandatory": True,
                "document_types": ["economic_model", "budget_impact"]
            }
        ],
        "timeline": {
            "submission_deadline": 90,
            "review_duration": 180,
            "appeal_period": 30
        }
    }


@pytest.fixture
def sample_submission_data():
    """Create sample submission data."""
    return {
        "id": "sub_001",
        "dossier_id": "dossier_001",
        "framework_id": "nice",
        "submission_type": SubmissionType.FULL_SUBMISSION,
        "submission_date": "2024-01-15",
        "target_decision_date": "2024-07-15",
        "submitted_documents": [
            {
                "requirement_id": "nice_req_001",
                "document_type": "clinical_study_report",
                "title": "Phase III Clinical Study Report",
                "version": "1.0",
                "submission_date": "2024-01-15"
            }
        ],
        "review_stage": ReviewStage.VALIDATION,
        "compliance_status": ComplianceStatus.COMPLIANT
    }


class TestHTAService:
    """Test HTA service functionality."""
    
    @pytest.mark.asyncio
    async def test_should_initialize_default_frameworks_on_startup(
        self,
        hta_service: HTAService
    ):
        """Test that default HTA frameworks are initialized."""
        # Act
        await hta_service._initialize_default_frameworks()
        
        # Get all frameworks
        frameworks = await hta_service.list_frameworks()
        
        # Assert
        framework_ids = {f.id for f in frameworks}
        expected_frameworks = {"nice", "g_ba", "has", "cadth"}
        
        assert expected_frameworks.issubset(framework_ids)
        
        # Check NICE framework specifically
        nice = await hta_service.get_framework("nice")
        assert nice is not None
        assert nice.name == "NICE"
        assert nice.agency == "National Institute for Health and Care Excellence"
        assert nice.country == "United Kingdom"
        assert len(nice.requirements) > 0
        assert nice.timeline["review_duration"] == 300  # 10 months
    
    @pytest.mark.asyncio
    async def test_should_create_framework_when_valid_data_provided(
        self,
        hta_service: HTAService,
        sample_framework_data: Dict[str, Any]
    ):
        """Test HTA framework creation with valid data."""
        # Act
        framework = await hta_service.create_framework(sample_framework_data)
        
        # Assert
        assert framework.id == sample_framework_data["id"]
        assert framework.name == sample_framework_data["name"]
        assert framework.agency == sample_framework_data["agency"]
        assert framework.country == sample_framework_data["country"]
        assert len(framework.requirements) == 2
        
        # Check requirements
        req1 = framework.requirements[0]
        assert req1.type == RequirementType.CLINICAL_EVIDENCE
        assert req1.mandatory is True
        assert "clinical_study_report" in req1.document_types
    
    @pytest.mark.asyncio
    async def test_should_raise_error_when_invalid_framework_data_provided(
        self,
        hta_service: HTAService
    ):
        """Test framework creation with invalid data."""
        # Arrange
        invalid_data = {
            "name": "",  # Empty name should be invalid
            "agency": "",  # Empty agency should be invalid
            "requirements": []  # No requirements should be invalid
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid framework data"):
            await hta_service.create_framework(invalid_data)
    
    @pytest.mark.asyncio
    async def test_should_retrieve_framework_when_exists(
        self,
        hta_service: HTAService,
        sample_framework_data: Dict[str, Any]
    ):
        """Test framework retrieval."""
        # Arrange
        created_framework = await hta_service.create_framework(sample_framework_data)
        
        # Act
        retrieved_framework = await hta_service.get_framework(created_framework.id)
        
        # Assert
        assert retrieved_framework is not None
        assert retrieved_framework.id == created_framework.id
        assert retrieved_framework.name == created_framework.name
    
    @pytest.mark.asyncio
    async def test_should_return_none_when_framework_not_exists(
        self,
        hta_service: HTAService
    ):
        """Test framework retrieval for non-existent ID."""
        # Act
        framework = await hta_service.get_framework("non_existent_id")
        
        # Assert
        assert framework is None
    
    @pytest.mark.asyncio
    async def test_should_list_frameworks_with_filters(
        self,
        hta_service: HTAService,
        sample_framework_data: Dict[str, Any]
    ):
        """Test framework listing with filters."""
        # Arrange
        await hta_service.create_framework(sample_framework_data)
        
        # Create second framework with different country
        second_framework = sample_framework_data.copy()
        second_framework["id"] = "framework_002"
        second_framework["name"] = "Another Framework"
        second_framework["country"] = "Another Country"
        await hta_service.create_framework(second_framework)
        
        # Act - Filter by country
        test_country_frameworks = await hta_service.list_frameworks(
            country="Test Country"
        )
        
        another_country_frameworks = await hta_service.list_frameworks(
            country="Another Country"
        )
        
        # Assert
        assert len(test_country_frameworks) == 1
        assert test_country_frameworks[0].country == "Test Country"
        
        assert len(another_country_frameworks) == 1
        assert another_country_frameworks[0].country == "Another Country"
    
    @pytest.mark.asyncio
    async def test_should_update_framework_when_valid_data_provided(
        self,
        hta_service: HTAService,
        sample_framework_data: Dict[str, Any]
    ):
        """Test framework update."""
        # Arrange
        framework = await hta_service.create_framework(sample_framework_data)
        
        updates = {
            "name": "Updated Framework Name",
            "description": "Updated description"
        }
        
        # Act
        updated_framework = await hta_service.update_framework(
            framework.id, updates
        )
        
        # Assert
        assert updated_framework is not None
        assert updated_framework.name == "Updated Framework Name"
        assert updated_framework.description == "Updated description"
        assert updated_framework.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_should_delete_framework_when_exists(
        self,
        hta_service: HTAService,
        sample_framework_data: Dict[str, Any]
    ):
        """Test framework deletion."""
        # Arrange
        framework = await hta_service.create_framework(sample_framework_data)
        
        # Act
        deleted = await hta_service.delete_framework(framework.id)
        
        # Assert
        assert deleted is True
        
        # Verify deletion
        retrieved = await hta_service.get_framework(framework.id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_should_get_framework_requirements(
        self,
        hta_service: HTAService,
        sample_framework_data: Dict[str, Any]
    ):
        """Test getting framework requirements."""
        # Arrange
        framework = await hta_service.create_framework(sample_framework_data)
        
        # Act
        requirements = await hta_service.get_framework_requirements(framework.id)
        
        # Assert
        assert len(requirements) == 2
        
        # Check clinical evidence requirement
        clinical_req = next(
            (r for r in requirements if r.type == RequirementType.CLINICAL_EVIDENCE),
            None
        )
        assert clinical_req is not None
        assert clinical_req.mandatory is True
        assert "clinical_study_report" in clinical_req.document_types
        
        # Check economic evidence requirement
        economic_req = next(
            (r for r in requirements if r.type == RequirementType.ECONOMIC_EVIDENCE),
            None
        )
        assert economic_req is not None
        assert economic_req.mandatory is True
        assert "economic_model" in economic_req.document_types
    
    @pytest.mark.asyncio
    async def test_should_create_submission_when_valid_data_provided(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test submission creation with valid data."""
        # Arrange - Initialize frameworks first to have "nice" available
        await hta_service._initialize_default_frameworks()
        
        # Act
        submission = await hta_service.create_submission(sample_submission_data)
        
        # Assert
        assert submission.id == sample_submission_data["id"]
        assert submission.dossier_id == sample_submission_data["dossier_id"]
        assert submission.framework_id == sample_submission_data["framework_id"]
        assert submission.submission_type == SubmissionType.FULL_SUBMISSION
        assert submission.review_stage == ReviewStage.VALIDATION
        assert submission.compliance_status == ComplianceStatus.COMPLIANT
        assert len(submission.submitted_documents) == 1
    
    @pytest.mark.asyncio
    async def test_should_raise_error_when_invalid_submission_data_provided(
        self,
        hta_service: HTAService
    ):
        """Test submission creation with invalid data."""
        # Arrange
        invalid_data = {
            "dossier_id": "",  # Empty dossier ID should be invalid
            "framework_id": "non_existent_framework",  # Non-existent framework
            "submission_date": "invalid_date"  # Invalid date format
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid submission data"):
            await hta_service.create_submission(invalid_data)
    
    @pytest.mark.asyncio
    async def test_should_check_submission_compliance(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test submission compliance checking."""
        # Arrange
        await hta_service._initialize_default_frameworks()
        submission = await hta_service.create_submission(sample_submission_data)
        
        # Act
        compliance = await hta_service.check_compliance(submission.id)
        
        # Assert
        assert compliance["submission_id"] == submission.id
        assert "overall_status" in compliance
        assert "missing_requirements" in compliance
        assert "compliance_score" in compliance
        assert "recommendations" in compliance
        
        # Check compliance structure
        assert isinstance(compliance["compliance_score"], (int, float))
        assert 0 <= compliance["compliance_score"] <= 100
        assert isinstance(compliance["missing_requirements"], list)
        assert isinstance(compliance["recommendations"], list)
    
    @pytest.mark.asyncio
    async def test_should_get_submission_timeline(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test getting submission timeline."""
        # Arrange
        await hta_service._initialize_default_frameworks()
        submission = await hta_service.create_submission(sample_submission_data)
        
        # Act
        timeline = await hta_service.get_submission_timeline(submission.id)
        
        # Assert
        assert timeline["submission_id"] == submission.id
        assert "milestones" in timeline
        assert "critical_path" in timeline
        assert "estimated_completion" in timeline
        
        # Check milestones structure
        milestones = timeline["milestones"]
        assert isinstance(milestones, list)
        
        for milestone in milestones:
            assert "stage" in milestone
            assert "target_date" in milestone
            assert "status" in milestone
            assert milestone["stage"] in [
                "validation", "scientific_review", "committee_review", 
                "appeal_period", "final_decision"
            ]
    
    @pytest.mark.asyncio
    async def test_should_update_submission_status(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test updating submission status."""
        # Arrange
        await hta_service._initialize_default_frameworks()
        submission = await hta_service.create_submission(sample_submission_data)
        
        # Act
        updated_submission = await hta_service.update_submission_status(
            submission.id,
            ReviewStage.SCIENTIFIC_REVIEW,
            ComplianceStatus.MINOR_ISSUES
        )
        
        # Assert
        assert updated_submission is not None
        assert updated_submission.review_stage == ReviewStage.SCIENTIFIC_REVIEW
        assert updated_submission.compliance_status == ComplianceStatus.MINOR_ISSUES
        assert updated_submission.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_should_list_submissions_with_filters(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test submission listing with filters."""
        # Arrange
        await hta_service._initialize_default_frameworks()
        await hta_service.create_submission(sample_submission_data)
        
        # Create second submission with different framework
        second_submission = sample_submission_data.copy()
        second_submission["id"] = "sub_002"
        second_submission["framework_id"] = "g_ba"
        second_submission["review_stage"] = ReviewStage.SCIENTIFIC_REVIEW
        await hta_service.create_submission(second_submission)
        
        # Act - Filter by framework
        nice_submissions = await hta_service.list_submissions(
            framework_id="nice"
        )
        
        # Act - Filter by review stage
        validation_submissions = await hta_service.list_submissions(
            review_stage=ReviewStage.VALIDATION
        )
        
        # Assert
        assert len(nice_submissions) == 1
        assert nice_submissions[0].framework_id == "nice"
        
        assert len(validation_submissions) == 1
        assert validation_submissions[0].review_stage == ReviewStage.VALIDATION
    
    @pytest.mark.asyncio
    async def test_should_get_statistics(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test HTA statistics."""
        # Arrange
        await hta_service._initialize_default_frameworks()
        await hta_service.create_submission(sample_submission_data)
        
        second_submission = sample_submission_data.copy()
        second_submission["id"] = "sub_002"
        second_submission["framework_id"] = "g_ba"
        second_submission["review_stage"] = ReviewStage.SCIENTIFIC_REVIEW
        await hta_service.create_submission(second_submission)
        
        # Act
        stats = await hta_service.get_statistics()
        
        # Assert
        assert stats["total_frameworks"] >= 4  # At least the 4 default frameworks
        assert stats["total_submissions"] == 2
        assert "submissions_by_framework" in stats
        assert "submissions_by_stage" in stats
        assert "compliance_distribution" in stats
        assert "average_review_time" in stats
        
        # Check framework distribution
        framework_dist = stats["submissions_by_framework"]
        assert "nice" in framework_dist
        assert "g_ba" in framework_dist
        assert framework_dist["nice"] == 1
        assert framework_dist["g_ba"] == 1
        
        # Check stage distribution
        stage_dist = stats["submissions_by_stage"]
        assert "validation" in stage_dist
        assert "scientific_review" in stage_dist
        assert stage_dist["validation"] == 1
        assert stage_dist["scientific_review"] == 1
    
    @pytest.mark.asyncio
    async def test_should_validate_submission_documents(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test submission document validation."""
        # Arrange
        await hta_service._initialize_default_frameworks()
        submission = await hta_service.create_submission(sample_submission_data)
        
        # Act
        validation_result = await hta_service._validate_submission_documents(
            submission.framework_id,
            submission.submitted_documents
        )
        
        # Assert
        assert "valid" in validation_result
        assert "missing_documents" in validation_result
        assert "excess_documents" in validation_result
        assert isinstance(validation_result["valid"], bool)
        assert isinstance(validation_result["missing_documents"], list)
        assert isinstance(validation_result["excess_documents"], list)
    
    @pytest.mark.asyncio
    async def test_should_calculate_compliance_score(
        self,
        hta_service: HTAService
    ):
        """Test compliance score calculation."""
        # Arrange
        requirements = [
            {"mandatory": True, "fulfilled": True},
            {"mandatory": True, "fulfilled": False},
            {"mandatory": False, "fulfilled": True},
            {"mandatory": False, "fulfilled": False}
        ]
        
        # Act
        score = await hta_service._calculate_compliance_score(requirements)
        
        # Assert
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
        # With 2 mandatory requirements and 1 fulfilled, score should be 50
        assert score == 50.0
    
    @pytest.mark.asyncio
    async def test_should_apply_pagination_to_listings(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test pagination in listings."""
        # Arrange
        await hta_service._initialize_default_frameworks()
        
        # Create multiple submissions
        for i in range(5):
            submission_data = sample_submission_data.copy()
            submission_data["id"] = f"sub_{i:03d}"
            await hta_service.create_submission(submission_data)
        
        # Act - Test pagination
        page1 = await hta_service.list_submissions(limit=2, offset=0)
        page2 = await hta_service.list_submissions(limit=2, offset=2)
        page3 = await hta_service.list_submissions(limit=2, offset=4)
        
        # Assert
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1  # Only 5 total, so last page has 1
        
        # Verify no overlap
        page1_ids = {s.id for s in page1}
        page2_ids = {s.id for s in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
    
    @pytest.mark.asyncio
    async def test_should_handle_missing_framework_in_submission_creation(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test submission creation with non-existent framework."""
        # Arrange
        submission_data = sample_submission_data.copy()
        submission_data["framework_id"] = "non_existent_framework"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Framework not found"):
            await hta_service.create_submission(submission_data)
    
    @pytest.mark.asyncio
    async def test_should_generate_submission_recommendations(
        self,
        hta_service: HTAService,
        sample_submission_data: Dict[str, Any]
    ):
        """Test submission recommendation generation."""
        # Arrange
        await hta_service._initialize_default_frameworks()
        submission = await hta_service.create_submission(sample_submission_data)
        
        # Act
        recommendations = await hta_service._generate_recommendations(
            submission.framework_id,
            ["missing_clinical_data", "incomplete_economic_model"]
        )
        
        # Assert
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0
