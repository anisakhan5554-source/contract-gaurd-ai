import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from risk_agent import apply_guardrails
from schemas import RiskAssessmentOutput, RiskLevel


def test_high_risk_triggers_human_review():
    assessment = RiskAssessmentOutput(
        clause_type="indemnification",
        risk_level=RiskLevel.high,
        risk_explanation="Test explanation",
        evidence="Test evidence",
        confidence=0.9,
        recommended_action="Test action"
    )
    result = apply_guardrails(assessment)
    assert result["reviewed_by_human"] == True


def test_low_confidence_triggers_human_review():
    assessment = RiskAssessmentOutput(
        clause_type="termination",
        risk_level=RiskLevel.low,
        risk_explanation="Test explanation",
        evidence="Test evidence",
        confidence=0.5,
        recommended_action="Test action"
    )
    result = apply_guardrails(assessment)
    assert result["reviewed_by_human"] == True


def test_low_risk_high_confidence_does_not_trigger_review():
    assessment = RiskAssessmentOutput(
        clause_type="payment",
        risk_level=RiskLevel.low,
        risk_explanation="Test explanation",
        evidence="Test evidence",
        confidence=0.95,
        recommended_action="No action needed"
    )
    result = apply_guardrails(assessment)
    assert result["reviewed_by_human"] == False