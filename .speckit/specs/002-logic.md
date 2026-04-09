# SPEC-002: Operational Workflow & Optimization

**Project:** Rubrica SRE Agent
**Version:** 1.0
**Status:** SELLADO

**Focus:** Reliability, Search Precision, and Critical Path Execution.

---

## 1. The "Instructor" Protocol (Logic Reliability)

We are moving away from raw string parsing. All LLM interactions that require data extraction must use the **Instructor** library to bridge Gemini 1.5 and our Pydantic models.

**The Change:** We utilize `instructor.from_gemini()` to patch the Gemini client.

**Why:** In a 48-hour sprint, we cannot waste time debugging `JSONDecodeError`. Instructor provides automatic retries with feedback—if the LLM returns invalid JSON or misses a field, Instructor sends the error back to the LLM to "self-correct" before the Python code ever sees it.

**Engineering Standard:** No node in LangGraph shall pass raw text to the next node. All state transitions must be governed by an Instructor-validated Pydantic object.

---

## 2. Hybrid Retrieval Strategy (Context Injection)

Codebases are not like natural language; they are full of specific, non-semantic tokens (variable names, error codes). Pure vector search is insufficient for SRE work.

**The Strategy:** Dual-Threat Search.

| Search Type | Technology | Purpose |
|-------------|------------|---------|
| **Vector Search** | Qdrant | Handles semantic queries like "How does the payment flow work?" |
| **Keyword Search** | BM25 | Handles exact matches like `AttributeError: 'NoneType' object` or `get_checkout_context()`. |

**The Implementation:** Our Codebase MCP Server will execute both searches in parallel and merge the results (Reranking) before feeding them to the Triage Supervisor. This ensures the Agent never "guesses" which file contains a specific error code.

---

## 3. Observability Consolidation

To avoid "Dashboard Fatigue," we are prioritizing our observability stack based on the Value to Judges:

| Tool | Priority | Mission |
|------|----------|---------|
| **LangSmith** | CRITICAL | Visualizes the "Thinking Graph." This is our primary demo tool to show the Supervisor/Worker loops. |
| **Opik** | HIGH | Used for LLM Evals. We will use Opik to prove that Rubrica's triage is statistically accurate compared to manual human triage. |
| **Sentry** | MEDIUM | Standard error tracking. Only for "Hard Crashes" (e.g., "Hetzner VPS is down" or "Redis Connection Refused"). |

---

## 4. The Refined "Rubrica" Workflow (The Happy Path)

This is the sequence of state transitions within our LangGraph execution.

### Stage A: The Intake & Shield
1. **FastAPI Entry:** Receives multimodal payload (Text + Image + Logs).
2. **NeMo Guardrails:** Validates the input. If a "Prompt Injection" is detected, the graph terminates immediately with a 403.
3. **Instructor Parsing:** Gemini Flash extracts core technical markers from the screenshot and logs into an `InitialAssessment` model.

### Stage B: Deep Triage (The Sub-Graph)
1. **Triage Supervisor:** Analyzes the `InitialAssessment` and delegates tasks.
2. **Codebase MCP:** Performs Hybrid Search (Vector + Keyword) on the Saleor repository.
3. **Synthesis:** Gemini Pro uses the retrieved code to build a `TriageResult` (Root Cause, Affected Files, Priority).

### Stage C: Action & Hibernation
1. **ITSM MCP:** Creates the Jira/Linear ticket and posts the Slack alert.
2. **Redis Checkpoint:** The graph saves the current `thread_id` and state to Redis.
3. **The Wait State:** The graph enters a "suspended" mode. It is no longer consuming CPU/RAM, but is waiting for a webhook.

### Stage D: The Resolution Loop
1. **Jira Webhook:** When an engineer closes the ticket, Jira hits our Cloudflare Tunnel URL.
2. **Resumption:** FastAPI uses the `thread_id` to pull the state from Redis and "wakes up" LangGraph.
3. **Reporter Notify:** The final node sends the resolution email via the ITSM MCP.

---

## 5. Deployment Guardrails

- **Zero-Inbound Policy:** No ports open on the Hetzner VPS. All traffic (API and Webhooks) flows through the Cloudflare Tunnel.
- **Rate-Limit Backoff:** Because we are on the Gemini Free Tier (2 RPM for Pro), the LangGraph nodes must implement Exponential Backoff to ensure the demo doesn't fail if we run multiple incidents in a row.

---

## CTO's Closing Statement

SPEC-002 provides the tactical edge. By using Instructor and Hybrid Search, we eliminate the two biggest points of failure in AI agents: broken JSON and bad context.
