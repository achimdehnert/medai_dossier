"""Tests for economics service."""

import pytest
from datetime import datetime
from typing import Dict, Any

from src.services.economics_service import EconomicsService
from src.models.economics import (
    ModelType,
    AnalysisType,
    CurrencyType,
    TimeHorizon
)


@pytest.fixture
def economics_service():
    """Create economics service instance."""
    return EconomicsService()


@pytest.fixture
def sample_model_data():
    """Create sample economic model data."""
    return {
        "id": "model_001",
        "name": "Cost-Effectiveness Model",
        "description": "Markov model for chronic disease treatment",
        "model_type": ModelType.MARKOV,
        "analysis_type": AnalysisType.COST_EFFECTIVENESS,
        "currency": CurrencyType.EUR,
        "time_horizon": TimeHorizon.LIFETIME,
        "cycle_length": 1.0,
        "discount_rate": 0.035,
        "model_structure": {
            "states": ["Healthy", "Diseased", "Dead"],
            "transitions": {
                "Healthy -> Diseased": 0.05,
                "Diseased -> Dead": 0.10
            }
        }
    }


@pytest.fixture
def sample_parameters_data():
    """Create sample model parameters data."""
    return {
        "treatment_cost": {
            "value": 10000.0,
            "distribution": "normal",
            "std_dev": 1000.0,
            "source": "Clinical trial costing study"
        },
        "treatment_effectiveness": {
            "value": 0.8,
            "distribution": "beta",
            "alpha": 80,
            "beta": 20,
            "source": "Meta-analysis of RCTs"
        },
        "utility_healthy": {
            "value": 0.9,
            "distribution": "uniform",
            "min": 0.85,
            "max": 0.95,
            "source": "Health state utility study"
        }
    }


class TestEconomicsService:
    """Test economics service functionality."""
    
    @pytest.mark.asyncio
    async def test_should_create_model_when_valid_data_provided(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test economic model creation with valid data."""
        # Act
        model = await economics_service.create_model(sample_model_data)
        
        # Assert
        assert model.id == sample_model_data["id"]
        assert model.name == sample_model_data["name"]
        assert model.model_type == ModelType.MARKOV
        assert model.analysis_type == AnalysisType.COST_EFFECTIVENESS
        assert model.currency == CurrencyType.EUR
        assert model.time_horizon == TimeHorizon.LIFETIME
        assert model.cycle_length == 1.0
        assert model.discount_rate == 0.035
    
    @pytest.mark.asyncio
    async def test_should_raise_error_when_invalid_model_data_provided(
        self,
        economics_service: EconomicsService
    ):
        """Test model creation with invalid data."""
        # Arrange
        invalid_data = {
            "name": "",  # Empty name should be invalid
            "model_type": "invalid_type",
            "discount_rate": -0.1  # Negative discount rate invalid
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid model data"):
            await economics_service.create_model(invalid_data)
    
    @pytest.mark.asyncio
    async def test_should_retrieve_model_when_exists(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test model retrieval."""
        # Arrange
        created_model = await economics_service.create_model(sample_model_data)
        
        # Act
        retrieved_model = await economics_service.get_model(created_model.id)
        
        # Assert
        assert retrieved_model is not None
        assert retrieved_model.id == created_model.id
        assert retrieved_model.name == created_model.name
    
    @pytest.mark.asyncio
    async def test_should_return_none_when_model_not_exists(
        self,
        economics_service: EconomicsService
    ):
        """Test model retrieval for non-existent ID."""
        # Act
        model = await economics_service.get_model("non_existent_id")
        
        # Assert
        assert model is None
    
    @pytest.mark.asyncio
    async def test_should_list_models_with_filters(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test model listing with filters."""
        # Arrange
        await economics_service.create_model(sample_model_data)
        
        # Create second model with different type
        second_model = sample_model_data.copy()
        second_model["id"] = "model_002"
        second_model["model_type"] = ModelType.DECISION_TREE
        second_model["analysis_type"] = AnalysisType.BUDGET_IMPACT
        await economics_service.create_model(second_model)
        
        # Act - Filter by Markov type
        markov_models = await economics_service.list_models(
            model_type=ModelType.MARKOV
        )
        
        # Act - Filter by budget impact analysis
        bia_models = await economics_service.list_models(
            analysis_type=AnalysisType.BUDGET_IMPACT
        )
        
        # Assert
        assert len(markov_models) == 1
        assert markov_models[0].model_type == ModelType.MARKOV
        
        assert len(bia_models) == 1
        assert bia_models[0].analysis_type == AnalysisType.BUDGET_IMPACT
    
    @pytest.mark.asyncio
    async def test_should_update_model_when_valid_data_provided(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test model update."""
        # Arrange
        model = await economics_service.create_model(sample_model_data)
        
        updates = {
            "name": "Updated Cost-Effectiveness Model",
            "discount_rate": 0.04
        }
        
        # Act
        updated_model = await economics_service.update_model(
            model.id, updates
        )
        
        # Assert
        assert updated_model is not None
        assert updated_model.name == "Updated Cost-Effectiveness Model"
        assert updated_model.discount_rate == 0.04
        assert updated_model.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_should_delete_model_when_exists(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test model deletion."""
        # Arrange
        model = await economics_service.create_model(sample_model_data)
        
        # Act
        deleted = await economics_service.delete_model(model.id)
        
        # Assert
        assert deleted is True
        
        # Verify deletion
        retrieved = await economics_service.get_model(model.id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_should_set_model_parameters(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any],
        sample_parameters_data: Dict[str, Any]
    ):
        """Test setting model parameters."""
        # Arrange
        model = await economics_service.create_model(sample_model_data)
        
        # Act
        await economics_service.set_parameters(model.id, sample_parameters_data)
        
        # Retrieve parameters
        parameters = await economics_service.get_parameters(model.id)
        
        # Assert
        assert parameters is not None
        assert "treatment_cost" in parameters
        assert "treatment_effectiveness" in parameters
        assert "utility_healthy" in parameters
        
        # Check parameter structure
        treatment_cost = parameters["treatment_cost"]
        assert treatment_cost["value"] == 10000.0
        assert treatment_cost["distribution"] == "normal"
        assert treatment_cost["std_dev"] == 1000.0
    
    @pytest.mark.asyncio
    async def test_should_run_base_case_analysis(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any],
        sample_parameters_data: Dict[str, Any]
    ):
        """Test base case analysis."""
        # Arrange
        model = await economics_service.create_model(sample_model_data)
        await economics_service.set_parameters(model.id, sample_parameters_data)
        
        # Act
        results = await economics_service.run_base_case(model.id)
        
        # Assert
        assert results["model_id"] == model.id
        assert "total_costs" in results
        assert "total_effects" in results
        assert "icer" in results
        assert "net_benefit" in results
        
        # Check result values are reasonable
        assert results["total_costs"] > 0
        assert results["total_effects"] > 0
        assert isinstance(results["icer"], (int, float))
    
    @pytest.mark.asyncio
    async def test_should_run_sensitivity_analysis(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any],
        sample_parameters_data: Dict[str, Any]
    ):
        """Test sensitivity analysis."""
        # Arrange
        model = await economics_service.create_model(sample_model_data)
        await economics_service.set_parameters(model.id, sample_parameters_data)
        
        sensitivity_config = {
            "parameters": ["treatment_cost", "treatment_effectiveness"],
            "ranges": {
                "treatment_cost": {"min": 8000, "max": 12000},
                "treatment_effectiveness": {"min": 0.7, "max": 0.9}
            },
            "analysis_type": "tornado"
        }
        
        # Act
        results = await economics_service.run_sensitivity_analysis(
            model.id, sensitivity_config
        )
        
        # Assert
        assert results["model_id"] == model.id
        assert results["analysis_type"] == "tornado"
        assert "parameter_impacts" in results
        assert "tornado_data" in results
        
        # Check parameter impacts
        impacts = results["parameter_impacts"]
        assert "treatment_cost" in impacts
        assert "treatment_effectiveness" in impacts
        
        for param, impact in impacts.items():
            assert "low_value" in impact
            assert "high_value" in impact
            assert "low_result" in impact
            assert "high_result" in impact
    
    @pytest.mark.asyncio
    async def test_should_calculate_budget_impact(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test budget impact calculation."""
        # Arrange
        model_data = sample_model_data.copy()
        model_data["analysis_type"] = AnalysisType.BUDGET_IMPACT
        model = await economics_service.create_model(model_data)
        
        bia_config = {
            "population_size": 10000,
            "treatment_uptake": [0.1, 0.2, 0.3, 0.4, 0.5],  # 5-year uptake
            "comparator_cost": 5000,
            "new_treatment_cost": 15000,
            "time_horizon": 5
        }
        
        # Act
        results = await economics_service.calculate_budget_impact(
            model.id, bia_config
        )
        
        # Assert
        assert results["model_id"] == model.id
        assert "annual_costs" in results
        assert "cumulative_impact" in results
        assert "total_impact" in results
        
        # Check annual costs structure
        annual_costs = results["annual_costs"]
        assert len(annual_costs) == 5  # 5-year horizon
        
        for year_cost in annual_costs:
            assert "year" in year_cost
            assert "population" in year_cost
            assert "new_treatment_cost" in year_cost
            assert "comparator_cost" in year_cost
            assert "net_impact" in year_cost
    
    @pytest.mark.asyncio
    async def test_should_raise_error_when_running_analysis_on_non_existent_model(
        self,
        economics_service: EconomicsService
    ):
        """Test analysis on non-existent model."""
        # Act & Assert
        with pytest.raises(ValueError, match="Model not found"):
            await economics_service.run_base_case("non_existent_id")
    
    @pytest.mark.asyncio
    async def test_should_get_statistics(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test economics statistics."""
        # Arrange
        await economics_service.create_model(sample_model_data)
        
        second_model = sample_model_data.copy()
        second_model["id"] = "model_002"
        second_model["model_type"] = ModelType.DECISION_TREE
        second_model["analysis_type"] = AnalysisType.BUDGET_IMPACT
        await economics_service.create_model(second_model)
        
        # Act
        stats = await economics_service.get_statistics()
        
        # Assert
        assert stats["total_models"] == 2
        assert "by_type" in stats
        assert "by_analysis" in stats
        assert "by_currency" in stats
        assert "average_discount_rate" in stats
        
        # Check type distribution
        assert stats["by_type"]["markov"] == 1
        assert stats["by_type"]["decision_tree"] == 1
        
        # Check analysis distribution
        assert stats["by_analysis"]["cost_effectiveness"] == 1
        assert stats["by_analysis"]["budget_impact"] == 1
    
    @pytest.mark.asyncio
    async def test_should_validate_parameters_structure(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test parameter validation."""
        # Arrange
        model = await economics_service.create_model(sample_model_data)
        
        invalid_parameters = {
            "invalid_param": {
                "value": "not_a_number",  # Should be numeric
                "distribution": "invalid_dist"  # Invalid distribution
            }
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid parameter"):
            await economics_service.set_parameters(model.id, invalid_parameters)
    
    @pytest.mark.asyncio
    async def test_should_apply_pagination_to_model_listing(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test model listing pagination."""
        # Arrange - Create multiple models
        for i in range(5):
            model_data = sample_model_data.copy()
            model_data["id"] = f"model_{i:03d}"
            model_data["name"] = f"Model {i}"
            await economics_service.create_model(model_data)
        
        # Act - Test pagination
        page1 = await economics_service.list_models(limit=2, offset=0)
        page2 = await economics_service.list_models(limit=2, offset=2)
        page3 = await economics_service.list_models(limit=2, offset=4)
        
        # Assert
        assert len(page1) == 2
        assert len(page2) == 2
        assert len(page3) == 1  # Only 5 total, so last page has 1
        
        # Verify no overlap
        page1_ids = {m.id for m in page1}
        page2_ids = {m.id for m in page2}
        assert len(page1_ids.intersection(page2_ids)) == 0
    
    @pytest.mark.asyncio
    async def test_should_handle_concurrent_model_operations(
        self,
        economics_service: EconomicsService,
        sample_model_data: Dict[str, Any]
    ):
        """Test concurrent model operations."""
        import asyncio
        
        # Arrange
        model_data_list = []
        for i in range(3):
            data = sample_model_data.copy()
            data["id"] = f"concurrent_model_{i}"
            data["name"] = f"Concurrent Model {i}"
            model_data_list.append(data)
        
        # Act - Create models concurrently
        tasks = [
            economics_service.create_model(data)
            for data in model_data_list
        ]
        
        created_models = await asyncio.gather(*tasks)
        
        # Assert
        assert len(created_models) == 3
        for i, model in enumerate(created_models):
            assert model.id == f"concurrent_model_{i}"
            assert f"Concurrent Model {i}" in model.name
