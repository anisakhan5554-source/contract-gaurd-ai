from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def diff_clauses(v1_clauses: list, v2_clauses: list, similarity_threshold: float = 0.75) -> dict:
    matched_pairs = []
    used_v2_indices = set()

    for v1_clause in v1_clauses:
        best_match = None
        best_score = 0.0
        best_index = None

        for i, v2_clause in enumerate(v2_clauses):
            if i in used_v2_indices:
                continue
            score = similarity(v1_clause["text"], v2_clause["text"])
            if score > best_score:
                best_score = score
                best_match = v2_clause
                best_index = i

        if best_match and best_score >= similarity_threshold:
            used_v2_indices.add(best_index)

            print("DEBUG VERSION DIFF:", best_score)

            status = "unchanged" if best_score >= 0.99 else "modified"

            print("DEBUG STATUS:", status)

            matched_pairs.append ({
                "v1_clause": v1_clause,
                "v2_clause": best_match,
                "similarity": best_score,
                "status": status
            })
        else:
            matched_pairs.append({
                "v1_clause": v1_clause,
                "v2_clause": None,
                "similarity": 0.0,
                "status": "removed"
            })

    added_clauses = [
        v2_clauses[i] for i in range(len(v2_clauses)) if i not in used_v2_indices
    ]

    return {
        "matched_pairs": matched_pairs,
        "added": added_clauses,
        "removed_count": sum(1 for p in matched_pairs if p["status"] == "removed"),
        "modified_count": sum(1 for p in matched_pairs if p["status"] == "modified"),
        "unchanged_count": sum(1 for p in matched_pairs if p["status"] == "unchanged"),
        "added_count": len(added_clauses),
    }