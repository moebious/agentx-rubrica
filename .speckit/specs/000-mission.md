# SPEC-000: Mission Mandate & Rules of Engagement

**Project:** Rubrica SRE Agent
**Event:** AgentX Hackathon 2026
**Status:** IMPLEMENTATION IN PROGRESS
**Updated:** April 9, 2026

---

## 1. The Assignment: SRE Incident Intake & Triage

We are building a production-ready SRE Agent for our e-commerce platform (Saleor). The mission is to bridge the gap between failure reports and technical resolution with zero manual friction.

### Core E2E Flow
1. **Intake:** Submit multimodal reports via UI.
2. **Shield:** Security validation BEFORE any processing.
3. **Triage:** Extract key details + produce technical summary.
4. **Ticket:** Auto-create tickets in Jira/Linear.
5. **Internal Notify:** Alert the tech team via Email/Slack.
6. **External Notify:** Automatically email the original reporter once resolved.

---

## 2. Technical Minimum Requirements

To pass the automated screening, Rubrica must meet these five "Hard Gates":

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **Multimodal Input** | ⚠️ Partial | Text + logs implemented, image processing TODO |
| **Guardrails** | ✅ Complete | Shield Node + tool gating + fail-closed (15/15 tests pass) |
| **Observability** | ✅ Complete | LangSmith/Opik conditional on API keys |
| **Integrations** | ⚠️ Partial | Jira/Slack/email stubbed, TODO |
| **Complex Codebase** | ⚠️ Partial | Code search stub, Qdrant TODO |

---

## 3. Implementation Progress

| Component | Status | Files |
|-----------|--------|-------|
| **Shield Node** | ✅ Complete | `backend/shield.py` |
| **Triage Agent** | ✅ Complete | `backend/triage.py` |
| **API Endpoints** | ✅ Complete | `backend/main.py` |
| **Test Suite** | ✅ Complete | `backend/test_shield.py` (15 tests) |
| **LLM Clients** | ✅ Complete | Dual-provider (Gemini + OpenRouter) |
| **Code Search (RAG)** | ⚠️ Stub | Qdrant client exists, search logic TODO |
| **ITSM Bridge** | ⚠️ Stub | Jira/Slack/email clients TODO |
| **Frontend** | ❌ Not Started | Next.js app scaffolded |

---

## 4. Evaluation Dimensions

| Dimension | Status | Evidence |
|-----------|--------|----------|
| **Reliability** | ✅ Complete | Fail-closed error handling, 15/15 tests pass |
| **Observability** | ✅ Complete | LangSmith/Opik conditional, structured logging via Loguru |
| **Scalability** | ⚠️ Partial | Architecture documented, Redis/Qdrant ready |
| **Context Engineering** | ⚠️ Partial | Using Gemini 2.5 Flash/Pro, RAG stubbed |
| **Security** | ✅ Complete | Shield Node + tool gating, SPEC-008 compliant |

---

## 5. API Endpoints Implemented

| Endpoint | Method | Status | Purpose |
|----------|--------|--------|---------|
| `/api/v1/health` | GET | ✅ | Health check |
| `/api/v1/shield/check` | POST | ✅ | Security validation |
| `/api/v1/incident` | POST | ✅ | Full triage pipeline |
| `/api/v1/incident/{id}` | GET | ⚠️ Stub | Incident status |
| `/api/v1/webhooks/jira` | POST | ⚠️ Stub | Jira webhook handling |

---

## 6. Technology Stack

**Backend:**
- FastAPI 0.128+ (Python 3.12)
- Gemini 2.5 Flash/Pro (google.genai package)
- OpenRouter (multi-provider support)
- Instructor (structured outputs)
- Redis (state management)
- Qdrant (vector search)

**Frontend:**
- Next.js 14 (scaffolded, not implemented)

**Infrastructure:**
- Docker Compose (Redis, Qdrant)
- uv (package manager)

---

## 7. Security Posture (SPEC-008)

✅ **Hard Gate Implemented**
- Shield validation runs BEFORE all tool access
- Fail-closed: blocks on all LLM errors
- Tool gating: no tools called when is_safe=False

**Test Results:**
```
backend/test_shield.py::15 passed (49.68s)
- 4 valid incidents → PASSED
- 6 attack vectors → BLOCKED
- 2 malicious payloads → HANDLED
- 3 LLM failures → FAIL-CLOSED
```

---

## 8. Next Steps (Priority Order)

1. **Code Search (RAG)** - Implement Qdrant vector search for codebase context
2. **ITSM Bridge** - Implement Jira ticket creation + Slack notifications
3. **Frontend** - Build incident submission UI
4. **E2E Integration** - Connect all components with Redis checkpointing

---

## 9. Git Repository

**Remote:** https://github.com/moebious/agentx-rubrica
**Branch:** `feature/shield-node`
**Recent Commits:**
- `9cfdde1` feat: Implement TriageAgent with Shield-based tool gating
- `30944bd` fix: Make observability tracing conditional on valid API keys
- `236b9aa` fix: Update model names and remove emojis

---

## 4. Mandatory Deliverables

Failure to include these files in our public MIT-licensed repository will result in immediate disqualification.

| File | Purpose |
|------|---------|
| **QUICKGUIDE.md** | How to run the Bunker and the Borde. |
| **.env.example** | Placeholders for Gemini, Jira, Slack, and Redis keys. |
| **AGENTS_USE.md** | (Crucial) Detailed breakdown of:<br>• Agent capabilities and tech stack.<br>• Orchestration logic and error handling.<br>• Evidence of observability and guardrails.<br>• Lessons learned and team reflections. |

---

## 5. Official FAQ & Constraints

| Rule | Details |
|------|---------|
| **English Only** | All code, documentation, and the demo video must be in English (B2+ level). |
| **Public MIT License** | The repo must be public. |
| **No Direct Mentor DMs** | All technical queries must go through #ask-mentors. |
| **Multimodal Requirement** | We MUST use an LLM that supports more than just text. (Gemini 1.5 Pro confirmed). |
