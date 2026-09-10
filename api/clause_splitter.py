import re

def split_into_clauses(text: str):
    pattern = r'\n\s*(?:\d+\.\d*|\bSection\s+\d+\b|\bARTICLE\s+[IVX]+\b)'
    parts = re.split(pattern, text)
    clauses = [p.strip() for p in parts if len(p.strip()) > 100]
    return clauses