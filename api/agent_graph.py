from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from retrieval import hybrid_search_clauses
from risk_agent import analyze_clause_risk, apply_guardrails
from schemas import RiskAssessmentOutput
from risk_agent import generate_redline, check_redline_scope


class ContractAnalysisState(TypedDict):
    clause_text: str
    precedents: Optional[list]
    risk_assessment: Optional[dict]
    guardrail_result: Optional[dict]
    redline: Optional[dict]
    redline_scope_check: Optional[dict]
    error: Optional[str]


def retrieve_node(state: ContractAnalysisState) -> ContractAnalysisState:
    try:
        precedents = hybrid_search_clauses(state["clause_text"], top_k=3)
        state["precedents"] = precedents
    except Exception as e:
        state["error"] = f"Retrieval failed: {str(e)}"
    return state


def risk_scoring_node(state: ContractAnalysisState) -> ContractAnalysisState:
    if state.get("error"):
        return state
    try:
        assessment = analyze_clause_risk(state["clause_text"])
        state["risk_assessment"] = assessment.model_dump()
    except Exception as e:
        state["error"] = f"Risk scoring failed: {str(e)}"
    return state


def guardrail_node(state: ContractAnalysisState) -> ContractAnalysisState:
    if state.get("error"):
        return state
    try:
        assessment = RiskAssessmentOutput(**state["risk_assessment"])
        guardrail_result = apply_guardrails(assessment)
        state["guardrail_result"] = guardrail_result
    except Exception as e:
        state["error"] = f"Guardrail check failed: {str(e)}"
    return state

def redline_node(state: ContractAnalysisState) -> ContractAnalysisState:
    if state.get("error"):
        return state

    guardrail_result = state.get("guardrail_result", {})
    risk_assessment = state.get("risk_assessment", {})

    if risk_assessment.get("risk_level") not in ("high", "critical"):
        state["redline"] = None
        return state

    try:
        redline = generate_redline(
            clause_text=state["clause_text"],
            risk_level=risk_assessment["risk_level"],
            risk_explanation=risk_assessment["risk_explanation"],
            recommended_action=risk_assessment["recommended_action"]
        )
        scope_check = check_redline_scope(state["clause_text"], redline.suggested_rewrite)

        state["redline"] = redline.model_dump()
        state["redline_scope_check"] = scope_check
    except Exception as e:
        state["error"] = f"Redline generation failed: {str(e)}"

    return state



def build_graph():
    graph = StateGraph(ContractAnalysisState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("score_risk", risk_scoring_node)
    graph.add_node("check_guardrails", guardrail_node)
    graph.add_node("generate_redline", redline_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "score_risk")
    graph.add_edge("score_risk", "check_guardrails")
    graph.add_edge("check_guardrails", "generate_redline")
    graph.add_edge("generate_redline", END)

    return graph.compile()
contract_analysis_graph=build_graph()


if __name__ == "__main__":
    test_clause = "Company shall indemnify Executive against any and all claims, without any cap or limitation on liability, for actions taken in good faith."

    result = contract_analysis_graph.invoke({
        "clause_text": test_clause,
        "precedents": None,
        "risk_assessment": None,
        "guardrail_result": None,
        "redline": None,
        "redline_scope_check": None,
        "error": None
    })

    print("=== FINAL STATE ===")
    print(f"Error: {result.get('error')}")
    print(f"Risk Assessment: {result.get('risk_assessment')}")
    print(f"Guardrail Result: {result.get('guardrail_result')}")
    print(f"Redline: {result.get('redline')}")
    print(f"Scope Check: {result.get('redline_scope_check')}")