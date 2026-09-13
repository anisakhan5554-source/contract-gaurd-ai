import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text, Enum, Integer
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()

class ClauseType(str, enum.Enum):
    indemnification = "indemnification"
    termination = "termination"
    liability = "liability"
    confidentiality = "confidentiality"
    payment = "payment"
    other = "other"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)


class Contract(Base):
    __tablename__ = "contracts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String, nullable=False)
    file_hash = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default="uploaded")
    version = Column(Integer, default=1)
    parent_contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    clauses = relationship("Clause", back_populates="contract")


class Clause(Base):
    __tablename__ = "clauses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = Column(UUID(as_uuid=True), ForeignKey("contracts.id"), nullable=False)
    text = Column(Text, nullable=False)
    clause_type = Column(Enum(ClauseType), default=ClauseType.other)
    embedding = Column(Vector(3072), nullable=True)

    contract = relationship("Contract", back_populates="clauses")
    risk_assessment = relationship("RiskAssessment", back_populates="clause", uselist=False)


class PrecedentClause(Base):
    __tablename__ = "precedent_clauses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source = Column(String)
    text = Column(Text, nullable=False)
    clause_type = Column(Enum(ClauseType), default=ClauseType.other)
    embedding = Column(Vector(3072), nullable=True)


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clause_id = Column(UUID(as_uuid=True), ForeignKey("clauses.id"), unique=True)
    risk_score = Column(Float)
    rationale = Column(Text)
    confidence = Column(Float)
    precedent_clause_id = Column(UUID(as_uuid=True), ForeignKey("precedent_clauses.id"), nullable=True)
    reviewed_by_human = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    clause = relationship("Clause", back_populates="risk_assessment")


class RedlineSuggestion(Base):
    __tablename__ = "redline_suggestions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clause_id = Column(UUID(as_uuid=True), ForeignKey("clauses.id"))
    suggested_text = Column(Text)
    agent_version = Column(String, default="v1")
    accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor = Column(String)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(UUID(as_uuid=True))
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

