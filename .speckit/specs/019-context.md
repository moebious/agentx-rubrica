# SPEC-019: Rubrica Project Context (Internal Memory)

**Status:** INTERNAL REFERENCE
**Purpose:** Comprehensive project understanding for development continuity
**Generated:** April 9, 2026

---

## 🎯 Project Essence

**Rubrica** is a production-grade SRE Incident Intake & Triage Agent for the Saleor e-commerce platform. It automates the journey from chaotic failure reports to structured technical resolution using stateful agentic orchestration.

**Core Problem Solved:** Bridging the gap between multimodal incident reports (screenshots + logs) and technical root-cause analysis in a complex codebase.

**Competition Context:** AgentX Hackathon 2026 submission — must demonstrate production-readiness, not just a functional prototype.

---

## 🏗️ Architecture Philosophy

### The Dual-Component Design
| Component | Name | Purpose |
|-----------|------|---------|
| **Backend** | The Bunker | FastAPI + LangGraph state machine for incident processing |
| **Frontend** | The Borde | Next.js UI for multimodal intake and real-time status |

### The "Stateless Compute, Stateful Memory" Pattern
- Backend instances are stateless
- All conversation state stored in Redis (checkpointing)
- Enables horizontal scaling and "hibernate/resume" workflows
- Any instance can resume any incident thread

---

## 🤖 The Agent Roster

| Agent | Model | Role | Key Capability |
|-------|-------|------|----------------|
| **Shield** | Gemini 2.5 Flash | Security Sentry | Prompt injection detection, input validation |
| **Triage Supervisor** | Gemini 2.5 Pro | Lead Investigator | Multimodal correlation, investigation planning |
| **Librarian** | Gemini 2.5 Pro | Code Researcher | Hybrid RAG (Vector + BM25) on Saleor repo |
| **ITSM Bridge** | Gemini 2.5 Flash | Integration Worker | Jira ticket creation, Slack notifications |

**Economic Design:** Flash for speed/low-cost tasks, Pro for deep reasoning

---

## 🔄 The Happy Path Workflow

```
1. INTAKE: User uploads screenshot + logs via Borde UI
       ↓
2. SHIELD: Gemini Flash validates input (is_safe check)
       ↓
3. TRIAGE: Supervisor correlates multimodal input
       ↓
4. RETRIEVAL: Librarian searches Saleor codebase
       ↓
5. ACTION: ITSM Bridge creates Jira ticket + Slack alert
       ↓
6. HIBERNATE: State saved to Redis, graph sleeps
       ↓
7. WEBHOOK: Jira sends "resolved" event
       ↓
8. RESUME: Graph wakes from Redis checkpoint
       ↓
9. NOTIFY: Reporter emailed with resolution confirmation
```

---

## 🔧 Tech Stack Summary

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **LLMs** | Gemini 2.5 Pro/Flash | 1M token context, multimodal, cost-effective |
| **Orchestration** | LangGraph | Stateful DAG with checkpointing |
| **Backend** | FastAPI (Python 3.12) | Async I/O, auto-generated OpenAPI |
| **Frontend** | Next.js 14 + shadcn/ui | Server components, premium UX |
| **State** | Redis | LangGraph checkpointing for long-running workflows |
| **Memory** | Qdrant | Vector storage for codebase RAG |
| **Validation** | Instructor + Pydantic v2 | Strict schema enforcement, no raw dicts |
| **Observability** | LangSmith + Opik | Tracing, metrics, LLM evals |
| **Logging** | Loguru | Structured async logging with correlation IDs |
| **Security** | Custom Shield Node | Prompt injection filtering |
| **Integration** | FastMCP | Safe tool execution protocol |

---

## 🎨 Key Differentiators

### 1. Stateful Lifecycle
Most agents are linear chats. Rubrica can **hibernate and resume** based on external webhooks (Jira resolution). This proves production readiness.

### 2. 1M Token Context Strategy
Instead of RAG snippets, Rubrica feeds **entire modules** to Gemini Pro. This provides full architectural awareness that snippet-based RAG cannot match.

### 3. Hybrid Search Safety
Never relies on vector search alone:
- **Qdrant (Semantic):** "How does payment flow work?"
- **BM25 (Keyword):** Exact error class matches like `AttributeError`

### 4. Multimodal Fusion
Correlates UI state (screenshots) with backend state (logs) in a single prompt. Vision provides the "what," logs provide the "why."

### 5. Economic Agent Design
Strategic model allocation:
- Flash: Shield, ITSM (speed-sensitive, low reasoning)
- Pro: Supervisor, Librarian (deep reasoning required)

---

## 🛡️ Security Architecture

### Multi-Layer Defense
1. **Shield Node:** LLM-based prompt injection filtering (Gemini Flash)
2. **Pydantic Validation:** All outputs must conform to strict schemas
3. **FastMCP Isolation:** Tools cannot access system directly
4. **Credential Safety:** Pydantic-settings crashes on missing keys
5. **PII Handling:** Automatic redaction in ticket creation

---

## 📊 Observability Strategy

### Three-Tier Approach
| Tier | Tool | Purpose |
|------|------|---------|
| **Macro** | LangSmith | Visualize agent decision tree/graph traces |
| **Quality** | Opik | LLM evals, token costs, latency metrics |
| **Micro** | Loguru | Structured logs with request_id correlation |

### Evidence for Judges
- Public LangSmith trace showing Shield → Triage → Action flow
- Opik dashboard with 90%+ triage accuracy benchmark
- Screenshot of Shield blocking prompt injection attack
- Terminal logs showing color-coded state transitions

---

## 📁 Filesystem Structure

```
rubrica/
├── backend/           # The Bunker
│   ├── graph.py      # LangGraph orchestration
│   ├── shield.py     # Security filtering
│   ├── tools.py      # MCP integrations
│   └── Dockerfile
├── frontend/          # The Borde
│   ├── app/          # Next.js App Router
│   ├── lib/          # API client
│   └── Dockerfile
├── shared/            # Single Source of Truth
│   └── schemas.py    # Pydantic models (API + State + Tools)
├── scripts/
│   └── ingest_saleor.py  # Codebase indexing
├── .env.example
├── docker-compose.yml
├── AGENTS_USE.md
├── QUICKGUIDE.md
├── README.md
└── LICENSE
```

**Critical Design Pattern:** `shared/` directory ensures frontend/backend parity. If schemas change, build fails immediately.

---

## 🎯 Use Case: "The Checkout Crisis"

The canonical demo scenario:
1. Customer gets "500 Internal Server Error" at checkout
2. Uploads screenshot of greyed-out "Pay" button + browser logs
3. Shield validates as legitimate technical report
4. Supervisor identifies `TaxError` in `saleor.checkout.calculations`
5. Librarian retrieves full `calculations.py` with hybrid search
6. Jira ticket created (Critical priority), Slack alerted
7. Engineer fixes bug, closes ticket
8. Webhook triggers resume, reporter emailed confirmation

**Proves:** Multimodal intake, codebase navigation, stateful lifecycle, integrations

---

## 🚀 Deployment Considerations

### Local Development
```bash
docker compose up --build
docker compose exec api python scripts/ingest_saleor.py
```

### Production
- **Hetzner CX22 VPS** (4GB RAM) for Bunker
- **Cloudflare Tunnels** for zero-inbound networking
- **Edge deployment** (Vercel) for Borde to reduce latency

### Scalability
- Horizontal: Stateless API instances + centralized Redis
- Vertical: 1M token context scales with codebase size
- Qdrant sharding for vector index growth

---

## 📝 Implementation Priorities (48-Hour Sprint)

| Phase | Focus | Deliverable |
|-------|-------|-------------|
| **T-48h** | Scaffold | Monorepo, FastAPI, Next.js |
| **T-40h** | Infrastructure | Docker Compose (Redis, Qdrant) |
| **T-36h** | Knowledge | Ingest Saleor to Qdrant |
| **T-24h** | Logic | LangGraph (Triage → Wait → Resolve) |
| **T-12h** | Integration | Cloudflare Tunnel, Jira webhooks |
| **T-4h** | Evidence | Opik evals, screenshots for judges |

---

## 🔑 Critical Insights

### Technical
1. **Redis checkpointing is the hardest part** — managing long-running async workflows in serverless environments
2. **Multimodal correlation is the breakthrough** — vision + logs catches UI/UX bugs text-only agents miss
3. **Pydantic is essential** — without strict schemas, LLM tool-calling is too risky for production

### Strategic
1. **Supervisor pattern > Chained pattern** — more stable, can request more info autonomously
2. **Best agents know when to wait** — human-in-the-loop is a feature, not a bug
3. **Specialization reduces hallucination** — dedicated Librarian agent vs. single-agent approach

---

## 📌 Quick Reference Commands

```bash
# Development
docker compose up --build
docker compose exec api python scripts/ingest_saleor.py

# Access
Frontend: http://localhost:3000
Backend: http://localhost:8000
API Docs: http://localhost:8000/docs
Redis: localhost:6379
Qdrant: http://localhost:6333/dashboard

# Environment
cp .env.example .env
# Edit .env with GEMINI_API_KEY
```

---

## ⚠️ Gotchas & Edge Cases

1. **Port conflicts:** Ensure 3000, 8000, 6379, 6333 are free
2. **Docker memory:** Minimum 4GB RAM required (Qdrant + Gemini)
3. **Shared directory:** Must use root context in docker-compose
4. **OpenRouter 401:** Check credits and API key validity
5. **LangGraph state:** Always include thread_id in webhooks for resumption

---

**End of SPEC-019: Internal Project Context**

*This spec serves as the comprehensive knowledge base for Rubrica, synthesizing information from all other specifications into a single reference document.*
