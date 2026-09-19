# ContractGuard AI

### Agentic Contract Intelligence for Risk Detection, Evidence Retrieval, Version Regression & Controlled Redlining

ContractGuard AI is a production-minded AI system for analyzing contracts at the **clause level**, retrieving supporting precedent, assessing risk, detecting risk regressions between contract versions, and generating controlled redline suggestions for human review.

The project is deliberately designed as more than an LLM wrapper or basic RAG chatbot.

It combines:

* Agentic AI with **LangGraph**
* Hybrid RAG using **dense + keyword retrieval**
* Clause-level risk intelligence
* Structured LLM outputs with **Pydantic validation**
* Contract version comparison and regression detection
* Controlled redline generation
* AI-specific security guardrails
* JWT authentication and contract-level authorization
* Human-in-the-loop review
* Audit logging and reproducibility
* LangSmith runtime observability
* Automated evaluation and security testing
* Dockerized deployment and CI validation

> **Core engineering principle:**
> **The LLM is a component of the system — not the system itself.**

---

# Executive Summary

ContractGuard AI addresses a practical enterprise problem:

> **How can AI assist with contract review while keeping evidence, security, validation, human oversight, and system behavior under engineering control?**

The system processes a contract through a controlled pipeline:

```text
Contract Upload
      │
      ▼
Input Validation
      │
      ▼
Document Ingestion
      │
      ▼
Clause Extraction
      │
      ▼
Hybrid Retrieval
(Dense + Keyword)
      │
      ▼
LangGraph Workflow
      │
      ├── Retrieve Precedent
      ├── Score Risk
      ├── Check Guardrails
      └── Generate Redline
      │
      ▼
Human Review
      │
      ▼
Persistence + Audit
      │
      ▼
Observability + Evaluation
```

The objective is not to replace legal professionals.

The objective is to provide a **controlled AI-assisted first-pass analysis system** where recommendations are evidence-backed, structured, reviewable, traceable, and measurable.

---

# System Architecture

```text
                         ┌─────────────────────┐
                         │   Streamlit UI      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      FastAPI        │
                         │ Auth / API / AuthZ  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌─────────────────────────────┐
                    │       LangGraph Agent       │
                    │                             │
                    │  ┌──────────┐               │
                    │  │ Retrieve │               │
                    │  └────┬─────┘               │
                    │       ▼                     │
                    │  ┌────────────┐             │
                    │  │ Score Risk │             │
                    │  └─────┬──────┘             │
                    │        ▼                    │
                    │  ┌───────────────┐          │
                    │  │  Guardrails   │          │
                    │  └───────┬───────┘          │
                    │          ▼                  │
                    │  ┌───────────────┐          │
                    │  │ Generate      │          │
                    │  │ Redline       │          │
                    │  └───────────────┘          │
                    └──────────────┬──────────────┘
                                   │
             ┌─────────────────────┼──────────────────────┐
             ▼                     ▼                      ▼
     ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
     │ PostgreSQL   │      │ Gemini +     │      │  LangSmith   │
     │ + pgvector   │      │ Pydantic     │      │ Observability│
     └──────────────┘      └──────────────┘      └──────────────┘
             │
             ▼
     Contracts / Clauses
     Risk Assessments
     Redlines / Reviews
     Audit Events
```

### Architectural control flow

```text
Untrusted Input
      ↓
Validation
      ↓
Retrieval
      ↓
LLM Reasoning
      ↓
Structured Output
      ↓
Validation
      ↓
Security Controls
      ↓
Business Logic
      ↓
Human Review
      ↓
Persistence
      ↓
Auditability
      ↓
Observability
```

This separation is intentional: model output does not directly become trusted application state.

---

# Why This Project?

A basic RAG application can answer questions over documents.

Contract analysis requires considerably more system behavior.

The system needs to answer questions such as:

* What clauses are present?
* Which clauses are potentially risky?
* What evidence supports that assessment?
* What changed between contract versions?
* Did a change introduce a potential risk regression?
* Should a redline be proposed?
* Should the result require human review?
* Can the system prevent malicious instructions embedded in documents?
* Can one user access another user's contract?
* Can an engineer trace how an analysis was produced?
* Can the system measure where its AI decisions are failing?

That shifts the engineering problem from:

```text
Document → LLM → Answer
```

to:

```text
Secure Application
        +
Retrieval
        +
Agent Orchestration
        +
Structured AI
        +
Validation
        +
Business Logic
        +
Human Oversight
        +
Auditability
        +
Observability
        +
Evaluation
```

---

# Agentic Workflow

ContractGuard uses LangGraph to explicitly model the analysis workflow.

```text
Contract
   │
   ▼
┌──────────┐
│ Retrieve │
└────┬─────┘
     ▼
┌────────────┐
│ Score Risk │
└─────┬──────┘
      ▼
┌───────────────┐
│ Check         │
│ Guardrails    │
└───────┬───────┘
        ▼
┌─────────────────┐
│ Generate        │
│ Controlled      │
│ Redline         │
└────────┬────────┘
         ▼
   Human Review
```

### `retrieve`

Retrieves relevant precedent clauses using hybrid retrieval.

### `score_risk`

Uses the LLM to produce structured clause-level risk assessments.

### `check_guardrails`

Validates AI output and applies security and confidence controls before downstream actions.

### `generate_redline`

Produces controlled revision suggestions where applicable rather than allowing unrestricted document rewriting.

### Human Review

The AI recommendation is persisted as a recommendation requiring review rather than silently becoming an authoritative decision.

> **The AI proposes. The reviewer decides.**

---

# Hybrid RAG

ContractGuard does not rely exclusively on semantic similarity.

The retrieval layer combines:

```text
Dense Vector Retrieval
          +
Keyword / BM25-style Retrieval
          ↓
     Hybrid Ranking
          ↓
Relevant Precedent
          ↓
Risk Analysis
```

The precedent library currently contains **419 clause examples** across areas including:

* Employment
* Commercial / MSA
* Confidentiality
* Settlement and litigation-related agreements

The purpose of retrieval is not simply to place more text into the model context.

It provides **inspectable supporting evidence** for the risk assessment.

This makes the reasoning process easier to review:

```text
Contract Clause
      ↓
Retrieved Evidence
      ↓
Risk Assessment
      ↓
Reasoning
      ↓
Confidence
```

---

# Clause-Level Risk Intelligence

Risk is evaluated at the clause level rather than treating the entire contract as one document.

Each assessment can capture:

| Field             | Purpose                       |
| ----------------- | ----------------------------- |
| Risk Level        | Categorizes assessed risk     |
| Reasoning         | Explains the assessment       |
| Confidence        | Indicates model confidence    |
| Precedent         | Supporting retrieved evidence |
| Review Status     | Tracks human review           |
| Contract / Clause | Maintains traceability        |

LLM output follows a controlled path:

```text
Gemini
   ↓
Structured Output
   ↓
Pydantic Validation
   ↓
Application Logic
   ↓
Database
```

This reduces dependence on fragile free-form model responses.

---

# Version Intelligence & Risk Regression

Contracts evolve.

A useful contract intelligence system therefore needs to understand not only:

> “What is risky?”

but also:

> **“What changed, and did the change increase the assessed risk?”**

ContractGuard compares contract versions at the clause level.

```text
Version 1
   │
   ▼
Clause Matching
   │
   ▼
Version 2
   │
   ▼
Similarity Analysis
   │
   ├── Unchanged
   ├── Modified
   └── Potentially New / Removed
          │
          ▼
     Risk Comparison
          │
          ▼
   Regression Detection
```

The comparison layer uses similarity-based clause matching to identify meaningful changes.

This supports detection of:

* unchanged clauses
* modified clauses
* changed risk levels
* potential risk regressions

The goal is to make version review more targeted rather than forcing a reviewer to manually compare every clause.

---

# Controlled Redlining

Redline generation is intentionally downstream of risk analysis and guardrails.

```text
Risk Detection
      ↓
Supporting Evidence
      ↓
Suggested Revision
      ↓
Validation
      ↓
Human Review
      ↓
Decision
```

The system does not treat generated text as an automatic legal action.

This creates a clear boundary between:

**AI-generated recommendation**

and

**human-approved decision.**

---

# Security & AI Guardrails

Contract documents are treated as **untrusted input**.

A document can contain text that attempts to manipulate the model, including instructions embedded inside otherwise legitimate contract content.

ContractGuard therefore considers both traditional application security and AI-specific threats.

### Threat categories

* Prompt injection
* Malicious embedded instructions
* Unexpected document content
* Oversized files
* Manipulated model-facing text
* Invalid model output
* Unauthorized contract access
* Cross-contract data exposure
* PII exposure
* Dependency vulnerabilities

### Guardrail layers

```text
File Validation
      ↓
Prompt Injection Detection
      ↓
LLM Analysis
      ↓
Output Validation
      ↓
Confidence / Scope Controls
      ↓
Business Logic
      ↓
Human Review
```

The design principle is simple:

> **Never assume that either user-provided documents or LLM output are inherently trustworthy.**

---

# Security Testing

Security was tested as part of the application rather than treated as a documentation checkbox.

Current testing evidence includes:

| Security Area            |                      Result |
| ------------------------ | --------------------------: |
| Guardrail tests          |           **9 / 9 passing** |
| Prompt-injection tests   |           **5 / 5 blocked** |
| Red-team scenarios       |                **9 tested** |
| User ownership isolation | **Verified with two users** |
| Dependency auditing      |    **pip-audit integrated** |

During development, dependency auditing identified **36 dependency vulnerabilities**. The critical issue identified during the audit was addressed, while dependency security remains an ongoing maintenance concern.

The project does not claim that these tests prove complete security.

They demonstrate that security controls were actively tested against defined failure scenarios.

---

# Authentication & Authorization

JWT authentication protects API access.

However, authentication alone is insufficient for a multi-user application.

ContractGuard also enforces **resource-level ownership checks**.

Example verification:

```text
User A
 ├── Contract A ✓
 └── Contract B ✗

User B
 ├── Contract B ✓
 └── Contract A ✗
```

This prevents authenticated users from simply accessing resources belonging to another user.

---

# Human-in-the-Loop

Contract analysis is designed around human oversight.

```text
AI Analysis
     ↓
Evidence + Confidence
     ↓
Risk Recommendation
     ↓
Human Review
     ↓
Approved / Rejected / Reviewed
```

Review status is persisted as part of the analysis lifecycle.

This makes human review an **architectural control**, not merely a UI feature.

---

# Auditability & Reproducibility

AI systems become difficult to debug when their decisions cannot be reconstructed.

ContractGuard records information such as:

* Contract association
* Analysis events
* Review events
* Risk assessments
* Model version
* Prompt version
* Audit events
* Review state

Conceptually:

```text
Input
  ↓
Retrieval
  ↓
Model
  ↓
Validation
  ↓
Decision
  ↓
Audit Record
```

The objective is to make important system actions traceable after execution.

---

# Observability with LangSmith

LangSmith is used to inspect the actual runtime behavior of the LangGraph workflow.

This became particularly important during development.

A key production-minded lesson from the project was:

> **Architecture written in code does not guarantee architecture executed at runtime.**

## Engineering Investigation: Finding an Orchestration Bug

The `/analyze` endpoint was originally expected to execute:

```text
API
 ↓
LangGraph
 ↓
Retrieve
 ↓
Score Risk
 ↓
Guardrails
 ↓
Redline
```

However, runtime investigation revealed that the API was directly calling the risk-scoring function:

```text
API
 ↓
score_risk()
```

This meant the intended orchestration graph was being bypassed.

The issue was discovered by inspecting LangSmith traces and noticing that the expected graph execution was missing.

The endpoint was then corrected to invoke the LangGraph workflow:


After the fix, the complete workflow appeared in LangSmith.

### Why this matters

This was not a theoretical architecture exercise.

It was a real runtime discrepancy between:

```text
What the code was supposed to do
```

and

```text
What the application was actually doing
```

Observability made that discrepancy visible.

### Observed node timings

| LangGraph Node     | Observed Time |
| ------------------ | ------------: |
| `retrieve`         |        2.34 s |
| `score_risk`       |       58.59 s |
| `check_guardrails` |        0.50 s |
| `generate_redline` |        0.36 s |

The trace also exposed `score_risk` as the dominant latency contributor.

That creates concrete optimization targets:

* reduce prompt size
* reduce retrieved context
* optimize retrieval
* cache reusable context
* evaluate faster models
* introduce asynchronous/background processing where appropriate

This is one of the most useful engineering outcomes of the project because the system now provides evidence about **where it spends time**, rather than relying on assumptions.

---

# Evaluation

The project includes a labeled evaluation set of **17 examples**.

Current results:

| Metric                   |     Result |
| ------------------------ | ---------: |
| Accuracy                 | **52.94%** |
| Groundedness             | **94.12%** |
| Hallucination Rate       |  **5.88%** |
| Escalation Rate          | **47.06%** |
| Observed False Negatives |      **0** |

### Interpretation

The strongest signal in the current evaluation is groundedness.

The main weakness observed in this small dataset is **risk-level calibration**.

Incorrect predictions were frequently one risk level higher rather than completely missing the clause's potential risk.

This distinction matters.

A system can be highly grounded while still requiring improvement in classification/calibration.

### Important limitation

The evaluation set contains only 17 labeled examples.

Therefore, these metrics should **not** be interpreted as production-level model performance.

A larger professionally labeled dataset is required to make stronger claims about:

* generalization
* precision
* recall
* calibration
* domain-specific performance
* regression detection accuracy

The evaluation framework is intended to make those improvements measurable over time.

---

# Reliability Engineering

The project includes several reliability-oriented controls.

### Idempotent analysis

Repeated analysis requests are handled without blindly creating duplicate analysis state.

### Health checks

Database and API health are explicitly checked.

### Structured logging

Important runtime events are logged in structured form for debugging and operational visibility.

### CI evaluation gate

AI evaluation is incorporated into CI validation rather than being performed only manually.

### Container validation

Docker builds are validated as part of the development workflow.

---

# Data Model

The core relationships are structured around contract ownership and analysis traceability.

```text
User
 │
 └── Contract
      │
      ├── Clause
      │    ├── RiskAssessment
      │    └── RedlineSuggestion
      │
      └── AuditLog
```

Database migrations are managed with Alembic.

PostgreSQL provides persistent application state, while pgvector supports vector-based retrieval.

---

# API Architecture

The FastAPI layer exposes protected operations around the contract lifecycle.

### Authentication

```text
POST /auth/signup
POST /auth/login
```

### Contracts

```text
POST /contracts/upload
GET  /contracts
GET  /contracts/{id}
POST /contracts/{id}/analyze
```

### Analysis

```text
GET  /contracts/{id}/analysis
POST /contracts/{id}/review
POST /contracts/{id}/compare
```

### Audit

```text
GET /contracts/{id}/audit
```

### System

```text
GET /health
```

Protected operations enforce authentication and resource ownership.

---

# Technology Stack

| Layer               | Technology                   |
| ------------------- | ---------------------------- |
| Language            | Python 3.11                  |
| API                 | FastAPI                      |
| ORM                 | SQLAlchemy                   |
| Validation          | Pydantic                     |
| Database            | PostgreSQL                   |
| Vector Search       | pgvector                     |
| Migrations          | Alembic                      |
| Agent Orchestration | LangGraph                    |
| LLM Integration     | Gemini                       |
| Retrieval           | Dense + Keyword / BM25-style |
| Frontend            | Streamlit                    |
| Authentication      | JWT                          |
| Observability       | LangSmith                    |
| Logging             | Structured Logging           |
| Containers          | Docker / Docker Compose      |
| CI/CD               | Automated CI                 |
| Security Audit      | pip-audit                    |

---

# Docker & Reproducible Environment

The entire application is containerized to reduce environment-specific differences and provide a reproducible runtime.

Start the application with:

```bash
docker compose up --build
```

The Docker Compose environment contains:

```text
Docker Compose
      │
      ├── ContractGuard API
      │
      ├── PostgreSQL
      │
      └── Streamlit Frontend
```

Published Docker image:

```text
anisakhan4/contractguard-ai:latest
```

Containerization provides a consistent development/runtime environment and creates a cleaner path toward cloud deployment.

---

# Testing Strategy

Testing covers more than API endpoints.

### Functional Testing

* Contract ingestion
* Clause extraction
* Risk analysis
* Version comparison
* Redline generation

### AI Evaluation

* Labeled examples
* Accuracy
* Groundedness
* Hallucination rate
* Escalation behavior
* False-negative tracking

### Security Testing

* Prompt injection
* JWT tampering
* Authentication failures
* Authorization failures
* Cross-contract access
* Malicious files
* Oversized inputs
* PII handling
* Output manipulation

### Reliability Testing

* Duplicate analysis requests
* Database health
* API health
* Container builds

### Observability Testing

* LangGraph execution
* Node-level latency
* Model execution
* Audit events

---

# What Makes This Different From a Basic RAG Chatbot?

A basic RAG application often looks like:

```text
Document
   ↓
Embedding
   ↓
Vector Search
   ↓
LLM
   ↓
Answer
```

ContractGuard is structured more like an AI application platform:

```text
Authentication
      ↓
Input Validation
      ↓
Document Ingestion
      ↓
Clause Extraction
      ↓
Hybrid Retrieval
      ↓
Agentic Risk Analysis
      ↓
Structured Output
      ↓
Guardrails
      ↓
Version Intelligence
      ↓
Controlled Redlining
      ↓
Human Review
      ↓
Auditability
      ↓
Observability
      ↓
Evaluation
```

The differentiator is not simply the presence of an LLM.

It is the engineering surrounding the LLM.

---

# Key Engineering Lessons

### 1. A graph in source code does not mean the graph is executing

Runtime traces are necessary to verify actual orchestration.

### 2. LLM output is not trusted application data

Structured schemas and validation should exist between model output and business logic.

### 3. Retrieval quality affects downstream reasoning

Better retrieval is not merely a search improvement; it changes the evidence available to the reasoning layer.

### 4. AI security requires AI-specific controls

Traditional API authentication does not protect against prompt injection or malicious model-facing content.

### 5. Human-in-the-loop can be an architectural control

Human review provides a boundary before high-impact recommendations become decisions.

### 6. Observability changes how AI systems are engineered

Tracing exposes runtime behavior, latency bottlenecks, failed paths, and unexpected execution.

### 7. Evaluation should expose weaknesses

A useful evaluation system should reveal where the model is wrong, not simply produce a score.

### 8. Runtime behavior matters as much as architecture

The `/analyze` orchestration issue demonstrated why implementation claims need runtime verification.

---

# Current Limitations

ContractGuard AI is an engineering prototype and **not a production legal decision system**.

Current limitations include:

* Small labeled evaluation dataset
* Risk-level calibration still needs improvement
* LLM latency, particularly during risk scoring
* Larger contract workloads require additional performance testing
* Larger professionally labeled datasets are required
* Production-scale load testing is still needed
* Cloud infrastructure hardening remains future work
* Enterprise identity integration is not yet implemented
* Organization-specific compliance requirements would require additional controls

These limitations are intentionally documented rather than hidden from the project.

---

# Production Roadmap

## Model & Evaluation

* Expand professionally labeled datasets
* Add category-specific evaluation
* Improve calibration
* Track precision / recall
* Add automated evaluation regression detection
* Evaluate multiple models

## Performance

* Optimize prompts
* Reduce retrieved context
* Improve retrieval efficiency
* Introduce caching
* Benchmark faster models
* Move long-running analysis to background workers

## Infrastructure

* Cloud deployment
* Horizontal scaling
* Queue-based processing
* Rate limiting
* Load testing
* Production database configuration

## Enterprise Security

* Fine-grained RBAC
* Enterprise identity provider integration
* Encryption at rest and in transit
* Secret-management infrastructure
* Retention policies
* Multi-tenant isolation
* Organization-level security policies

## Observability

* Operational dashboards
* Latency monitoring
* Token and cost monitoring
* Model-quality monitoring
* Evaluation regression alerts
* Production drift monitoring

---

# Demo Flow

A complete demonstration can follow this sequence:

```text
1. Login
      ↓
2. Upload Contract
      ↓
3. Ingestion
      ↓
4. Clause Extraction
      ↓
5. Hybrid Retrieval
      ↓
6. AI Risk Analysis
      ↓
7. Guardrail Validation
      ↓
8. Evidence Review
      ↓
9. Upload / Compare Version
      ↓
10. Detect Risk Regression
      ↓
11. Generate Controlled Redline
      ↓
12. Human Review
      ↓
13. Audit Events
      ↓
14. Inspect LangSmith Trace
```

For demonstrations where fresh model execution is unavailable because of model quota or provider limitations, previously processed analysis results can be used to demonstrate the application's downstream capabilities without falsely implying a new model invocation.

---

# Project Metrics

| Area                          |           Current Evidence |
| ----------------------------- | -------------------------: |
| Precedent clauses             |                    **419** |
| Labeled evaluation examples   |                     **17** |
| Accuracy                      |                 **52.94%** |
| Groundedness                  |                 **94.12%** |
| Hallucination rate            |                  **5.88%** |
| Observed false negatives      |                      **0** |
| Guardrail tests               |          **9 / 9 passing** |
| Prompt-injection tests        |          **5 / 5 blocked** |
| Red-team scenarios            |               **9 tested** |
| Ownership isolation           |        **2-user verified** |
| LangGraph nodes traced        |                      **4** |
| Largest observed node latency | **58.59 s (`score_risk`)** |

These numbers describe the current development/evaluation environment and should not be interpreted as production guarantees.

---

# Final Perspective

ContractGuard AI started with a simple question:

> **Can AI help analyze contracts?**

The engineering question became more interesting:

> **How do you build an AI system whose recommendations can be supported by evidence, validated, secured, reviewed, audited, traced, measured, and improved?**

That led to an architecture combining:

**Agentic AI + LangGraph + Hybrid RAG + Structured Outputs + Security Guardrails + Version Intelligence + Human-in-the-Loop + Auditability + Observability + Evaluation**

The project demonstrates not only how to build an AI workflow, but how to **engineer around the failure modes of AI systems**.

The model itself is only one component of the system.

> **The AI recommends.
> The evidence supports.
> The guardrails constrain.
> The human reviews.
> The system records.
> The engineer can trace what happened.**

---

# Built With

**Python · FastAPI · LangGraph · LangChain · Gemini · PostgreSQL · pgvector · SQLAlchemy · Pydantic · Streamlit · Docker · Docker Compose · LangSmith · JWT · Alembic**

---

# Author

**Anisa Nabi**

Agentic AI Engineer · AI Automation · LLM Applications · RAG · Multi-Agent Systems

GitHub: `anisakhan5554-source`

---
