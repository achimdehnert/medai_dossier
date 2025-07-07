"""HTA framework management API endpoints."""

from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()


@router.get("/frameworks")
async def get_hta_frameworks():
    """Get available HTA frameworks and their requirements."""
    frameworks = {
        "amcp": {
            "name": "Academy of Managed Care Pharmacy",
            "region": "USA",
            "requirements": ["Executive Summary", "Clinical Evidence", "Economic Evidence"]
        },
        "eunethta": {
            "name": "European Network for Health Technology Assessment",
            "region": "Europe",
            "requirements": ["Clinical Effectiveness", "Safety", "Economic Evaluation"]
        },
        "g_ba": {
            "name": "Gemeinsamer Bundesausschuss",
            "region": "Germany",
            "requirements": ["Benefit Assessment", "Comparative Effectiveness"]
        },
        "nice": {
            "name": "National Institute for Health and Care Excellence",
            "region": "UK",
            "requirements": ["Clinical Evidence", "Cost-Effectiveness", "Impact Assessment"]
        },
        "has": {
            "name": "Haute Autorité de Santé",
            "region": "France",
            "requirements": ["Medical Service", "Medical Improvement", "Economic Impact"]
        }
    }
    return frameworks


@router.get("/templates/{framework}")
async def get_framework_template(framework: str):
    """Get template structure for specific HTA framework."""
    if framework not in ["amcp", "eunethta", "g_ba", "nice", "has"]:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    return {
        "framework": framework,
        "template": f"Template structure for {framework} - to be implemented"
    }
