# SPEC-020: Implementation Roadmap & Coding Plan

**Status:** ACTIVE PLAN
**Purpose:** Step-by-step implementation guide for Rubrica SRE Agent
**Timeline:** 48-hour sprint
**Dependencies:** SPECS 000-019

---

## 📋 Overview

This document translates the Rubrica specifications into a concrete implementation sequence. Each phase produces working artifacts that can be tested immediately, enabling rapid iteration and early validation.

**Core Principle:** Build in layers. Foundation first, then intelligence, then integration, then polish.

---

## 🏗️ PHASE 0: Project Scaffolding (Foundation)

**Duration:** ~2 hours
**Deliverable:** Working monorepo with Docker infrastructure

### Tasks
- [ ] **0.1** Initialize git repository and create directory structure
  ```
  rubrica/
  ├── backend/
  ├── frontend/
  ├── shared/
  ├── scripts/
  └── tests/
  ```
- [ ] **0.2** Create `shared/__init__.py` and `shared/schemas.py` with base Pydantic models
  - `IncidentIntake`, `SecurityCheck`, `TriageResult`, `InvestigationPlan`
- [ ] **0.3** Create `.env.example` (SPEC-016)
- [ ] **0.4** Create `docker-compose.yml` (SPEC-015)
- [ ] **0.5** Verify: `docker compose up` starts Redis and Qdrant successfully

**Validation:** `docker ps` shows 2 running containers (redis, qdrant)

---

## 🔧 PHASE 1: The Bunker - Backend Foundation (1-6 hours)

**Duration:** ~5 hours
**Deliverable:** FastAPI server with basic endpoints

### 1.1 Project Setup (1 hour)
- [ ] **1.1.1** Create `backend/requirements.txt`
  ```
  fastapi
  uvicorn[standard]
  pydantic>=2.0
  pydantic-settings
  instructor
  langgraph
  langchain-google-genai
  qdrant-client
  redis
  loguru
  python-multipart
  sendgrid
  slack-sdk
  ```
- [ ] **1.1.2** Create `backend/Dockerfile` (SPEC-017)
- [ ] **1.1.3** Create `backend/main.py` with FastAPI app
- [ ] **1.1.4** Add health check endpoint: `GET /api/v1/health`
- [ ] **1.1.5** Verify: `docker compose up api` exposes http://localhost:8000/docs

### 1.2 Configuration & Settings (30 min)
- [ ] **1.2.1** Create `backend/config.py` using pydantic-settings
- [ ] **1.2.2** Load environment variables (GEMINI_API_KEY, REDIS_URL, QDRANT_URL)
- [ ] **1.2.3** Implement fail-fast: crash on missing required keys
- [ ] **1.2.4** Add Loguru configuration with structured logging

### 1.3 Database Connections (1 hour)
- [ ] **1.3.1** Create `backend/db/redis_client.py`
- [ ] **1.3.2** Create `backend/db/qdrant_client.py`
- [ ] **1.3.3** Add connection health checks
- [ ] **1.3.4** Test: Write/read from Redis, create Qdrant collection

**Validation:** All services connect successfully, logs show structured output

---

## 🛡️ PHASE 2: Security Layer (6-9 hours)

**Duration:** ~3 hours
**Deliverable:** Working Shield Node

### Tasks
- [ ] **2.1** Create `backend/shield.py` with ShieldNode class
  - Input: `IncidentIntake` model
  - Logic: Gemini Flash with negative constraint prompt
  - Output: `SecurityCheck` model (is_safe: bool, risk_score: int)
- [ ] **2.2** Implement Instructor integration for structured output
- [ ] **2.3** Add shield endpoint: `POST /api/v1/shield/check`
- [ ] **2.4** Create test cases:
  - Valid SRE report → is_safe=True
  - Prompt injection → is_safe=False
  - Off-topic request → is_safe=False
- [ ] **2.5** Add to LangGraph as first node

**Validation:** Shield blocks "ignore previous instructions" attack

---

## 🧠 PHASE 3: Intelligence Layer (9-18 hours)

**Duration:** ~9 hours
**Deliverable:** Working Triage and Librarian agents

### 3.1 Triage Supervisor (3 hours)
- [ ] **3.1.1** Create `backend/agents/supervisor.py`
- [ ] **3.1.2** Implement multimodal correlation logic
- [ ] **3.1.3** Create `InvestigationPlan` output model
- [ ] **3.1.4** Add Instructor retry logic for validation failures
- [ ] **3.1.5** Test: Screenshot + logs → technical summary

### 3.2 Librarian - RAG Implementation (4 hours)
- [ ] **3.2.1** Create `backend/agents/librarian.py`
- [ ] **3.2.2** Implement Qdrant vector search
- [ ] **3.2.3** Implement BM25 keyword search (using rank-bm25)
- [ ] **3.2.4** Create hybrid result merger
- [ ] **3.2.5** Add context compression logic
- [ ] **3.2.6** Test: Error class → exact code location

### 3.3 LangGraph Orchestration (2 hours)
- [ ] **3.3.1** Create `backend/graph.py` with state machine
- [ ] **3.3.2** Define state schema using Pydantic
- [ ] **3.3.3** Implement nodes: shield → triage → librarian → synthesis
- [ ] **3.3.4** Add Redis checkpointing for state persistence
- [ ] **3.3.5** Test: Full graph execution produces `TriageResult`

**Validation:** Graph traces visible in LangSmith

---

## 🔌 PHASE 4: ITSM Integration (18-22 hours)

**Duration:** ~4 hours
**Deliverable:** Jira and Slack integrations

### Tasks
- [ ] **4.1** Create `backend/integrations/itsm_bridge.py`
- [ ] **4.2** Implement Jira client (using jira library)
  - Create ticket with priority mapping
  - Generate ticket ID
- [ ] **4.3** Implement Slack webhook client
  - Post to #sre-alerts with ticket link
- [ ] **4.4** Implement email notification (SendGrid or mock)
- [ ] **4.5** Add ITSM node to LangGraph
- [ ] **4.6** Test: Full incident → Jira ticket created + Slack alert sent

**Validation:** Integration endpoints return valid ticket IDs

---

## 🔄 PHASE 5: Stateful Lifecycle (22-26 hours)

**Duration:** ~4 hours
**Deliverable:** Hibernate and resume functionality

### Tasks
- [ ] **5.1** Implement "wait" state in LangGraph
- [ ] **5.2** Add Redis checkpoint save after ITSM action
- [ ] **5.3** Create webhook endpoint: `POST /api/v1/webhooks/jira`
- [ ] **5.4** Implement resume logic: load thread_id from Redis, wake graph
- [ ] **5.5** Add final notification node (email reporter)
- [ ] **5.6** Test: Create ticket → graph sleeps → webhook → graph wakes → notification sent

**Validation:** Incident persists across container restart

---

## 📚 PHASE 6: Codebase Ingestion (26-30 hours)

**Duration:** ~4 hours
**Deliverable:** Saleor indexing script

### Tasks
- [ ] **6.1** Create `scripts/ingest_saleor.py`
- [ ] **6.2** Implement Saleor repository cloning/downloading
- [ ] **6.3** Create file chunker (Python, GraphQL files)
- [ ] **6.4** Generate embeddings using Gemini embedding model
- [ ] **6.5** Batch insert to Qdrant with metadata
- [ ] **6.6** Create BM25 index from file contents
- [ ] **6.7** Add progress logging and error handling
- [ ] **6.8** Test: Query returns relevant Saleor code snippets

**Validation:** Search returns accurate results for "checkout tax calculation"

---

## 🎨 PHASE 7: The Borde - Frontend (30-38 hours)

**Duration:** ~8 hours
**Deliverable:** Next.js intake UI and dashboard

### 7.1 Project Setup (1 hour)
- [ ] **7.1.1** Initialize Next.js 14 with App Router
- [ ] **7.1.2** Install dependencies: Tailwind, shadcn/ui
- [ ] **7.1.3** Create `frontend/Dockerfile` (SPEC-017)
- [ ] **7.1.4** Configure environment variables
- [ ] **7.1.5** Test: http://localhost:3000 loads

### 7.2 API Client (1 hour)
- [ ] **7.2.1** Generate TypeScript client from FastAPI OpenAPI
- [ ] **7.2.2** Create `frontend/lib/api.ts`
- [ ] **7.2.3** Add types from `shared/schemas.py`
- [ ] **7.2.4** Test: Client calls health endpoint

### 7.3 Intake Page (3 hours)
- [ ] **7.3.1** Create `app/intake/page.tsx`
- [ ] **7.3.2** Add form: description field, file upload (screenshot + logs)
- [ ] **7.3.3** Implement file preview for images
- [ ] **7.3.4** Add submit handler with loading state
- [ ] **7.3.5** Display incident ID after submission
- [ ] **7.3.6** Add error handling and validation

### 7.4 Dashboard Page (3 hours)
- [ ] **7.4.1** Create `app/dashboard/page.tsx`
- [ ] **7.4.2** Add incident list (poll or SSE for updates)
- [ ] **7.4.3** Display incident status: Shield → Triage → Action → Resolved
- [ ] **7.4.4** Show LangSmith trace link
- [ ] **7.4.5** Display Jira ticket link
- [ ] **7.4.6** Add real-time status updates

**Validation:** Full user flow works end-to-end

---

## 📊 PHASE 8: Observability & Evidence (38-44 hours)

**Duration:** ~6 hours
**Deliverable:** Complete observability stack and demo evidence

### Tasks
- [ ] **8.1** LangSmith Integration
  - Add tracing to all LangGraph nodes
  - Generate public trace URLs
  - Screenshot "Checkout Crisis" trace
- [ ] **8.2** Opik Integration
  - Add token cost tracking
  - Add latency metrics
  - Run 5-incident eval dataset
  - Screenshot dashboard with 90%+ accuracy
- [ ] **8.3** Security Evidence
  - Run prompt injection attack
  - Screenshot Shield blocking it
- [ ] **8.4** System Evidence
  - Collect color-coded terminal logs
  - Screenshot state transitions

**Validation:** All evidence collected for `AGENTS_USE.md`

---

## 📝 PHASE 9: Documentation (44-46 hours)

**Duration:** ~2 hours
**Deliverable:** Complete documentation set

### Tasks
- [ ] **9.1** Create `README.md` (SPEC-011)
- [ ] **9.2** Create `AGENTS_USE.md` (SPEC-012) with evidence links
- [ ] **9.3** Create `QUICKGUIDE.md` (SPEC-014)
- [ ] **9.4** Create `SCALING.md` (SPEC-013)
- [ ] **9.5** Update `.env.example` with all required variables
- [ ] **9.6** Create `LICENSE` file (MIT)

**Validation:** All docs present and accurate

---

## 🚀 PHASE 10: Final Integration & Polish (46-48 hours)

**Duration:** ~2 hours
**Deliverable:** Production-ready deployment

### Tasks
- [ ] **10.1** Run full E2E test: "Checkout Crisis" scenario
- [ ] **10.2** Verify all container restarts work
- [ ] **10.3** Check memory usage (optimize if >4GB)
- [ ] **10.4** Clean up test data and logs
- [ ] **10.5** Create demo script (step-by-step for judges)
- [ ] **10.6** Final validation checklist:
  - [ ] All services start with `docker compose up`
  - [ ] Ingest script runs without errors
  - [ ] Incident can be submitted via UI
  - [ ] Jira ticket is created
  - [ ] Slack alert is sent
  - [ ] Webhook resumes incident
  - [ ] Reporter receives notification
  - [ ] LangSmith trace is accessible
  - [ ] All documentation is complete

---

## 📦 Critical Files by Creation Order

```
1. shared/schemas.py              # Foundation
2. backend/requirements.txt
3. backend/Dockerfile
4. docker-compose.yml
5. .env.example
6. backend/main.py
7. backend/config.py
8. backend/db/redis_client.py
9. backend/db/qdrant_client.py
10. backend/shield.py              # Security
11. backend/agents/supervisor.py
12. backend/agents/librarian.py    # Intelligence
13. backend/integrations/itsm_bridge.py
14. backend/graph.py               # Orchestration
15. scripts/ingest_saleor.py       # Ingestion
16. frontend/package.json
17. frontend/Dockerfile
18. frontend/lib/api.ts
19. frontend/app/intake/page.tsx   # Frontend
20. frontend/app/dashboard/page.tsx
21. README.md                      # Documentation
22. AGENTS_USE.md
23. QUICKGUIDE.md
24. LICENSE
```

---

## ⚠️ Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Gemini rate limits** | Implement exponential backoff, use Flash where possible |
| **Qdrant indexing slow** | Chunk and batch ingest, provide progress bar |
| **LangGraph state complexity** | Start with linear flow, add cycles after basic flow works |
| **Docker memory issues** | Use slim images, clean package caches, limit container memory |
| **Webhook testing** | Use ngrok or Cloudflare Tunnel for local testing |

---

## 🎯 Success Criteria

The project is complete when:
1. ✅ `docker compose up` starts all services successfully
2. ✅ Ingest script indexes Saleor without errors
3. ✅ User can submit incident via UI with screenshot + logs
4. ✅ Shield validates input and blocks attacks
5. ✅ Triage produces accurate technical summary
6. ✅ Jira ticket is created with correct priority
7. ✅ Slack alert includes ticket link
8. ✅ Webhook triggers resume and notification
9. ✅ LangSmith shows full graph trace
10. ✅ All documentation is present and accurate

---

## 📌 Quick Reference: Phase Dependencies

```
Phase 0 (Scaffolding)
    ↓
Phase 1 (Backend Foundation)
    ↓
Phase 2 (Security) ←─────┐
    ↓                     │
Phase 3 (Intelligence)   │
    ↓                     │
Phase 4 (ITSM) ←─────────┘
    ↓
Phase 5 (Stateful Lifecycle)
    ↓
Phase 6 (Ingestion) [Can run in parallel after Phase 3]
    ↓
Phase 7 (Frontend) [Can run in parallel after Phase 1]
    ↓
Phase 8 (Observability)
    ↓
Phase 9 (Documentation)
    ↓
Phase 10 (Final Polish)
```

**Parallelization Opportunities:**
- Phases 6 & 7 can run concurrently after Phase 3
- Frontend development (7.2-7.4) can happen alongside backend (3-5)

---

**End of SPEC-020: Implementation Roadmap**

*This plan provides a concrete path from zero to production-ready Rubrica in 48 hours. Adjust phase durations based on team size and expertise.*
