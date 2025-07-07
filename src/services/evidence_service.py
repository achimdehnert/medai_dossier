"""Evidence service for managing clinical evidence data."""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio

from ..models.evidence import (
    ClinicalEvidence, 
    EvidenceType, 
    StudyDesign,
    OutcomeType,
    RiskOfBias
)


logger = logging.getLogger(__name__)


class EvidenceService:
    """Service for managing clinical evidence."""
    
    def __init__(self):
        """Initialize evidence service."""
        self._evidence_store: Dict[str, ClinicalEvidence] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
        
    async def create_evidence(
        self,
        evidence_data: Dict[str, Any]
    ) -> ClinicalEvidence:
        """Create new clinical evidence.
        
        Args:
            evidence_data: Evidence data dictionary
            
        Returns:
            Created evidence instance
            
        Raises:
            ValueError: If evidence data is invalid
        """
        try:
            # Create evidence instance
            evidence = ClinicalEvidence(**evidence_data)
            
            # Store evidence
            self._evidence_store[evidence.id] = evidence
            
            self.logger.info(f"Created evidence: {evidence.id}")
            return evidence
            
        except Exception as e:
            self.logger.error(f"Failed to create evidence: {e}")
            raise ValueError(f"Invalid evidence data: {e}")
    
    async def get_evidence(
        self,
        evidence_id: str
    ) -> Optional[ClinicalEvidence]:
        """Get evidence by ID.
        
        Args:
            evidence_id: Evidence ID
            
        Returns:
            Evidence instance or None
        """
        return self._evidence_store.get(evidence_id)
    
    async def list_evidence(
        self,
        evidence_type: Optional[EvidenceType] = None,
        study_design: Optional[StudyDesign] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[ClinicalEvidence]:
        """List evidence with filters.
        
        Args:
            evidence_type: Filter by evidence type
            study_design: Filter by study design
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of evidence instances
        """
        evidence_list = list(self._evidence_store.values())
        
        # Apply filters
        if evidence_type:
            evidence_list = [
                e for e in evidence_list 
                if e.evidence_type == evidence_type
            ]
        
        if study_design:
            evidence_list = [
                e for e in evidence_list
                if e.study_design == study_design
            ]
        
        # Sort by creation date (newest first)
        evidence_list.sort(
            key=lambda x: x.created_at or datetime.min,
            reverse=True
        )
        
        # Apply pagination
        return evidence_list[offset:offset + limit]
    
    async def update_evidence(
        self,
        evidence_id: str,
        updates: Dict[str, Any]
    ) -> Optional[ClinicalEvidence]:
        """Update evidence.
        
        Args:
            evidence_id: Evidence ID
            updates: Update data
            
        Returns:
            Updated evidence or None
        """
        evidence = self._evidence_store.get(evidence_id)
        if not evidence:
            return None
        
        # Create updated evidence
        evidence_data = evidence.dict()
        evidence_data.update(updates)
        evidence_data["updated_at"] = datetime.utcnow()
        
        try:
            updated_evidence = ClinicalEvidence(**evidence_data)
            self._evidence_store[evidence_id] = updated_evidence
            
            self.logger.info(f"Updated evidence: {evidence_id}")
            return updated_evidence
            
        except Exception as e:
            self.logger.error(f"Failed to update evidence {evidence_id}: {e}")
            raise ValueError(f"Invalid update data: {e}")
    
    async def delete_evidence(
        self,
        evidence_id: str
    ) -> bool:
        """Delete evidence.
        
        Args:
            evidence_id: Evidence ID
            
        Returns:
            True if deleted, False if not found
        """
        if evidence_id in self._evidence_store:
            del self._evidence_store[evidence_id]
            self.logger.info(f"Deleted evidence: {evidence_id}")
            return True
        return False
    
    async def search_evidence(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ClinicalEvidence]:
        """Search evidence by text query.
        
        Args:
            query: Search query
            filters: Additional filters
            
        Returns:
            List of matching evidence
        """
        results = []
        query_lower = query.lower()
        
        for evidence in self._evidence_store.values():
            # Search in key fields
            searchable_text = " ".join([
                evidence.title.lower(),
                evidence.description.lower() if evidence.description else "",
                evidence.study_population.lower() if evidence.study_population else "",
                str(evidence.primary_endpoint).lower() if evidence.primary_endpoint else ""
            ])
            
            if query_lower in searchable_text:
                results.append(evidence)
        
        # Apply additional filters if provided
        if filters:
            if "evidence_type" in filters:
                results = [
                    e for e in results 
                    if e.evidence_type == filters["evidence_type"]
                ]
            
            if "study_design" in filters:
                results = [
                    e for e in results
                    if e.study_design == filters["study_design"]
                ]
        
        return results
    
    async def get_evidence_by_dossier(
        self,
        dossier_id: str
    ) -> List[ClinicalEvidence]:
        """Get evidence linked to a dossier.
        
        Args:
            dossier_id: Dossier ID
            
        Returns:
            List of linked evidence
        """
        # This would typically query a relationship table
        # For now, return empty list as demo
        return []
    
    async def assess_quality(
        self,
        evidence_id: str
    ) -> Dict[str, Any]:
        """Assess evidence quality.
        
        Args:
            evidence_id: Evidence ID
            
        Returns:
            Quality assessment results
        """
        evidence = await self.get_evidence(evidence_id)
        if not evidence:
            raise ValueError(f"Evidence not found: {evidence_id}")
        
        # Simple quality assessment based on available data
        quality_score = 0
        criteria = {}
        
        # Study design quality
        design_scores = {
            StudyDesign.RCT: 5,
            StudyDesign.COHORT: 4,
            StudyDesign.CASE_CONTROL: 3,
            StudyDesign.CROSS_SECTIONAL: 2,
            StudyDesign.CASE_SERIES: 1
        }
        
        design_score = design_scores.get(evidence.study_design, 0)
        quality_score += design_score
        criteria["study_design"] = {
            "score": design_score,
            "weight": 0.3
        }
        
        # Sample size quality
        sample_size = evidence.sample_size or 0
        if sample_size >= 1000:
            size_score = 5
        elif sample_size >= 500:
            size_score = 4
        elif sample_size >= 100:
            size_score = 3
        elif sample_size >= 50:
            size_score = 2
        else:
            size_score = 1
        
        quality_score += size_score
        criteria["sample_size"] = {
            "score": size_score,
            "weight": 0.2
        }
        
        # Risk of bias
        if evidence.risk_of_bias:
            bias_scores = {
                RiskOfBias.LOW: 5,
                RiskOfBias.MODERATE: 3,
                RiskOfBias.HIGH: 1,
                RiskOfBias.UNCLEAR: 2
            }
            bias_score = bias_scores.get(evidence.risk_of_bias, 0)
        else:
            bias_score = 0
        
        quality_score += bias_score
        criteria["risk_of_bias"] = {
            "score": bias_score,
            "weight": 0.3
        }
        
        # Publication status
        pub_score = 3 if evidence.publication_status == "published" else 1
        quality_score += pub_score
        criteria["publication_status"] = {
            "score": pub_score,
            "weight": 0.2
        }
        
        # Calculate weighted score
        total_weighted_score = sum(
            criteria[key]["score"] * criteria[key]["weight"]
            for key in criteria
        )
        
        # Convert to percentage
        max_possible_score = sum(5 * criteria[key]["weight"] for key in criteria)
        quality_percentage = (total_weighted_score / max_possible_score) * 100
        
        return {
            "evidence_id": evidence_id,
            "overall_score": round(quality_percentage, 1),
            "raw_score": quality_score,
            "max_score": 20,
            "criteria": criteria,
            "assessment_date": datetime.utcnow().isoformat(),
            "recommendations": self._generate_quality_recommendations(
                evidence, criteria
            )
        }
    
    def _generate_quality_recommendations(
        self,
        evidence: ClinicalEvidence,
        criteria: Dict[str, Any]
    ) -> List[str]:
        """Generate quality improvement recommendations.
        
        Args:
            evidence: Evidence instance
            criteria: Quality criteria scores
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Study design recommendations
        if criteria["study_design"]["score"] < 4:
            recommendations.append(
                "Consider supplementing with higher-quality study designs (RCT or cohort studies)"
            )
        
        # Sample size recommendations
        if criteria["sample_size"]["score"] < 3:
            recommendations.append(
                "Seek additional studies with larger sample sizes to strengthen evidence"
            )
        
        # Risk of bias recommendations
        if criteria["risk_of_bias"]["score"] < 4:
            recommendations.append(
                "Look for studies with lower risk of bias or conduct bias assessment"
            )
        
        # Publication recommendations
        if criteria["publication_status"]["score"] < 3:
            recommendations.append(
                "Prioritize peer-reviewed published studies when available"
            )
        
        return recommendations
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get evidence statistics.
        
        Returns:
            Evidence statistics
        """
        evidence_list = list(self._evidence_store.values())
        
        # Count by evidence type
        type_counts = {}
        for evidence in evidence_list:
            evidence_type = evidence.evidence_type.value
            type_counts[evidence_type] = type_counts.get(evidence_type, 0) + 1
        
        # Count by study design
        design_counts = {}
        for evidence in evidence_list:
            study_design = evidence.study_design.value
            design_counts[study_design] = design_counts.get(study_design, 0) + 1
        
        # Quality distribution
        quality_scores = []
        for evidence in evidence_list:
            try:
                assessment = await self.assess_quality(evidence.id)
                quality_scores.append(assessment["overall_score"])
            except:
                continue
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            "total_evidence": len(evidence_list),
            "by_type": type_counts,
            "by_design": design_counts,
            "average_quality_score": round(avg_quality, 1),
            "quality_distribution": {
                "high": len([s for s in quality_scores if s >= 80]),
                "medium": len([s for s in quality_scores if 60 <= s < 80]),
                "low": len([s for s in quality_scores if s < 60])
            }
        }
