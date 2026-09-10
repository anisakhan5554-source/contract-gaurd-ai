import os
from google import genai
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client

def embed_text(text_input: str):
    result = get_client().models.embed_content(
        model="models/gemini-embedding-001",
        contents=text_input
    )
    return result.embeddings[0].values

def retrieve_similar_clauses(query_text: str, top_k: int = 3, db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    query_embedding = embed_text(query_text)
    embedding_str = str(query_embedding)

    sql = text("""
        SELECT id, source, text, clause_type,
               1 - (embedding <=> :query_embedding) AS similarity
        FROM precedent_clauses
        ORDER BY embedding <=> :query_embedding
        LIMIT :top_k
    """)

    results = db.execute(sql, {"query_embedding": embedding_str, "top_k": top_k}).fetchall()

    if close_db:
        db.close()

    return [
        {
            "id": str(r.id),
            "source": r.source,
            "text": r.text,
            "clause_type": r.clause_type,
            "similarity": float(r.similarity)
        }
        for r in results
    ]


def keyword_search_clauses(query_text: str, top_k: int = 3, db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    sql = text("""
        SELECT id, source, text, clause_type,
               ts_rank(text_search, websearch_to_tsquery('english', :query_text)) AS rank
        FROM precedent_clauses
        WHERE text_search @@ websearch_to_tsquery('english', :query_text)
        ORDER BY rank DESC
        LIMIT :top_k
    """)

    results = db.execute(sql, {"query_text": query_text, "top_k": top_k}).fetchall()

    if close_db:
        db.close()

    return [
        {
            "id": str(r.id),
            "source": r.source,
            "text": r.text,
            "clause_type": r.clause_type,
            "rank": float(r.rank)
        }
        for r in results
    ]


def hybrid_search_clauses(query_text: str, top_k: int = 3, db: Session = None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    fetch_k = max(top_k * 3, 10)
    dense_results = retrieve_similar_clauses(query_text, top_k=fetch_k, db=db)
    keyword_results = keyword_search_clauses(query_text, top_k=fetch_k, db=db)

    if close_db:
        db.close()

    combined = {}
    for r in dense_results:
        combined[r["id"]] = {**r, "dense_score": r["similarity"], "keyword_score": 0.0}
    for r in keyword_results:
        if r["id"] in combined:
            combined[r["id"]]["keyword_score"] = r["rank"]
        else:
            combined[r["id"]] = {**r, "dense_score": 0.0, "keyword_score": r["rank"]}

    for item in combined.values():
        item["hybrid_score"] = (0.7 * item["dense_score"]) + (0.3 * min(item["keyword_score"], 1.0))

    ranked = sorted(combined.values(), key=lambda x: x["hybrid_score"], reverse=True)
    return ranked[:top_k]


if __name__ == "__main__":
    test_clause = "Executive's employment."

    print("=== DENSE ONLY ===")
    for r in retrieve_similar_clauses(test_clause, top_k=3):
        print(f"[{r['similarity']:.3f}] {r['text'][:100]}")

    print("\n=== KEYWORD ONLY ===")
    for r in keyword_search_clauses(test_clause, top_k=3):
        print(f"[{r['rank']:.3f}] {r['text'][:100]}")

    print("\n=== HYBRID ===")
    for r in hybrid_search_clauses(test_clause, top_k=3):
        print(f"[hybrid={r['hybrid_score']:.3f} dense={r['dense_score']:.3f} kw={r['keyword_score']:.3f}] {r['text'][:100]}")