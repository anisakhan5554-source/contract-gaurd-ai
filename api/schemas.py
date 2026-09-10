from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RiskAssessmentOutput(BaseModel):
    clause_type: str = Field(description="Type of clause, e.g. indemnification, termination, liability")
    risk_level: RiskLevel = Field(description="Overall risk level of this clause")
    risk_explanation: str = Field(description="Plain-language explanation of why this clause is risky")
    evidence: str = Field(description="The specific part of the clause text that justifies this risk rating")
    confidence: float = Field(ge=0.0, le=1.0, description="Model's confidence in this assessment, 0 to 1")
    recommended_action: str = Field(description="What should be done about this clause, e.g. 'cap liability', 'no action needed'")


class RedlineOutput(BaseModel):
    original_clause: str
    suggested_rewrite: str
    rationale: str = Field(description="Why this rewrite addresses the identified risk")