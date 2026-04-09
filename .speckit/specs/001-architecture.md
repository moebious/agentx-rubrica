# SPEC-001: Rubrica System Architecture

**Project:** Rubrica SRE Incident Intake & Triage Agent
**Version:** 1.0
**Status:** SEALED & MANDATORY

**Principles:** Typed E2E, Deterministic Orchestration, Zero-Trust AI, Deep Observability.

---

## 1. Executive Summary

Rubrica is a production-grade SRE agent designed to automate the gap between a messy user failure report and a technical root-cause resolution. It leverages a stateful, multimodal pipeline to ingest reports, search a complex codebase (Saleor), and manage the lifecycle of an incident ticket through resolution.

---

## 2. The Bunker: Backend (Python Core)

The backend is a containerized, asynchronous powerhouse focused on reliability and state management.

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Framework | FastAPI | Asynchronous I/O for concurrent LLM and API calls. |
| Orchestrator | LangGraph | Manages the cyclic SRE workflow (Intake → Triage → Wait → Resolve). |
| Logic Layer | Instructor | Enforces strict Pydantic model compliance for all LLM outputs. |
| Persistence | Redis | Checkpointing for LangGraph states to allow for long-running "Wait" loops. |
| Vector Engine | Qdrant | High-performance local embedding storage for Codebase RAG. |
| Data Contracts | Pydantic v2 | Unified source of truth for all schemas (API, State, and Tools). |
| Logging | Loguru | Structured, asynchronous logging for real-time terminal debugging. |

---

## 3. El Borde: Frontend (Edge Runtime)

The frontend focuses on low-latency intake and a premium "Internal Tool" aesthetic.

- **Framework:** Next.js 14+ (App Router) for server-side optimizations.
- **Runtime:** Bun 1.1+ for 10x faster installation and build cycles.
- **UI Foundation:** Tailwind CSS + shadcn/ui for an accessible, professional aesthetic.
- **Contract Sync:** Auto-generated TS Client via FastAPI's OpenAPI spec to ensure frontend/backend parity.

---

## 4. The Intelligence Layer (AI & Tooling)

We utilize a decoupled tool architecture to keep the "Brain" clean and the "Hands" specialized.

- **Primary LLM:** Gemini 1.5 Pro/Flash (via Google AI Studio).
  - **Flash:** Rapid multimodal intake and initial parsing.
  - **Pro:** Deep-context code analysis and technical synthesis.

- **Tooling Protocol:** Python FastMCP.
  - **MCP-1 (ITSM):** Jira/Linear and Slack/Discord integration.
  - **MCP-2 (Codebase):** Hybrid Retrieval (Qdrant Vector + BM25 Keyword Search).

- **Security Barrier:** NeMo Guardrails. Intercepts prompt injection and off-topic requests before they hit the LLM.

---

## 5. Infrastructure & Observability (The Metal)

We optimize for "Zero-Downtime Demos" and verifiable engineering.

- **Hosting:** Hetzner CX22 VPS (4GB RAM) running Docker Compose.
- **Networking:** Cloudflare Tunnels to expose the API and receive Jira webhooks without opening ports.
- **CI/CD:** GitHub Actions for automated linting, testing, and deployment.
- **Observability (Macro):** LangSmith for tracing the LangGraph state machine flow.
- **Observability (Micro):** Opik for tracking prompt costs, latency, and agent evaluation scores.
- **Alerting:** Sentry for catching unhandled hardware or API-level exceptions.

---

## 6. Implementation Principles

1. **Strict Typing:** No `dict` or `Any` in the core logic. Everything is a Pydantic model.
2. **Fail Fast:** Use `pydantic-settings` to crash the server immediately if `.env` keys are missing.
3. **Hybrid Search:** Never rely on vector search alone for code; always provide keyword search for exact function/file matching.
4. **Trace Everything:** If it isn't in LangSmith or Opik, it didn't happen.

---

## CTO's Closing Statement

This is the most robust stack possible for this hackathon. We have eliminated the "toy demo" risk by implementing Redis persistence and Cloudflare Tunnels.

**SPEC-001 is now the law of the repo.**

*Shall we move to create the `schemas.py` file to define the Pydantic data contracts that will govern our "Bunker" and "Borde"?*
