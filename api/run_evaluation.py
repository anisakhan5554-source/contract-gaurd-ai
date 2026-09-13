import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from risk_agent import analyze_clause_risk

def load_labeled_data():
    path = os.path.join("..", "data", "evaluation", "labeled_clauses.json")
    with open(path, "r") as f:
        return json.load(f)

def check_hallucination(clause_text, evidence):
    return evidence.lower() in clause_text.lower()

def run_eval():
    data = load_labeled_data()
    correct = 0
    hallucination_free_count = 0
    results = []

    for item in data:
        try:
            assessment = analyze_clause_risk(item["text"])
            predicted = assessment.risk_level.value
            expected = item["expected_risk"]
            match = predicted == expected
            hallucination_free = check_hallucination(item["text"], assessment.evidence)

            if match:
                correct += 1
            if hallucination_free:
                hallucination_free_count += 1

            results.append({
                "text": item["text"][:60],
                "expected": expected,
                "predicted": predicted,
                "match": match,
                "confidence": assessment.confidence,
                "hallucination_free": hallucination_free
            })
        except Exception as e:
            results.append({"text": item["text"][:60], "error": str(e)})

    accuracy = correct / len(data)
    hallucination_rate = 1 - (hallucination_free_count / len(data))
    print(f"\n=== EVALUATION RESULTS ===")
    print(f"Accuracy: {accuracy:.2%} ({correct}/{len(data)})")
    print(f"Hallucination rate: {hallucination_rate:.2%} (evidence not found in {len(data) - hallucination_free_count}/{len(data)} cases)\n")
    for r in results:
        print(r)

if __name__ == "__main__":
    run_eval()