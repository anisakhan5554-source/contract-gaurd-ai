# Contract Risk Analyzer

### Agentic Contract Intelligence for Risk Detection, Precedent Retrieval, Version Regression & Controlled Redlining

> **AI-assisted contract intelligence for identifying contractual risk, retrieving supporting precedent, detecting version regressions, and generating controlled redline suggestions — with guardrails, human oversight, auditability, and reproducible AI execution.**

---

## Overview

**Contract Risk Analyzer** is an enterprise-oriented Agentic AI system designed to help teams analyze contracts more systematically and transparently.

Instead of treating an LLM as an isolated chatbot, the system combines:

* **Agentic orchestration with LangGraph**
* **Hybrid RAG using dense vector + keyword retrieval**
* **Structured risk analysis with Pydantic**
* **Contract version comparison and risk regression detection**
* **AI-generated redline suggestions**
* **Human-in-the-loop review**
* **Prompt-injection and input-security guardrails**
* **JWT authentication and ownership isolation**
* **Audit logging and reproducibility tracking**
* **LangSmith observability**
* **Automated evaluation and red-team security testing**
* **Dockerized deployment and CI validation**

The core design principle is:

> **AI should assist high-stakes contract decisions with evidence, controls, traceability, and human oversight — not operate as an unchecked black box.**

This project is intended as an **AI engineering / enterprise AI system**, not as legal advice or a replacement for qualified legal professionals.

---

# At a Glance

| Capability                 | Evidence                                                                 |
| -------------------------- | ------------------------------------------------------------------------ |
| Agentic orchestration      | LangGraph StateGraph with retrieval → scoring → guardrail → redline flow |
| Hybrid RAG                 | Dense vector retrieval + keyword/BM25-style retrieval                    |
| Precedent corpus           | **419 precedent clauses** across 4 contract niches                       |
| Structured AI output       | Gemini + Pydantic validation                                             |
| Version intelligence       | Clause-level diff + risk regression detection                            |
| Redlining                  | AI-generated controlled rewrite suggestions                              |
| Human oversight            | Human review / HITL workflow                                             |
| Guardrails                 | **5 guardrail categories**                                               |
| Guardrail tests            | **9/9 pytest tests passing**                                             |
| Prompt-injection defense   | **5/5 tested injection attempts blocked**                                |
| Evaluation set             | **17 labeled examples** in expanded evaluation                           |
| Expanded measured accuracy | **52.94%**                                                               |
| False negatives            | **0 observed in the evaluated set**                                      |
| Observability              | LangSmith traces + structured JSON logs                                  |
| Reproducibility            | Model/prompt version recorded per assessment                             |
| Authentication             | JWT + user ownership isolation                                           |
| Security testing           | **9 red-team security scenarios**                                        |
| Dependency audit           | `pip-audit` surfaced **36 CVEs**; critical issue addressed               |
| Containerization           | Docker + Docker Compose                                                  |
| Docker registry            | **Docker Hub image published**                                           |
| CI/CD                      | Docker build + AI evaluation gate                                        |

---

# Why This Project Exists

Contract review contains several recurring engineering problems:

1. Important clauses can be buried inside long documents.
2. Risk assessment often depends on contractual context and precedent.
3. Contract revisions can introduce subtle risk regressions.
4. LLM outputs can be inconsistent or insufficiently grounded.
5. Sensitive contract data requires authentication and isolation.
6. High-impact AI decisions require human oversight.
7. AI systems need observability and reproducibility, not just generated text.

This project addresses these problems as an **AI engineering system** rather than simply adding an LLM to a document-upload application.

---

# System Architecture

```text
                         ┌──────────────────────┐
                         │      Streamlit UI    │
                         │ Login / Review /     │
                         │ Compare / Audit      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FastAPI API     │
                         │ Auth / Contracts /   │
                         │ Analysis / HITL       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │       LangGraph Workflow     │
                    │                              │
                    │ Retrieve → Score → Guardrail │
                    │              ↓               │
                    │           Redline            │
                    └──────────────┬───────────────┘
                                   │
             ┌─────────────────────┼─────────────────────┐
             ▼                     ▼                     ▼
      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
      │ Hybrid RAG   │      │ Risk Agent   │      │ Redline Agent│
      │ Vector +     │      │ Gemini +     │      │ Controlled   │
      │ Keyword      │      │ Pydantic     │      │ Rewrite      │
      └──────┬───────┘      └──────┬───────┘      └──────────────┘
             │                     │
             ▼                     ▼
      ┌─────────────────────────────────────┐
      │ PostgreSQL + pgvector               │
      │ Contracts / Clauses / Precedents /  │
      │ Risks / Redlines / Audit Logs / Users│
      └─────────────────────────────────────┘

             ┌─────────────────────────────┐
             │ Security & Control Layer   │
             │                             │
             │ Input Validation            │
             │ Prompt Injection Detection  │
             │ Confidence Guardrails        │
             │ Risk-Level Guardrails        │
             │ Scope Guardrails             │
             │ JWT / Ownership Isolation   │
             │ Human Review                 │
             └─────────────────────────────┘

                    ┌─────────────────┐
                    │   Observability │
                    │   LangSmith     │
                    │   JSON Logs     │
                    │   Cost / Tokens │
                    └─────────────────┘
```

---

# Core AI Workflow

The system uses an actual **LangGraph StateGraph**, rather than a single sequential LLM call.

```text
Contract
   │
   ▼
Document Ingestion
   │
   ▼
Clause Extraction
   │
   ▼
Hybrid Precedent Retrieval
   │
   ▼
Risk Analysis Agent
   │
   ▼
Structured Validation
   │
   ▼
Guardrail Checks
   │
   ├──────────► Escalate / Human Review
   │
   ▼
Redline Agent
   │
   ▼
Persist Results
   │
   ▼
Audit + Observability
```

This separation allows individual stages to be tested, observed, and controlled independently.

---

# 1. Contract Intelligence

The ingestion pipeline accepts contract documents and extracts individual clauses for downstream analysis.

### Capabilities

* Contract upload
* File validation
* Document processing
* Clause extraction
* Clause persistence
* Contract/version tracking
* Protection against invalid or malicious input files

A previous clause-extraction issue caused valid clauses to be filtered too aggressively. The filtering logic was corrected and subsequently verified against real contract documents.

---

# 2. Hybrid RAG / Precedent Engine

The system does not rely exclusively on semantic similarity.

It combines:

```text
                 Contract Clause
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
      Dense Retrieval      Keyword Retrieval
        pgvector             BM25-style
             │                   │
             └─────────┬─────────┘
                       ▼
                Hybrid Results
                       │
                       ▼
              Relevant Precedents
```

### Precedent Corpus

The current corpus contains **419 precedent clauses** across four practical contract niches:

* Employment
* Master Services / Commercial Agreements
* Confidentiality
* Settlement / Litigation

The corpus includes clauses derived from real contractual documents, including public SEC/EDGAR filings.

### Why Hybrid Retrieval?

Dense retrieval is useful for semantic similarity, while keyword-based retrieval can preserve important contractual terminology and exact concepts.

Combining both approaches provides a stronger evidence-retrieval layer than relying on one retrieval method alone.

---

# 3. Risk Analysis Agent

The risk analysis layer uses an LLM with structured output validation.

### Flow

```text
Clause
  │
  ▼
Relevant Precedents
  │
  ▼
LLM Risk Analysis
  │
  ▼
Pydantic Structured Output
  │
  ▼
Confidence / Risk Guardrails
  │
  ▼
Persisted Assessment
```

The system evaluates contractual clauses and produces structured assessments rather than relying on free-form text alone.

The implementation includes:

* Structured response validation
* Retry handling
* Confidence tracking
* Risk-level validation
* Evidence-aware analysis
* Persistence of assessment results

---

# 4. Evaluation Results

Evaluation is treated as an engineering requirement rather than an afterthought.

## Expanded Evaluation

The later evaluation used a labeled set of **17 examples**.

| Metric                   | Measured Result |
| ------------------------ | --------------: |
| Accuracy                 |      **52.94%** |
| Hallucination rate       |       **5.88%** |
| Escalation rate          |      **47.06%** |
| Groundedness             |      **94.12%** |
| Observed false negatives |           **0** |

The evaluation showed a consistent calibration pattern: incorrect predictions tended to be **one risk level higher than the labeled result**, rather than under-flagging the clause.

### Important Limitation

This is a **small evaluation set** and should not be interpreted as production-level accuracy.

Additional repeated calibration experiments were constrained by the Gemini free-tier request quota. The quota limitation is treated as an experimentation constraint; it is **not** presented as an explanation for the measured 52.94% result.

The evaluation framework is designed so that a larger labeled dataset can be introduced as the system matures.

---

# 5. Version Intelligence

Contracts evolve.

A clause that was previously acceptable may become materially riskier after a revision.

The system therefore supports:

* Contract version detection
* Clause-level comparison
* Modified clause identification
* Risk regression detection
* Version-to-version review

### Example

```text
Version 1
Compensation: $70,000
Risk: Medium

        ↓ Contract Revision

Version 2
Compensation: $75,000
Risk: High

        ↓

Risk Regression Detected
```

The implementation uses clause-level comparison logic and has been verified through live API and UI testing.

---

# 6. Redline Agent

For clauses requiring intervention, the system can generate a suggested rewrite.

```text
High-Risk Clause
      │
      ▼
Risk Analysis
      │
      ▼
Evidence / Precedent
      │
      ▼
Redline Agent
      │
      ▼
Suggested Revision
      │
      ▼
Human Review
```

The redline workflow is deliberately designed as a **suggestion mechanism**, not an autonomous legal decision-maker.

A persistence issue where generated redlines were not being saved was identified and fixed. Redline records are now persisted and verified.

---

# 7. Guardrails & AI Safety

High-impact AI workflows require controls around model output.

The system implements five guardrail categories:

### 1. Confidence Guardrail

Low-confidence assessments can be routed toward additional review rather than being treated as definitive.

### 2. Risk-Level Guardrail

Risk outputs are validated against expected constraints.

### 3. Scope Guardrail

The model is constrained to the intended contract-analysis task.

### 4. Input Validation

Uploaded files are validated before entering the analysis pipeline.

### 5. Prompt-Injection Detection

The system checks document input for malicious instructions attempting to manipulate the AI workflow.

### Tested Result

**9/9 guardrail tests passed.**

Prompt-injection testing included **5/5 tested attacks being blocked**.

---

# 8. Human-in-the-Loop

The system supports explicit human review for AI-generated assessments and recommendations.

```text
AI Assessment
     │
     ▼
Guardrails
     │
     ├── Acceptable
     │      │
     │      ▼
     │   Continue
     │
     └── Requires Review
            │
            ▼
       Human Reviewer
            │
            ▼
       Review Decision
```

Human review is particularly important for high-risk contractual changes where an automated suggestion should not become an unverified business or legal decision.

---

# 9. Authentication & Data Isolation

The API uses JWT-based authentication.

Security controls include:

* User signup/login
* JWT authentication
* Protected API endpoints
* Contract ownership checks
* User-scoped contract access
* Cross-user isolation

A two-user isolation test was performed to verify that one user cannot access another user's contracts through the protected API.

Input validation was also strengthened so invalid signup values such as blank credentials are rejected through schema validation.

---

# 10. Security & Red-Team Testing

Security testing was implemented as a dedicated engineering layer.

### Tested Scenarios

* Prompt injection
* Authentication bypass
* JWT tampering
* Malicious files
* Oversized files
* Output manipulation
* Cross-contract data leakage
* PII detection/redaction
* Authorization boundaries

### Results

**9 automated security scenarios were tested.**

Prompt-injection testing blocked all five tested injection attempts.

The cross-contract leakage test also served an important purpose: it exposed a real ownership-isolation issue during development, which was subsequently addressed.

This is a key engineering principle of the project:

> **Security tests are used to discover weaknesses, not merely to demonstrate that everything passes.**

---

# 11. PII Protection

The system includes PII detection and redaction capabilities as part of the security and human-review workflow.

The goal is to reduce unnecessary exposure of sensitive information in logs, traces, and review contexts.

PII handling is treated as a security concern rather than only a UI feature.

---

# 12. Observability

The LangGraph workflow is integrated with **LangSmith** for tracing.

Tracing provides visibility into:

* Workflow execution
* Individual graph nodes
* Model calls
* Latency
* Token usage
* Execution paths
* Failures

The project initially exposed an important observability problem: the graph was not actually being invoked in the expected execution path.

That issue was identified and corrected, after which real LangSmith traces were verified.

---

# 13. Reproducibility

Each risk assessment records model and prompt version information.

This enables future investigation of questions such as:

> Why did the AI produce a different assessment after a model or prompt change?

The audit trail records relevant execution metadata rather than treating model output as an untraceable event.

---

# 14. Audit Logging

The system maintains audit information around important operations.

Audit records support:

* Contract analysis history
* Risk assessments
* Human review
* Model/prompt version information
* Relevant execution metadata

This provides a foundation for investigating how an AI-assisted decision was produced.

---

# 15. Reliability & Idempotency

The system includes reliability hardening beyond the basic happy path.

### Implemented

* API health checks
* PostgreSQL health checks
* Retry logic
* Structured model output validation
* Docker health checks
* Idempotency protection on contract analysis
* CI evaluation gate
* Failure-aware testing

The `/analyze` workflow was specifically hardened against duplicate clause creation when the same contract is analyzed repeatedly.

---

# 16. Docker & Deployment

The application is containerized using Docker.

### Docker Components

* Docker
* Docker Compose
* PostgreSQL
* API container
* Health checks
* Reproducible local environment

A clean `docker compose up --build` workflow was verified from a fresh environment.

## Docker Hub

The application image is published to Docker Hub:

```text
anisakhan4/contractguard-ai:latest
```

Pull the published image with:

```bash
docker pull anisakhan4/contractguard-ai:latest
```

This provides a reproducible container artifact in addition to the source-code repository.

---

# 17. CI/CD

The project includes CI validation for important engineering paths.

The CI workflow includes:

```text
Code Push
   │
   ├── Tests
   │
   ├── AI Evaluation Gate
   │
   └── Docker Build
```

The goal is to prevent changes from being treated as complete simply because the application starts successfully.

AI behavior and containerization are both included in the engineering validation process.

---

# Technology Stack

| Layer               | Technology                                |
| ------------------- | ----------------------------------------- |
| Language            | Python 3.11                               |
| API                 | FastAPI                                   |
| Agent orchestration | LangGraph                                 |
| LLM                 | Gemini                                    |
| Structured output   | Pydantic                                  |
| RAG                 | Hybrid dense + keyword retrieval          |
| Vector search       | PostgreSQL + pgvector                     |
| Database ORM        | SQLAlchemy                                |
| Migrations          | Alembic                                   |
| Authentication      | JWT                                       |
| UI                  | Streamlit                                 |
| Observability       | LangSmith                                 |
| Testing             | Pytest                                    |
| Security audit      | pip-audit                                 |
| Containers          | Docker / Docker Compose                   |
| Container registry  | Docker Hub                                |
| CI/CD               | CI pipeline with Docker + evaluation gate |
| Logging             | Structured JSON logs                      |

---

# Data Model

The system uses persistent models for the major entities in the workflow:

```text
User
 │
 └── Contract
       │
       ├── Clause
       │
       ├── RiskAssessment
       │
       ├── RedlineSuggestion
       │
       └── AuditLog

PrecedentClause
       │
       └── Hybrid Retrieval
```

This allows AI outputs and workflow events to be persisted rather than existing only inside a single model response.

---

# API Surface

The backend exposes protected API workflows for:

* Authentication
* Contract upload
* Contract analysis
* Contract/version comparison
* Risk assessment
* Human review
* Health checks
* Contract-scoped operations

The API is designed around authenticated, user-scoped resources rather than exposing analysis functionality as an unrestricted endpoint.

---

# Engineering Evidence

This project was built around the principle:

> **If a feature cannot be tested, traced, or demonstrated, it is not considered finished.**

Examples of issues discovered and fixed during development include:

* Clause extraction filtering bug
* Redline persistence bug
* LangGraph execution/tracing issue
* Contract ownership isolation vulnerability
* Signup validation weakness
* Duplicate clause creation during repeated analysis
* Docker health-check problems
* Dependency vulnerability discovered through `pip-audit`

These fixes are part of the project's engineering evidence.

---

# Production-Oriented Design Principles

### 1. Evidence over generation

Risk assessments should be supported by retrieved contractual precedent where possible.

### 2. Structured outputs over free-form responses

Pydantic validation provides a predictable interface between the model and application logic.

### 3. Guardrails before downstream action

Model output passes through validation and control layers before redlining or persistence.

### 4. Human oversight for consequential actions

AI-generated recommendations remain reviewable by a human.

### 5. Traceability

Important AI operations are logged and observable.

### 6. Reproducibility

Model and prompt versions are recorded with assessments.

### 7. Security as an engineering layer

Authentication, isolation, injection defense, PII handling, and security testing are integrated into the system.

### 8. Failure discovery is valuable

Security and evaluation tests are used to find weaknesses rather than only produce favorable results.

---

# Engineering Completion Matrix

| Layer | Engineering Area              | Status |
| ----: | ----------------------------- | :----: |
|     1 | Foundation & Project Setup    |    ✅   |
|     2 | Database & Data Model         |    ✅   |
|     3 | Document Ingestion            |    ✅   |
|     4 | Contract Intelligence         |    ✅   |
|     5 | Hybrid RAG / Precedent Engine |    ✅   |
|     6 | Risk Analysis Agent           |    ✅   |
|     7 | LangGraph Orchestration       |    ✅   |
|     8 | Redline Agent                 |    ✅   |
|     9 | Guardrails & Human Safety     |    ✅   |
|    10 | Version Intelligence          |    ✅   |
|    11 | API + Authentication          |    ✅   |
|    12 | Streamlit UI                  |    ✅   |
|    13 | Evaluation Framework          |    ✅   |
|    14 | Red-Team Security             |    ✅   |
|    15 | Observability                 |    ✅   |
|    16 | Docker / CI-CD Hardening      |    ✅   |
|    17 | Final Production Review       |    ✅   |

**Engineering implementation: complete.**

The remaining portfolio work is primarily presentation evidence: final demo recording and selected screenshots.

---

# Demo

### Planned demonstration flow

```text


**Demo:** `TODO — add final video link`

---

# Screenshots


### Contract Analysis

```text
TODO — Add screenshot showing:
Risk assessment + clause analysis + supporting RAG evidence
```

### Version Intelligence

```text
TODO — Add screenshot showing:
Version 1 → Version 2 clause comparison + risk regression
```

### Human Review & Redlining

```text
TODO — Add screenshot showing:
AI redline suggestion + human review workflow
```

### Auditability

```text
TODO — Add screenshot showing:
Audit log + model/prompt version information
```

### Observability

```text
TODO — Add screenshot showing:
LangSmith workflow trace
```

---

# Local Setup

## Prerequisites

* Python 3.11+
* Docker
* Docker Compose
* PostgreSQL / pgvector
* Required LLM API credentials

## Clone

```bash
git clone <repository-url>
cd contract-risk-analyzer
```

## Environment

Create a `.env` file containing the required configuration, including database and model credentials.

Example structure:

```env
DATABASE_URL=<your-database-url>
GEMINI_API_KEY=<your-gemini-api-key>
JWT_SECRET=<your-secret>
LANGSMITH_API_KEY=<your-langsmith-key>
```

Never commit secrets to the repository.

## Docker

Build and start the environment:

```bash
docker compose up --build
```

The project includes database and API health checks to verify service readiness.

---

# Docker Hub Deployment

Published image:

```text
anisakhan4/contractguard-ai:latest
```

Pull:

```bash
docker pull anisakhan4/contractguard-ai:latest
```

Run using the required environment configuration for the application.

---

# Testing

Run the automated test suite:

```bash
pytest
```

The project includes tests covering:

* Guardrails
* Authentication
* Authorization
* Prompt injection
* JWT tampering
* File validation
* PII handling
* Output manipulation
* Cross-contract isolation
* Regression behavior

---

# Security Notes

This project handles contract-related information and therefore treats security as a first-class engineering concern.

Implemented controls include:

* JWT authentication
* Resource ownership isolation
* Input validation
* Prompt-injection detection
* Malicious file testing
* Oversized file testing
* PII detection/redaction
* Output manipulation testing
* Dependency auditing
* Human review
* Audit logging

### Dependency Audit

`pip-audit` was used during development and surfaced **36 CVEs** across dependencies.

A critical dependency issue identified during the audit was addressed.

Dependency security should continue to be monitored as the underlying package ecosystem changes.

---

# Known Limitations

This project is an **engineering prototype / portfolio system with production-oriented architecture**, not a deployed legal-service platform.

Current limitations include:

### Evaluation Dataset

The expanded evaluation contains 17 labeled examples. A production system would require a significantly larger, professionally labeled dataset representing diverse contract types and jurisdictions.

### Model Calibration

The measured 52.94% accuracy demonstrates that additional calibration and evaluation work is required before making high-confidence claims about generalized risk-classification performance.

### Domain Coverage

The current precedent corpus covers four contract niches and does not represent every contract type or jurisdiction.

### Legal Interpretation

The system provides AI-assisted analysis and redline suggestions. It does not replace legal counsel or constitute legal advice.

### Scale Testing

The project has not yet demonstrated production-scale throughput, concurrency, or multi-tenant cloud load performance.

### Model Dependency

AI behavior depends on the selected model, prompt versions, retrieval quality, and available model quotas.

---

# Roadmap

Potential future improvements include:

* Larger professionally labeled evaluation dataset
* Automated calibration optimization
* More contract domains and jurisdictions
* Advanced clause taxonomy
* Better retrieval reranking
* Human feedback loops
* Reviewer analytics
* Larger-scale load testing
* Cloud-native deployment
* Fine-grained role-based access control
* Additional model providers / fallback models
* Automated regression monitoring
* More comprehensive PII and sensitive-data controls

---

# What Makes This Different From a Basic LLM Contract App?

A basic implementation might look like:

```text
Upload PDF
   ↓
Send text to LLM
   ↓
Return summary
```

This project instead implements:

```text
                 Contract
                    │
                    ▼
             Clause Intelligence
                    │
                    ▼
            Hybrid Evidence RAG
                    │
                    ▼
             Risk Analysis Agent
                    │
                    ▼
              Guardrail Layer
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      Continue             Escalate
          │                   │
          ▼                   ▼
      Redlining          Human Review
          │                   │
          └─────────┬─────────┘
                    ▼
              Audit + Trace
                    │
                    ▼
          Reproducible Record
```

The emphasis is therefore not only on **what the LLM generates**, but on:

* How information is retrieved
* How agents are orchestrated
* How outputs are validated
* How unsafe inputs are handled
* How users are isolated
* How humans remain involved
* How AI behavior is evaluated
* How failures are discovered
* How execution is traced
* How results can be reproduced

---

# Project Status

**Status: Engineering implementation complete**

The system has completed its planned 17-layer engineering scope, including:

* Agentic orchestration
* Hybrid RAG
* Risk analysis
* Redlining
* Guardrails
* HITL
* Version intelligence
* Authentication
* Evaluation
* Red-team security
* Observability
* Docker
* CI/CD
* Auditability

The final portfolio presentation layer consists of the demo video and selected screenshots.

---

# Engineering Philosophy

This project follows a simple principle:

> **Reliable AI systems are built around models, not just with models.**

The LLM is one component of the system.

The surrounding engineering determines whether its output can be:

**retrieved → validated → constrained → reviewed → traced → audited → improved**

That is the core engineering focus of Contract Risk Analyzer.

---

## Disclaimer

Contract Risk Analyzer is an AI engineering project for research, demonstration, and portfolio purposes.

It provides **AI-assisted contract analysis and suggestions** and should not be relied upon as legal advice, legal representation, or a substitute for review by qualified legal professionals.

---

## Author

**Anisa Nabi**

**Target Profile:** Agentic AI Engineer | Multi-Agent Systems | LLMs & AI Automation

**Core Focus:**

`Agentic AI` · `Generative AI` · `LLMs` · `RAG` · `Multi-Agent Systems` · `LangGraph` · `LangChain` · `AI Automation` · `Python` · `FastAPI` · `PostgreSQL` · `Vector Databases` · `MCP` · `n8n` · `Docker` · `Cloud Deployment`

---

⭐ **If you're reviewing this project as an AI engineering portfolio piece, the most important sections are the architecture, evaluation evidence, security testing, observability, and engineering fixes—not just the feature list.**
