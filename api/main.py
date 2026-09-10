import os
import hashlib
from uuid import UUID
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, get_engine
from models import Base, Contract, Clause, RiskAssessment, RedlineSuggestion, AuditLog
from clause_splitter import  split_into_clauses
from risk_agent import  analyze_clause_risk,apply_guardrails,save_risk_assessment

app = FastAPI(title="Contract Risk Analyzer & Negotiator")

UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)



@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=get_engine())


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/contracts/upload")
def upload_contract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(400, "Only PDF or TXT contracts are supported")

    contents = file.file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")

    file_hash = hashlib.sha256(contents).hexdigest()

    existing = db.query(Contract).filter(Contract.file_hash == file_hash).first()
    if existing:
        return {"message": "Contract already uploaded", "contract_id": str(existing.id)}

    save_path = os.path.join(UPLOAD_DIR, f"{file_hash}_{file.filename}")
    with open(save_path, "wb") as f:
        f.write(contents)

    contract = Contract(filename=file.filename, file_hash=file_hash, status="uploaded")
    db.add(contract)
    db.commit()
    db.refresh(contract)

    log = AuditLog(
        actor="system",
        action="uploaded_contract",
        entity_type="contract",
        entity_id=contract.id,
        details=file.filename,
    )
    db.add(log)
    db.commit()

    return {"message": "Uploaded", "contract_id": str(contract.id), "status": contract.status}


@app.get("/contracts")
def list_contracts(db: Session = Depends(get_db)):
    contracts = db.query(Contract).all()
    return [
        {"id": str(c.id), "filename": c.filename, "status": c.status, "created_at": c.created_at}
        for c in contracts
    ]


@app.get("/contracts/{contract_id}/clauses")
def get_clauses(contract_id: UUID, db: Session = Depends(get_db)):
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
def analyze_contract(contract_id: UUID, db: Session = Depends(get_db)):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(404, "Contract not found")

    file_path = None
    for filename in os.listdir(UPLOAD_DIR):
        if filename.startswith(contract.file_hash):
            file_path = os.path.join(UPLOAD_DIR, filename)
            break

    if not file_path:
        raise HTTPException(404, "Uploaded file not found on disk")

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text_content = f.read()

    raw_clauses = split_into_clauses(text_content)

    results = []
    for clause_text in raw_clauses:
        clause = Clause(contract_id=contract.id, text=clause_text)
        db.add(clause)
        db.commit()
        db.refresh(clause)

        try:
            assessment = analyze_clause_risk(clause_text)
            guardrail_result = apply_guardrails(assessment)
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