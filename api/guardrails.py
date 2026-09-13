import re

ALLOWED_EXTENSIONS = (".pdf", ".txt")
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB
MIN_FILE_SIZE_BYTES = 10  # reject near-empty files


def validate_input_file(filename: str, file_size_bytes: int) -> dict:
    errors = []

    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        errors.append(f"Unsupported file type. Allowed: {ALLOWED_EXTENSIONS}")

    if file_size_bytes > MAX_FILE_SIZE_BYTES:
        errors.append(f"File too large ({file_size_bytes} bytes). Max: {MAX_FILE_SIZE_BYTES} bytes")

    if file_size_bytes < MIN_FILE_SIZE_BYTES:
        errors.append("File is empty or too small to be a valid contract")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (all )?(previous|prior|above) instructions",
    r"you are now",
    r"new instructions?:",
    r"system prompt",
    r"forget (everything|all previous)",
    r"act as (if|a)",
    r"override (your|the) (guidelines|rules|instructions)",
    r"reveal your (instructions|prompt|system)",
]


def detect_prompt_injection(text: str) -> dict:
    text_lower = text.lower()
    matches = []

    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            matches.append(pattern)

    return {
        "injection_detected": len(matches) > 0,
        "matched_patterns": matches
    }


def detect_pii(text: str) -> dict:
    patterns = {
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "email": r'\b[\w.-]+@[\w.-]+\.\w+\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
    }
    found = {}
    for label, pattern in patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            found[label] = len(matches)
    return {"pii_detected": len(found) > 0, "types": found}