import os
import hashlib
from uuid import UUID
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import re
from database import get_db, get_engine
from models import Base, Contract, Clause, RiskAssessment, RedlineSuggestion, AuditLog
from clause_splitter import split_into_clauses
from risk_agent import analyze_clause_risk, apply_guardrails, save_risk_assessment
from guardrails import validate_input_file, detect_prompt_injection
from version_diff import diff_clauses
from agent_graph import contract_analysis_graph
from schemas import RiskAssessmentOutput
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth import hash_password, verify_password, create_access_token, decode_access_token
from models import User
from jose import JWTError
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("contractguard")

def log_event(event: str, **kwargs):
    logger.info(json.dumps({"event": event, **kwargs}))

app = FastAPI(title="Contract Risk Analyzer & Negotiator")

app = FastAPI(title="Contract Risk Analyzer & Negotiator")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(401, "Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user


UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=get_engine())


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/contracts/upload")
def upload_contract(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contents = file.file.read()
    validation = validate_input_file(file.filename, len(contents))
    if not validation["valid"]:
        raise HTTPException(400, "; ".join(validation["errors"]))

    file_hash = hashlib.sha256(contents).hexdigest()

    existing = db.query(Contract).filter(Contract.file_hash == file_hash).first()
    if existing:
        return {"message": "Contract already uploaded", "contract_id": str(existing.id), "version": existing.version}

    previous_version = (
        db.query(Contract)
        .filter(Contract.filename == file.filename)
        .order_by(Contract.version.desc())
        .first()
    )

    new_version = 1
    parent_id = None
    if previous_version:
        new_version = previous_version.version + 1
        parent_id = previous_version.id

    save_path = os.path.join(UPLOAD_DIR, f"{file_hash}_{file.filename}")
    with open(save_path, "wb") as f:
        f.write(contents)

    contract = Contract(
        filename=file.filename,
        file_hash=file_hash,
        status="uploaded",
        version=new_version,
        parent_contract_id=parent_id,
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)

    log = AuditLog(
        actor="system",
        action="uploaded_contract",
        entity_type="contract",
        entity_id=contract.id,
        details=f"filename={file.filename}, version={new_version}" + (f", parent={parent_id}" if parent_id else ""),
    )
    db.add(log)
    db.commit()

    return {"message": "Uploaded", "contract_id": str(contract.id), "status": contract.status, "version": new_version}


@app.get("/contracts")
def list_contracts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contracts = db.query(Contract).all()
    return [
        {"id": str(c.id), "filename": c.filename, "status": c.status, "created_at": c.created_at}
        for c in contracts
    ]


@app.get("/contracts/{contract_id}/clauses")
def get_clauses(contract_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(404, "Contract not found")

    results = []
    for clause in contract.clauses:
        assessment = clause.risk_assessment
        results.append({
            "clause_id": str(clause.id),
            "text": clause.text,
            "clause_type": clause.clause_type,
            "risk_score": assessment.risk_score if assessment else None,
            "rationale": assessment.rationale if assessment else None,
            "confidence": assessment.confidence if assessment else None,
            "reviewed_by_human": assessment.reviewed_by_human if assessment else None,
        })
    return results


@app.get("/audit-log")
def get_audit_log(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return [
        {"actor": l.actor, "action": l.action, "entity_type": l.entity_type,
         "entity_id": str(l.entity_id), "timestamp": l.timestamp}
        for l in logs
    ]


@app.post("/contracts/{contract_id}/analyze")
def analyze_contract(contract_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(404, "Contract not found")

    # existing_assessments = db.query(RiskAssessment).join(Clause).filter(Clause.contract_id == contract.id).count()
    # if existing_assessments > 0:
    #     raise HTTPException(400, "Contract already analyzed. Delete existing assessments to re-run.")

    file_path = None
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(contract.file_hash):
            file_path = os.path.join(UPLOAD_DIR, filename)
            break

    if not file_path:
        raise HTTPException(404, "Uploaded file not found on disk")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text_content = f.read()

    injection_check = detect_prompt_injection(text_content)
    if injection_check["injection_detected"]:
        log = AuditLog(
            actor="system",
            action="prompt_injection_flagged",
            entity_type="contract",
            entity_id=contract.id,
            details=f"Matched patterns: {injection_check['matched_patterns']}",
        )

        db.add(log)
        db.commit()
        raw_clauses = split_into_clauses(text_content)

    results = []
    for clause_text in raw_clauses:
        clause = Clause(contract_id=contract.id, text=clause_text)
        db.add(clause)
        db.commit()
        db.refresh(clause)

        try:
            graph_result = contract_analysis_graph.invoke({
                "clause_text": clause_text,
                "precedents": None,
                "risk_assessment": None,
                "guardrail_result": None,
                "redline": None,
                "redline_scope_check": None,
                "error": None
            })

            if graph_result.get("error"):
                raise Exception(graph_result["error"])

            assessment = RiskAssessmentOutput(**graph_result["risk_assessment"])
            guardrail_result = graph_result["guardrail_result"]
            save_risk_assessment(clause.id, assessment, guardrail_result, db=db)

            log = AuditLog(
                actor="risk_agent",
                action="analyzed_clause",
                entity_type="clause",
                entity_id=clause.id,
                details=f"risk={assessment.risk_level.value}, reviewed_by_human={guardrail_result['reviewed_by_human']}",
            )
            db.add(log)
            db.commit()
            log_event("clause_analyzed", clause_id=str(clause.id), risk_level=assessment.risk_level.value,
                      confidence=assessment.confidence)


            results.append({
                "clause_id": str(clause.id),
                "risk_level": assessment.risk_level.value,
                "confidence": assessment.confidence,
                "reviewed_by_human": guardrail_result["reviewed_by_human"],
            })
        except Exception as e:
            results.append({
                "clause_id": str(clause.id),
                "error": str(e)
            })

    contract.status = "analyzed"
    db.commit()

    return {"contract_id": str(contract.id), "clauses_analyzed": len(results), "results": results}


@app.get("/contracts/{contract_id}/history")
def get_contract_history(contract_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(404, "Contract not found")

    all_versions = db.query(Contract).filter(Contract.filename == contract.filename).order_by(Contract.version).all()

    return [
        {
            "contract_id": str(c.id),
            "version": c.version,
            "status": c.status,
            "created_at": c.created_at,
            "parent_contract_id": str(c.parent_contract_id) if c.parent_contract_id else None,
        }
        for c in all_versions
    ]


@app.post("/contracts/{v2_contract_id}/compare")
def compare_versions(v2_contract_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v2_contract = db.query(Contract).filter(Contract.id == v2_contract_id).first()
    if not v2_contract:
        raise HTTPException(404, "Contract not found")
    if not v2_contract.parent_contract_id:
        raise HTTPException(400, "This contract has no previous version to compare against")

    v1_contract = db.query(Contract).filter(Contract.id == v2_contract.parent_contract_id).first()

    v1_clauses = [{"id": str(c.id), "text": c.text, "risk_assessment": c.risk_assessment} for c in v1_contract.clauses]
    v2_clauses_raw = [{"id": str(c.id), "text": c.text, "clause_obj": c} for c in v2_contract.clauses]

    if not v2_clauses_raw:
        raise HTTPException(400, "Version 2 has not been analyzed yet. Run /analyze first.")

    diff_result = diff_clauses(v1_clauses, v2_clauses_raw, similarity_threshold=0.5)

    comparison_results = []
    regressions = []
    improvements = []

    risk_rank = {"low": 1, "medium": 2, "high": 3, "critical": 4}

    for pair in diff_result["matched_pairs"]:
        v1_clause = pair["v1_clause"]
        v2_clause = pair["v2_clause"]

        v1_risk = v1_clause["risk_assessment"].risk_score if v1_clause.get("risk_assessment") else None
        v1_risk_level = None
        if v1_risk is not None:
            v1_risk_level = {0.25: "low", 0.5: "medium", 0.75: "high", 1.0: "critical"}.get(v1_risk, "unknown")

        v2_risk_level = None
        if v2_clause and pair["status"] in ("modified", "unchanged"):
            clause_obj = v2_clause["clause_obj"]
            if clause_obj.risk_assessment:
                v2_risk_level = clause_obj.risk_assessment.risk_score
                v2_risk_level = {0.25: "low", 0.5: "medium", 0.75: "high", 1.0: "critical"}.get(v2_risk_level, "unknown")

        regression = False
        improvement = False
        if v1_risk_level and v2_risk_level and v1_risk_level in risk_rank and v2_risk_level in risk_rank:
            if risk_rank[v2_risk_level] > risk_rank[v1_risk_level]:
                regression = True
            elif risk_rank[v2_risk_level] < risk_rank[v1_risk_level]:
                improvement = True

        result = {
            "status": pair["status"],
            "similarity": round(pair["similarity"], 2),
            "v1_text_preview": v1_clause["text"][:150],
            "v2_text_preview": v2_clause["text"][:150] if v2_clause else None,
            "v1_risk_level": v1_risk_level,
            "v2_risk_level": v2_risk_level,
            "regression": regression,
            "improvement": improvement,
        }
        comparison_results.append(result)

        if regression:
            regressions.append(result)
        if improvement:
            improvements.append(result)

    for added in diff_result["added"]:
        comparison_results.append({
            "status": "added",
            "v1_text_preview": None,
            "v2_text_preview": added["text"][:150],
        })

    if regressions:
        log = AuditLog(
            actor="system",
            action="risk_regression_detected",
            entity_type="contract",
            entity_id=v2_contract.id,
            details=f"{len(regressions)} clause(s) regressed in risk level compared to v{v1_contract.version}",
        )
        db.add(log)
        db.commit()

    summary = (
        f"Version {v1_contract.version} had clauses analyzed. "
        f"Version {v2_contract.version} shows {diff_result['modified_count']} modified, "
        f"{diff_result['added_count']} added, {diff_result['removed_count']} removed clauses. "
        f"{len(regressions)} risk regression(s) detected, {len(improvements)} improvement(s)."
    )

    return {
        "v1_contract_id": str(v1_contract.id),
        "v2_contract_id": str(v2_contract.id),
        "summary": summary,
        "regressions_detected": len(regressions) > 0,
        "regressions": regressions,
        "improvements": improvements,
        "full_comparison": comparison_results,
    }


@app.post("/signup")
def signup(email: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(400, "Email already registered")
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created", "user_id": str(user.id)}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/contracts/{contract_id}/pending-review")
def get_pending_review(contract_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(404, "Contract not found")
    pending = []
    for clause in contract.clauses:
        if clause.risk_assessment and clause.risk_assessment.reviewed_by_human:
            pending.append({
                "clause_id": str(clause.id),
                "text": clause.text[:150],
                "risk_score": clause.risk_assessment.risk_score,
                "rationale": clause.risk_assessment.rationale,
            })
    return {"contract_id": str(contract.id), "pending_review_count": len(pending), "clauses": pending}


def redact_pii(text: str) -> str:
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED-SSN]', text)
    text = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '[REDACTED-EMAIL]', text)
    text = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[REDACTED-PHONE]', text)
    return text

