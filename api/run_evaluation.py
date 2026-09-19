import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from risk_agent import analyze_clause_risk, apply_guardrails
from retrieval import hybrid_search_clauses

RISK_RANK = {"low": 1, "medium": 2, "high": 3, "critical": 4}

def load_labeled_data():
    path = os.path.join( "data", "evaluation", "labeled_clauses.json")
    with open(path, "r") as f:
        return json.load(f)

def check_hallucination(clause_text, evidence):
    return evidence.lower() in clause_text.lower()

def check_groundedness(clause_text, risk_explanation):
    precedents = hybrid_search_clauses(clause_text, top_k=3)
    for p in precedents:
        words = set(p["text"].lower().split())
        explanation_words = set(risk_explanation.lower().split())
        if len(words & explanation_words) >= 3:
            return True
    return False

def run_eval():
    data = load_labeled_data()
    correct = 0
    hallucination_free_count = 0
    escalated_count = 0
    grounded_count = 0
    false_negatives = 0
    false_positives = 0
    results = []

    for item in data:
        try:
            assessment = analyze_clause_risk(item["text"])
            predicted = assessment.risk_level.value
            expected = item["expected_risk"]
            match = predicted == expected

            hallucination_free = check_hallucination(item["text"], assessment.evidence)
            grounded = check_groundedness(item["text"], assessment.risk_explanation)
            guardrail_result = apply_guardrails(assessment)
            escalated = guardrail_result["reviewed_by_human"]

            is_false_negative = RISK_RANK[predicted] < RISK_RANK[expected]
            is_false_positive = RISK_RANK[predicted] > RISK_RANK[expected]

            if match: correct += 1
            if hallucination_free: hallucination_free_count += 1
            if escalated: escalated_count += 1
            if grounded: grounded_count += 1
            if is_false_negative: false_negatives += 1
            if is_false_positive: false_positives += 1

            results.append({
                "text": item["text"][:60], "expected": expected, "predicted": predicted,
                "match": match, "confidence": assessment.confidence,
                "hallucination_free": hallucination_free, "escalated": escalated,
                "grounded": grounded, "false_negative": is_false_negative,
                "false_positive": is_false_positive
            })
        except Exception as e:
            results.append({"text": item["text"][:60], "error": str(e)})

    n = len(data)
    accuracy = correct / n
    print(f"\n=== EVALUATION RESULTS ===")
    print(f"Dataset size: {n}")
    print(f"Accuracy: {accuracy:.2%} ({correct}/{n})")
    print(f"False Negatives (predicted risk too LOW - dangerous): {false_negatives}/{n}")
    print(f"False Positives (predicted risk too HIGH - over-cautious): {false_positives}/{n}")
    print(f"Hallucination rate: {1-hallucination_free_count/n:.2%}")
    print(f"Human escalation rate: {escalated_count/n:.2%}")
    print(f"Groundedness rate: {grounded_count/n:.2%}\n")

    if accuracy < 0.5:
        print("⚠️ WARNING: Accuracy below 50% threshold - review model/prompt")

    for r in results:
        print(r)

    return accuracy

if __name__ == "__main__":
    acc = run_eval()
    sys.exit(0 if acc >= 0.5 else 1)