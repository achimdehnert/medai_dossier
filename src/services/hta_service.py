"""HTA service for managing HTA frameworks and submission requirements."""

from typing import List, Optional, Dict, Any, Set
from datetime import datetime
import logging
import asyncio

from ..models.hta import (
    HTAFramework,
    SubmissionRequirement,
    RequirementType,
    SubmissionStatus,
    HTASubmission,
    ComplianceCheck
)


logger = logging.getLogger(__name__)


class HTAService:
    """Service for managing HTA frameworks and submissions."""
    
    def __init__(self):
        """Initialize HTA service."""
        self._framework_store: Dict[str, HTAFramework] = {}
        self._submission_store: Dict[str, HTASubmission] = {}
        self._requirement_store: Dict[str, List[SubmissionRequirement]] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Initialize with default frameworks
        asyncio.create_task(self._initialize_frameworks())
    
    async def _initialize_frameworks(self):
        """Initialize default HTA frameworks."""
        default_frameworks = [
            {
                "id": "nice",
                "name": "NICE (UK)",
                "description": "National Institute for Health and Care Excellence",
                "country": "United Kingdom",
                "agency": "NICE",
                "submission_types": ["STA", "MTA", "HST"],
                "key_requirements": [
                    "Clinical evidence",
                    "Economic model",
                    "Budget impact analysis",
                    "Quality of life data"
                ],
                "timeline_weeks": 32,
                "fee_required": True
            },
            {
                "id": "gba",
                "name": "G-BA (Germany)",
                "description": "Gemeinsamer Bundesausschuss",
                "country": "Germany",
                "agency": "G-BA",
                "submission_types": ["Nutzenbewertung"],
                "key_requirements": [
                    "Clinical dossier",
                    "Comparative effectiveness",
                    "Patient-relevant endpoints",
                    "Quality of evidence"
                ],
                "timeline_weeks": 24,
                "fee_required": False
            },
            {
                "id": "has",
                "name": "HAS (France)",
                "description": "Haute Autorité de Santé",
                "country": "France",
                "agency": "HAS",
                "submission_types": ["ASMR", "SMR"],
                "key_requirements": [
                    "Clinical benefit assessment",
                    "Medical service improvement",
                    "Economic evaluation",
                    "Target population"
                ],
                "timeline_weeks": 28,
                "fee_required": True
            },
            {
                "id": "cadth",
                "name": "CADTH (Canada)",
                "description": "Canadian Agency for Drugs and Technologies in Health",
                "country": "Canada",
                "agency": "CADTH",
                "submission_types": ["CDR", "pCODR"],
                "key_requirements": [
                    "Systematic review",
                    "Economic evaluation",
                    "Budget impact analysis",
                    "Patient input"
                ],
                "timeline_weeks": 26,
                "fee_required": True
            }
        ]
        
        for framework_data in default_frameworks:
            try:
                framework = HTAFramework(**framework_data)
                self._framework_store[framework.id] = framework
                
                # Initialize requirements for each framework
                await self._create_default_requirements(framework.id)
                
            except Exception as e:
                self.logger.error(f"Failed to initialize framework {framework_data['id']}: {e}")
    
    async def _create_default_requirements(self, framework_id: str):
        """Create default requirements for a framework."""
        framework = self._framework_store.get(framework_id)
        if not framework:
            return
        
        # Default requirements based on framework
        requirements_data = []
        
        if framework_id == "nice":
            requirements_data = [
                {
                    "name": "Clinical Evidence Dossier",
                    "description": "Comprehensive clinical evidence package",
                    "requirement_type": RequirementType.CLINICAL,
                    "mandatory": True,
                    "deadline_weeks": 4
                },
                {
                    "name": "Economic Model",
                    "description": "Cost-effectiveness or cost-utility model",
                    "requirement_type": RequirementType.ECONOMIC,
                    "mandatory": True,
                    "deadline_weeks": 6
                },
                {
                    "name": "Budget Impact Analysis",
                    "description": "Budget impact assessment",
                    "requirement_type": RequirementType.ECONOMIC,
                    "mandatory": True,
                    "deadline_weeks": 6
                }
            ]
        elif framework_id == "gba":
            requirements_data = [
                {
                    "name": "Module 4 - Clinical Study Reports",
                    "description": "Detailed clinical study reports",
                    "requirement_type": RequirementType.CLINICAL,
                    "mandatory": True,
                    "deadline_weeks": 3
                },
                {
                    "name": "Module 3 - Quality Documentation",
                    "description": "Product quality documentation",
                    "requirement_type": RequirementType.REGULATORY,
                    "mandatory": True,
                    "deadline_weeks": 2
                }
            ]
        
        # Create requirement objects
        requirements = []
        for req_data in requirements_data:
            req_data["id"] = f"{framework_id}_{len(requirements) + 1}"
            req_data["framework_id"] = framework_id
            requirement = SubmissionRequirement(**req_data)
            requirements.append(requirement)
        
        self._requirement_store[framework_id] = requirements
    
    async def get_framework(
        self,
        framework_id: str
    ) -> Optional[HTAFramework]:
        """Get HTA framework by ID.
        
        Args:
            framework_id: Framework ID
            
        Returns:
            Framework instance or None
        """
        return self._framework_store.get(framework_id)
    
    async def list_frameworks(
        self,
        country: Optional[str] = None,
        agency: Optional[str] = None
    ) -> List[HTAFramework]:
        """List HTA frameworks with filters.
        
        Args:
            country: Filter by country
            agency: Filter by agency
            
        Returns:
            List of framework instances
        """
        frameworks = list(self._framework_store.values())
        
        # Apply filters
        if country:
            frameworks = [
                f for f in frameworks 
                if f.country.lower() == country.lower()
            ]
        
        if agency:
            frameworks = [
                f for f in frameworks
                if f.agency.lower() == agency.lower()
            ]
        
        # Sort by name
        frameworks.sort(key=lambda x: x.name)
        
        return frameworks
    
    async def get_requirements(
        self,
        framework_id: str
    ) -> List[SubmissionRequirement]:
        """Get requirements for HTA framework.
        
        Args:
            framework_id: Framework ID
            
        Returns:
            List of requirements
        """
        return self._requirement_store.get(framework_id, [])
    
    async def create_submission(
        self,
        submission_data: Dict[str, Any]
    ) -> HTASubmission:
        """Create new HTA submission.
        
        Args:
            submission_data: Submission data
            
        Returns:
            Created submission
            
        Raises:
            ValueError: If submission data is invalid
        """
        try:
            # Validate framework exists
            framework_id = submission_data.get("framework_id")
            if framework_id not in self._framework_store:
                raise ValueError(f"Framework not found: {framework_id}")
            
            # Create submission
            submission = HTASubmission(**submission_data)
            self._submission_store[submission.id] = submission
            
            self.logger.info(f"Created HTA submission: {submission.id}")
            return submission
            
        except Exception as e:
            self.logger.error(f"Failed to create submission: {e}")
            raise ValueError(f"Invalid submission data: {e}")
    
    async def get_submission(
        self,
        submission_id: str
    ) -> Optional[HTASubmission]:
        """Get HTA submission by ID.
        
        Args:
            submission_id: Submission ID
            
        Returns:
            Submission instance or None
        """
        return self._submission_store.get(submission_id)
    
    async def update_submission_status(
        self,
        submission_id: str,
        status: SubmissionStatus,
        notes: Optional[str] = None
    ) -> Optional[HTASubmission]:
        """Update submission status.
        
        Args:
            submission_id: Submission ID
            status: New status
            notes: Optional status notes
            
        Returns:
            Updated submission or None
        """
        submission = self._submission_store.get(submission_id)
        if not submission:
            return None
        
        # Update submission
        submission_data = submission.dict()
        submission_data["status"] = status
        submission_data["updated_at"] = datetime.utcnow()
        
        if notes:
            if "status_history" not in submission_data:
                submission_data["status_history"] = []
            
            submission_data["status_history"].append({
                "status": status.value,
                "timestamp": datetime.utcnow().isoformat(),
                "notes": notes
            })
        
        try:
            updated_submission = HTASubmission(**submission_data)
            self._submission_store[submission_id] = updated_submission
            
            self.logger.info(f"Updated submission {submission_id} status to {status.value}")
            return updated_submission
            
        except Exception as e:
            self.logger.error(f"Failed to update submission {submission_id}: {e}")
            raise ValueError(f"Invalid update data: {e}")
    
    async def check_compliance(
        self,
        dossier_id: str,
        framework_id: str
    ) -> ComplianceCheck:
        """Check dossier compliance with HTA framework.
        
        Args:
            dossier_id: Dossier ID
            framework_id: Framework ID
            
        Returns:
            Compliance check results
            
        Raises:
            ValueError: If framework not found
        """
        framework = await self.get_framework(framework_id)
        if not framework:
            raise ValueError(f"Framework not found: {framework_id}")
        
        requirements = await self.get_requirements(framework_id)
        
        # Initialize compliance check
        compliance_check = ComplianceCheck(
            id=f"cc_{dossier_id}_{framework_id}_{int(datetime.utcnow().timestamp())}",
            dossier_id=dossier_id,
            framework_id=framework_id,
            check_date=datetime.utcnow(),
            overall_score=0.0,
            requirements_met=0,
            total_requirements=len(requirements),
            missing_requirements=[],
            recommendations=[]
        )
        
        # Check each requirement (simplified demo logic)
        met_count = 0
        missing_requirements = []
        recommendations = []
        
        for requirement in requirements:
            # Simulate requirement checking
            # In practice, this would check actual dossier content
            is_met = self._simulate_requirement_check(requirement)
            
            if is_met:
                met_count += 1
            else:
                missing_requirements.append({
                    "requirement_id": requirement.id,
                    "name": requirement.name,
                    "type": requirement.requirement_type.value,
                    "mandatory": requirement.mandatory
                })
                
                if requirement.mandatory:
                    recommendations.append(
                        f"Critical: Complete {requirement.name} - this is mandatory for {framework.name}"
                    )
                else:
                    recommendations.append(
                        f"Optional: Consider adding {requirement.name} to strengthen submission"
                    )
        
        # Calculate overall score
        overall_score = (met_count / len(requirements)) * 100 if requirements else 0
        
        # Update compliance check
        compliance_check.overall_score = overall_score
        compliance_check.requirements_met = met_count
        compliance_check.missing_requirements = missing_requirements
        compliance_check.recommendations = recommendations
        
        # Add framework-specific recommendations
        if overall_score < 80:
            compliance_check.recommendations.append(
                f"Overall compliance is {overall_score:.1f}%. Consider addressing missing requirements before submission."
            )
        
        self.logger.info(
            f"Completed compliance check for dossier {dossier_id} against {framework_id}: {overall_score:.1f}%"
        )
        
        return compliance_check
    
    def _simulate_requirement_check(
        self,
        requirement: SubmissionRequirement
    ) -> bool:
        """Simulate requirement checking.
        
        Args:
            requirement: Requirement to check
            
        Returns:
            True if requirement is met
        """
        # Simple simulation - in practice would check actual dossier content
        import random
        
        # Higher probability for mandatory requirements
        if requirement.mandatory:
            return random.random() > 0.3  # 70% chance of being met
        else:
            return random.random() > 0.5  # 50% chance of being met
    
    async def get_submission_timeline(
        self,
        framework_id: str,
        submission_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get submission timeline for framework.
        
        Args:
            framework_id: Framework ID
            submission_type: Optional submission type
            
        Returns:
            Timeline information
        """
        framework = await self.get_framework(framework_id)
        if not framework:
            raise ValueError(f"Framework not found: {framework_id}")
        
        requirements = await self.get_requirements(framework_id)
        
        # Create timeline milestones
        milestones = []
        
        # Preparation phase
        milestones.append({
            "phase": "Preparation",
            "week": 0,
            "tasks": [
                "Gather required documentation",
                "Prepare clinical evidence package",
                "Develop economic model"
            ],
            "deliverables": ["Initial documentation"]
        })
        
        # Requirement deadlines
        for requirement in requirements:
            if requirement.deadline_weeks:
                milestones.append({
                    "phase": f"{requirement.name} Due",
                    "week": requirement.deadline_weeks,
                    "tasks": [f"Submit {requirement.name}"],
                    "deliverables": [requirement.name]
                })
        
        # Review phase
        review_start = framework.timeline_weeks - 8 if framework.timeline_weeks > 8 else framework.timeline_weeks // 2
        milestones.append({
            "phase": "Agency Review",
            "week": review_start,
            "tasks": [
                "Agency conducts technical review",
                "Clarification questions may be raised"
            ],
            "deliverables": ["Review comments"]
        })
        
        # Final decision
        milestones.append({
            "phase": "Final Decision",
            "week": framework.timeline_weeks,
            "tasks": [
                "Agency publishes decision",
                "Reimbursement recommendation issued"
            ],
            "deliverables": ["Final recommendation"]
        })
        
        # Sort by week
        milestones.sort(key=lambda x: x["week"])
        
        return {
            "framework_id": framework_id,
            "framework_name": framework.name,
            "total_weeks": framework.timeline_weeks,
            "submission_type": submission_type,
            "milestones": milestones,
            "key_deadlines": [
                {
                    "name": req.name,
                    "week": req.deadline_weeks,
                    "mandatory": req.mandatory
                }
                for req in requirements
                if req.deadline_weeks
            ]
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get HTA statistics.
        
        Returns:
            HTA statistics
        """
        frameworks = list(self._framework_store.values())
        submissions = list(self._submission_store.values())
        
        # Framework statistics
        countries = set(f.country for f in frameworks)
        agencies = set(f.agency for f in frameworks)
        
        # Submission statistics
        status_counts = {}
        for submission in submissions:
            status = submission.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Framework usage
        framework_usage = {}
        for submission in submissions:
            framework_id = submission.framework_id
            framework_usage[framework_id] = framework_usage.get(framework_id, 0) + 1
        
        return {
            "total_frameworks": len(frameworks),
            "countries": len(countries),
            "agencies": len(agencies),
            "total_submissions": len(submissions),
            "submission_status": status_counts,
            "framework_usage": framework_usage,
            "average_timeline": sum(f.timeline_weeks for f in frameworks) / len(frameworks) if frameworks else 0
        }
