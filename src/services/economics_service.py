"""Economics service for managing health economic data and models."""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import logging
import asyncio
from decimal import Decimal

from ..models.economics import (
    EconomicModel,
    ModelType,
    Currency,
    CostCategory,
    AnalysisTimeframe,
    ModelParameter,
    SensitivityAnalysis
)


logger = logging.getLogger(__name__)


class EconomicsService:
    """Service for managing health economic models and analyses."""
    
    def __init__(self):
        """Initialize economics service."""
        self._model_store: Dict[str, EconomicModel] = {}
        self._parameter_store: Dict[str, List[ModelParameter]] = {}
        self._analysis_store: Dict[str, SensitivityAnalysis] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def create_model(
        self,
        model_data: Dict[str, Any]
    ) -> EconomicModel:
        """Create new economic model.
        
        Args:
            model_data: Model data dictionary
            
        Returns:
            Created model instance
            
        Raises:
            ValueError: If model data is invalid
        """
        try:
            # Create model instance
            model = EconomicModel(**model_data)
            
            # Store model
            self._model_store[model.id] = model
            
            # Initialize parameter store
            self._parameter_store[model.id] = []
            
            self.logger.info(f"Created economic model: {model.id}")
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to create model: {e}")
            raise ValueError(f"Invalid model data: {e}")
    
    async def get_model(
        self,
        model_id: str
    ) -> Optional[EconomicModel]:
        """Get economic model by ID.
        
        Args:
            model_id: Model ID
            
        Returns:
            Model instance or None
        """
        return self._model_store.get(model_id)
    
    async def list_models(
        self,
        model_type: Optional[ModelType] = None,
        currency: Optional[Currency] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[EconomicModel]:
        """List economic models with filters.
        
        Args:
            model_type: Filter by model type
            currency: Filter by currency
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of model instances
        """
        models = list(self._model_store.values())
        
        # Apply filters
        if model_type:
            models = [m for m in models if m.model_type == model_type]
        
        if currency:
            models = [m for m in models if m.currency == currency]
        
        # Sort by creation date (newest first)
        models.sort(
            key=lambda x: x.created_at or datetime.min,
            reverse=True
        )
        
        # Apply pagination
        return models[offset:offset + limit]
    
    async def update_model(
        self,
        model_id: str,
        updates: Dict[str, Any]
    ) -> Optional[EconomicModel]:
        """Update economic model.
        
        Args:
            model_id: Model ID
            updates: Update data
            
        Returns:
            Updated model or None
        """
        model = self._model_store.get(model_id)
        if not model:
            return None
        
        # Create updated model
        model_data = model.dict()
        model_data.update(updates)
        model_data["updated_at"] = datetime.utcnow()
        
        try:
            updated_model = EconomicModel(**model_data)
            self._model_store[model_id] = updated_model
            
            self.logger.info(f"Updated model: {model_id}")
            return updated_model
            
        except Exception as e:
            self.logger.error(f"Failed to update model {model_id}: {e}")
            raise ValueError(f"Invalid update data: {e}")
    
    async def delete_model(
        self,
        model_id: str
    ) -> bool:
        """Delete economic model.
        
        Args:
            model_id: Model ID
            
        Returns:
            True if deleted, False if not found
        """
        if model_id in self._model_store:
            del self._model_store[model_id]
            # Clean up related data
            if model_id in self._parameter_store:
                del self._parameter_store[model_id]
            
            self.logger.info(f"Deleted model: {model_id}")
            return True
        return False
    
    async def add_parameter(
        self,
        model_id: str,
        parameter_data: Dict[str, Any]
    ) -> ModelParameter:
        """Add parameter to economic model.
        
        Args:
            model_id: Model ID
            parameter_data: Parameter data
            
        Returns:
            Created parameter
            
        Raises:
            ValueError: If model not found or parameter invalid
        """
        if model_id not in self._model_store:
            raise ValueError(f"Model not found: {model_id}")
        
        try:
            parameter = ModelParameter(**parameter_data)
            
            # Add to parameter store
            if model_id not in self._parameter_store:
                self._parameter_store[model_id] = []
            
            self._parameter_store[model_id].append(parameter)
            
            self.logger.info(
                f"Added parameter {parameter.name} to model {model_id}"
            )
            return parameter
            
        except Exception as e:
            self.logger.error(f"Failed to add parameter: {e}")
            raise ValueError(f"Invalid parameter data: {e}")
    
    async def get_parameters(
        self,
        model_id: str
    ) -> List[ModelParameter]:
        """Get parameters for economic model.
        
        Args:
            model_id: Model ID
            
        Returns:
            List of parameters
        """
        return self._parameter_store.get(model_id, [])
    
    async def run_base_case(
        self,
        model_id: str
    ) -> Dict[str, Any]:
        """Run base case analysis for economic model.
        
        Args:
            model_id: Model ID
            
        Returns:
            Base case results
            
        Raises:
            ValueError: If model not found
        """
        model = await self.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        parameters = await self.get_parameters(model_id)
        
        # Simple base case calculation (demonstration)
        total_costs = Decimal("0")
        total_qalys = Decimal("0")
        
        # Calculate costs and outcomes based on model type
        if model.model_type == ModelType.CEA:
            # Cost-effectiveness analysis
            for param in parameters:
                if param.category == CostCategory.DIRECT_MEDICAL:
                    total_costs += Decimal(str(param.base_value))
                elif param.name.lower().startswith("qaly"):
                    total_qalys += Decimal(str(param.base_value))
        
        elif model.model_type == ModelType.CUA:
            # Cost-utility analysis
            for param in parameters:
                if param.category in [CostCategory.DIRECT_MEDICAL, CostCategory.DIRECT_NON_MEDICAL]:
                    total_costs += Decimal(str(param.base_value))
                elif param.name.lower().startswith("utility"):
                    total_qalys += Decimal(str(param.base_value)) * Decimal(str(model.time_horizon or 1))
        
        elif model.model_type == ModelType.BIA:
            # Budget impact analysis
            for param in parameters:
                if "cost" in param.name.lower():
                    total_costs += Decimal(str(param.base_value))
        
        # Calculate ICER if applicable
        icer = None
        if total_qalys > 0 and model.model_type in [ModelType.CEA, ModelType.CUA]:
            icer = float(total_costs / total_qalys)
        
        results = {
            "model_id": model_id,
            "model_type": model.model_type.value,
            "total_costs": float(total_costs),
            "total_qalys": float(total_qalys) if total_qalys > 0 else None,
            "icer": icer,
            "currency": model.currency.value,
            "time_horizon": model.time_horizon,
            "analysis_date": datetime.utcnow().isoformat(),
            "parameters_used": len(parameters)
        }
        
        self.logger.info(f"Completed base case analysis for model {model_id}")
        return results
    
    async def run_sensitivity_analysis(
        self,
        model_id: str,
        analysis_config: Dict[str, Any]
    ) -> SensitivityAnalysis:
        """Run sensitivity analysis.
        
        Args:
            model_id: Model ID
            analysis_config: Analysis configuration
            
        Returns:
            Sensitivity analysis results
            
        Raises:
            ValueError: If model not found
        """
        model = await self.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        parameters = await self.get_parameters(model_id)
        base_case = await self.run_base_case(model_id)
        
        # Create sensitivity analysis
        analysis_data = {
            "id": f"sa_{model_id}_{int(datetime.utcnow().timestamp())}",
            "model_id": model_id,
            "analysis_type": analysis_config.get("type", "one_way"),
            "parameters_varied": analysis_config.get("parameters", []),
            "base_case_results": base_case,
            "scenarios": [],
            "created_at": datetime.utcnow()
        }
        
        # Run scenarios
        analysis_type = analysis_config.get("type", "one_way")
        
        if analysis_type == "one_way":
            # One-way sensitivity analysis
            for param_name in analysis_config.get("parameters", []):
                param = next((p for p in parameters if p.name == param_name), None)
                if not param:
                    continue
                
                # Test low and high values
                for variation in ["low", "high"]:
                    if variation == "low" and param.min_value is not None:
                        test_value = param.min_value
                    elif variation == "high" and param.max_value is not None:
                        test_value = param.max_value
                    else:
                        # Use +/- 20% if bounds not specified
                        factor = 0.8 if variation == "low" else 1.2
                        test_value = param.base_value * factor
                    
                    # Calculate results with varied parameter
                    scenario_result = await self._calculate_scenario(
                        model_id, param_name, test_value, base_case
                    )
                    
                    analysis_data["scenarios"].append({
                        "parameter": param_name,
                        "variation": variation,
                        "value": test_value,
                        "results": scenario_result
                    })
        
        elif analysis_type == "probabilistic":
            # Probabilistic sensitivity analysis (simplified)
            num_iterations = analysis_config.get("iterations", 1000)
            
            for i in range(min(num_iterations, 100)):  # Limit for demo
                # Random parameter variations would go here
                # For now, just create placeholder scenarios
                analysis_data["scenarios"].append({
                    "iteration": i + 1,
                    "results": base_case  # Simplified
                })
        
        # Create analysis object
        analysis = SensitivityAnalysis(**analysis_data)
        self._analysis_store[analysis.id] = analysis
        
        self.logger.info(f"Completed sensitivity analysis: {analysis.id}")
        return analysis
    
    async def _calculate_scenario(
        self,
        model_id: str,
        param_name: str,
        param_value: float,
        base_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate scenario results with parameter variation.
        
        Args:
            model_id: Model ID
            param_name: Parameter name
            param_value: Parameter value
            base_case: Base case results
            
        Returns:
            Scenario results
        """
        # Simplified calculation - in practice would re-run full model
        # with varied parameter
        
        # For demo, apply simple percentage change
        change_factor = param_value / base_case.get("total_costs", 1) if "cost" in param_name.lower() else 1
        
        scenario_costs = base_case["total_costs"] * change_factor
        scenario_qalys = base_case.get("total_qalys", 0)
        
        scenario_icer = None
        if scenario_qalys and scenario_qalys > 0:
            scenario_icer = scenario_costs / scenario_qalys
        
        return {
            "total_costs": scenario_costs,
            "total_qalys": scenario_qalys,
            "icer": scenario_icer,
            "parameter_changed": param_name,
            "parameter_value": param_value
        }
    
    async def get_sensitivity_analysis(
        self,
        analysis_id: str
    ) -> Optional[SensitivityAnalysis]:
        """Get sensitivity analysis by ID.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis instance or None
        """
        return self._analysis_store.get(analysis_id)
    
    async def calculate_budget_impact(
        self,
        model_id: str,
        scenario_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate budget impact.
        
        Args:
            model_id: Model ID
            scenario_config: Scenario configuration
            
        Returns:
            Budget impact results
        """
        model = await self.get_model(model_id)
        if not model:
            raise ValueError(f"Model not found: {model_id}")
        
        if model.model_type != ModelType.BIA:
            self.logger.warning(
                f"Model {model_id} is not a budget impact model"
            )
        
        # Get parameters
        parameters = await self.get_parameters(model_id)
        
        # Extract scenario configuration
        target_population = scenario_config.get("target_population", 10000)
        market_uptake = scenario_config.get("market_uptake", [0.1, 0.2, 0.3, 0.4, 0.5])
        time_horizon = scenario_config.get("time_horizon", 5)
        
        # Calculate budget impact by year
        annual_results = []
        
        for year in range(1, time_horizon + 1):
            year_index = min(year - 1, len(market_uptake) - 1)
            uptake_rate = market_uptake[year_index]
            treated_patients = int(target_population * uptake_rate)
            
            # Calculate costs
            cost_per_patient = sum(
                param.base_value for param in parameters
                if param.category == CostCategory.DIRECT_MEDICAL
            )
            
            total_cost = cost_per_patient * treated_patients
            
            annual_results.append({
                "year": year,
                "treated_patients": treated_patients,
                "uptake_rate": uptake_rate,
                "cost_per_patient": cost_per_patient,
                "total_cost": total_cost
            })
        
        # Calculate cumulative impact
        cumulative_cost = sum(result["total_cost"] for result in annual_results)
        cumulative_patients = sum(result["treated_patients"] for result in annual_results)
        
        results = {
            "model_id": model_id,
            "scenario_config": scenario_config,
            "annual_results": annual_results,
            "cumulative_cost": cumulative_cost,
            "cumulative_patients": cumulative_patients,
            "average_cost_per_patient": cumulative_cost / cumulative_patients if cumulative_patients > 0 else 0,
            "currency": model.currency.value,
            "analysis_date": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Completed budget impact analysis for model {model_id}")
        return results
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get economics statistics.
        
        Returns:
            Economics statistics
        """
        models = list(self._model_store.values())
        
        # Count by model type
        type_counts = {}
        for model in models:
            model_type = model.model_type.value
            type_counts[model_type] = type_counts.get(model_type, 0) + 1
        
        # Count by currency
        currency_counts = {}
        for model in models:
            currency = model.currency.value
            currency_counts[currency] = currency_counts.get(currency, 0) + 1
        
        # Parameter statistics
        total_parameters = sum(len(params) for params in self._parameter_store.values())
        avg_parameters = total_parameters / len(models) if models else 0
        
        return {
            "total_models": len(models),
            "by_type": type_counts,
            "by_currency": currency_counts,
            "total_parameters": total_parameters,
            "average_parameters_per_model": round(avg_parameters, 1),
            "sensitivity_analyses": len(self._analysis_store)
        }
