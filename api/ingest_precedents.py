import os
import re
import sys
from google import genai
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database import SessionLocal
from models import PrecedentClause, ClauseType

PRECEDENTS_DIR = "../data/precedents"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def load_contract_files():
    files = []
    for filename in os.listdir(PRECEDENTS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(PRECEDENTS_DIR, filename)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            files.append((filename, text))
    return files


def split_into_clauses(text):
    pattern = r'\n\s*(?:\d+\.\d*|\bSection\s+\d+\b|\bARTICLE\s+[IVX]+\b)'
    parts = re.split(pattern, text)
    clauses = [p.strip() for p in parts if len(p.strip()) > 100]
    return clauses


def get_embedding(text):
    result = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values


def guess_clause_type(text):
    text_lower = text.lower()
    if "indemnif" in text_lower:
        return ClauseType.indemnification
    elif "terminat" in text_lower:
        return ClauseType.termination
    elif "liabilit" in text_lower:
        return ClauseType.liability
    elif "confidential" in text_lower:
        return ClauseType.confidentiality
    elif "payment" in text_lower or "compensation" in text_lower:
        return ClauseType.payment
    else:
        return ClauseType.other


if __name__ == "__main__":
    contracts = load_contract_files()
    db: Session = SessionLocal()

    total_inserted = 0

    for filename, text in contracts:
        clauses = split_into_clauses(text)
        print(f"--- {filename}: {len(clauses)} clauses ---")

        for i, clause_text in enumerate(clauses):
            try:
                embedding = get_embedding(clause_text)
                clause_type = guess_clause_type(clause_text)

                record = PrecedentClause(
                    source=filename,
                    text=clause_text,
                    clause_type=clause_type,
                    embedding=embedding
                )
                db.add(record)
                total_inserted += 1

                if (i + 1) % 10 == 0:
                    print(f"  Embedded {i + 1}/{len(clauses)} clauses...")

            except Exception as e:
                print(f"  Skipped clause {i} due to error: {e}")

        db.commit()

    print(f"\nDone. Inserted {total_inserted} precedent clauses into the database.")
    db.close()