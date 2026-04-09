# SPEC-021: Solo MVP Implementation Plan

**Status:** ACTIVE PLAN
**Developer Profile:** Solo, Mid-Level Experience
**Timeline:** 48 hours with realistic scope
**Philosophy:** Complete, working demo over complex incomplete system

---

## 🎯 MVP Scope Decisions

### ✅ Must Have (Non-Negotiable)
| Feature | Rationale |
|---------|-----------|
| **Next.js Frontend** | Critical for demo — judges see the UI, not the API |
| **Sample Codebase Index** | Core feature — prove RAG works on real code |
| **Shield → TriageAgent Flow** | Two agents is the minimum for security + intelligence |
| **README.md** | Required deliverable |
| **AGENTS_USE.md** | Required deliverable |

### ⚡ Simplified (Time-Savers)
| Feature | Approach | Time Saved |
|---------|----------|------------|
| **Hibernate/Resume** | Skip — inline notifications only | 4 hours |
| **BM25 Search** | Vector-only (Qdrant) | 2 hours |
| **ITSM Integration** | Real Jira OR Slack, mock the other | 2 hours |
| **Full Observability** | LangSmith only (skip Opik evals) | 3 hours |
| **Extra Docs** | Skip until end | 2 hours |

### 📊 Scope Comparison
| Approach | Original | MVP | Savings |
|----------|----------|-----|----------|
| Agents | 4 | 2 | 6 hours |
| Frontend | Next.js | Next.js | 0 (kept!) |
| Search | Hybrid | Vector only | 2 hours |
| Webhooks | Full flow | Inline only | 4 hours |
| Integration | Both real | One real, one mock | 2 hours |
| Observability | Full stack | LangSmith only | 3 hours |
| Codebase | Full Saleor | 50-100 sample files | 3 hours |
| Docs | Full set | 2 essential | 2 hours |
| **TOTAL** | ~80 hours | **~35 hours** | **~45 hours** |

---

## 📋 30-Hour Implementation Plan

### DAY 1: Foundation & Intelligence (16 hours)

#### Hours 0-3: Scaffolding
- [ ] Initialize monorepo structure
- [ ] Create `shared/schemas.py` with core models
  - `IncidentIntake`, `SecurityCheck`, `TriageResult`
- [ ] Create `docker-compose.yml` (Redis, Qdrant, API placeholder)
- [ ] Create `.env.example`
- [ ] **Validation:** `docker compose up` starts services

#### Hours 3-6: Shield Node
- [ ] Create `backend/shield.py`
- [ ] Implement Gemini Flash integration
- [ ] Add prompt injection detection logic
- [ ] Create `SecurityCheck` output model
- [ ] Add `/api/v1/shield/check` endpoint
- [ ] **Validation:** Blocks "ignore instructions" attack

#### Hours 6-10: Triage Agent
- [ ] Create `backend/agents/triage_agent.py`
- [ ] Implement Gemini Pro integration
- [ ] Add multimodal correlation logic
- [ ] Create `TriageResult` output model
- [ ] Add Instructor validation with retry
- [ ] **Validation:** Produces technical summary from screenshot + logs

#### Hours 10-13: Qdrant Integration
- [ ] Create `backend/db/qdrant_client.py`
- [ ] Implement vector search
- [ ] Create collection schema
- [ ] Add embedding logic (Gemini embeddings)
- [ ] **Validation:** Search returns relevant results

#### Hours 13-16: Simple Graph
- [ ] Create `backend/graph.py` with linear flow
- [ ] Nodes: Shield → Triage → Done
- [ ] Add basic state management (no Redis checkpointing yet)
- [ ] Add LangSmith tracing
- [ ] **Validation:** End-to-end flow produces trace

---

### DAY 2: Frontend, Integration & Polish (14+ hours)

#### Hours 16-19: Codebase Ingestion
- [ ] Create sample codebase (50-100 Python files)
- [ ] Create `scripts/ingest_sample.py`
- [ ] Implement file chunking
- [ ] Generate embeddings
- [ ] Batch insert to Qdrant
- [ ] **Validation:** Search returns accurate code snippets

#### Hours 19-23: Next.js Frontend
- [ ] Initialize Next.js 14 with App Router
- [ ] Install Tailwind + shadcn/ui
- [ ] Create intake page (`app/intake/page.tsx`)
  - Description input
  - File upload (screenshot + logs)
  - Submit button with loading state
  - Result display
- [ ] Create API client (`lib/api.ts`)
- [ ] Add error handling
- [ ] **Validation:** Can submit incident via UI

#### Hours 23-26: ITSM Integration (Choose One)
- [ ] **Option A: Real Jira, Mock Slack**
  - Integrate Jira Python library
  - Create ticket with priority
  - Mock Slack (log payload to console)
- [ ] **Option B: Real Slack, Mock Jira**
  - Integrate Slack webhook
  - Post to channel with incident details
  - Mock Jira (log payload to console)
- [ ] Add integration to graph
- [ ] **Validation:** Real API call succeeds

#### Hours 26-29: Redis & State
- [ ] Add Redis client to backend
- [ ] Implement basic state storage
- [ ] Add incident ID tracking
- [ ] Store triage results in Redis
- [ ] **Validation:** State persists across requests

#### Hours 29-32: Documentation
- [ ] Create `README.md`
  - Architecture overview
  - Setup instructions
  - Tech stack
- [ ] Create `AGENTS_USE.md`
  - Agent descriptions
  - Workflow explanation
  - LangSmith trace link
  - Security evidence
- [ ] Create `.env.example` with all variables
- [ ] **Validation:** Both docs are complete and accurate

#### Hours 32-35: Buffer & Polish
- [ ] Run full E2E test
- [ ] Fix any bugs
- [ ] Collect LangSmith trace screenshot
- [ ] Collect Shield security test screenshot
- [ ] Clean up test data
- [ ] Verify `docker compose up` works fresh
- [ ] **Validation:** Demo-ready

---

## 🏗️ Simplified Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NEXT.JS FRONTEND                        │
│  (Intake Page: Description + Screenshot + Logs Upload)      │
└────────────────────────┬────────────────────────────────────┘
                         │ POST /api/v1/incident
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   SHIELD NODE    │
              │  (Gemini Flash)  │
              │  Input validation │
              └────────┬─────────┘
                       │ is_safe=true
                       ▼
              ┌──────────────────┐
              │  TRIAGE AGENT    │
              │  (Gemini Pro)    │
              │  - Correlate UI  │
              │  - Search Qdrant │
              │  - Produce plan  │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  ITSM ACTION     │
              │  - Real Jira OR  │
              │  - Real Slack    │
              │  - Mock other    │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   REDIS STORE    │
              │  - Save incident │
              │  - Save result   │
              └──────────────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  NOTIFICATION    │
              │  - Inline email  │
              │  - No webhook    │
              └──────────────────┘

(Observable via LangSmith throughout)
```

---

## 📦 Critical Files (Simplified Set)

```
rubrica/
├── shared/
│   └── schemas.py              # Foundation: Pydantic models
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── graph.py                # Shield → Triage → Action
│   ├── shield.py               # Security validation
│   ├── agents/
│   │   └── triage_agent.py     # Single triage agent
│   ├── db/
│   │   ├── redis_client.py
│   │   └── qdrant_client.py
│   ├── integrations/
│   │   ├── jira_client.py      # OR slack_client.py
│   │   └── mock_itsm.py        # Mock the other
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── intake/
│   │   │   └── page.tsx        # Main intake UI
│   │   └── layout.tsx
│   ├── lib/
│   │   └── api.ts              # API client
│   ├── package.json
│   └── Dockerfile
├── scripts/
│   └── ingest_sample.py        # Sample codebase ingestion
├── sample_codebase/             # 50-100 Python files
├── docker-compose.yml
├── .env.example
├── README.md                    # Essential
├── AGENTS_USE.md                # Essential
└── LICENSE
```

**Total: ~20 files** (vs 30+ in full spec)

---

## 🎯 Demo Script (What Judges See)

### Step 1: The Setup (2 minutes)
- Show repo structure
- Run `docker compose up`
- Show services starting (Redis, Qdrant, API, Frontend)
- "We're ready to ingest incidents"

### Step 2: The Intake (3 minutes)
- Open http://localhost:3000
- Show intake form
- Upload sample screenshot (checkout error)
- Upload sample logs
- Click submit

### Step 3: The Intelligence (5 minutes)
- Switch to terminal showing API logs
- Show Shield validation: "is_safe: true"
- Show Triage Agent: "Analyzing multimodal input..."
- Show Qdrant search: "Found 3 relevant files"
- Show final output: "Root cause identified"

### Step 4: The Integration (2 minutes)
- Show Jira ticket created (real browser)
- OR show Slack message posted (real browser)
- Show the other: "In production, this would notify X"
- Show incident stored in Redis

### Step 5: The Observability (3 minutes)
- Open LangSmith trace
- Walk through the decision tree
- Show token usage and latency
- "Full transparency into agent reasoning"

**Total demo: 15 minutes**

---

## ⚠️ Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Next.js takes too long** | Use create-next-app with shadcn, don't over-engineer |
| **Qdrant indexing fails** | Have pre-indexed sample data as fallback |
| **Jira/Slack API issues** | Mock implementation ready as backup |
| **LangSmith not working** | Console logging is sufficient for demo |
| **Time running out** | Cut documentation first, then integration, then frontend |

---

## 🎯 Success Criteria (MVP)

### Must Have (Blocking)
- [ ] Docker compose starts all services
- [ ] User can submit incident via Next.js UI
- [ ] Shield validates input and blocks attacks
- [ ] Triage produces technical summary
- [ ] Qdrant returns relevant code snippets
- [ ] One real integration works (Jira OR Slack)
- [ ] LangSmith shows full trace
- [ ] README and AGENTS_USE.md are complete

### Nice to Have (If Time)
- [ ] Both integrations real
- [ ] BM25 search added
- [ ] Extra documentation
- [ ] Polished UI design

---

## 📌 Hour Checkpoint Guide

| Hour | Should Have | If Behind |
|------|-------------|-----------|
| 6 | Shield working | Skip advanced prompt patterns |
| 12 | Triage + Qdrant working | Reduce sample codebase size |
| 18 | Full backend flow | Mock both integrations |
| 24 | Frontend functional | Use simpler UI components |
| 30 | Documentation | Reduce to README only |

---

## 🚀 Quick Start Commands

```bash
# Initial setup
git clone https://github.com/your-username/rubrica.git
cd rubrica
cp .env.example .env
# Edit .env with API keys

# Start services
docker compose up --build

# Ingest sample codebase
docker compose exec api python scripts/ingest_sample.py

# Run locally (if not using Docker for frontend)
cd frontend && npm install && npm run dev
```

---

## 💡 Final Notes

### What You're Building
A working SRE agent that:
- Takes multimodal incident reports
- Validates security
- Searches codebase intelligently
- Creates real tickets/notifications
- Shows full observability

### What You're NOT Building (Yet)
- Hibernate/resume webhooks
- Full hybrid search
- Complete Saleor index
- Both integrations real
- Full documentation suite

### The Win
You'll have a **complete, working system** that tells a coherent story. Judges can see the UI, trace the logic, and understand the architecture.

**That's what wins hackathons.**

---

**End of SPEC-021: Solo MVP Implementation Plan**

*Focus on complete execution over incomplete complexity. Build something that works end-to-end.*
