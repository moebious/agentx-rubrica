# SPEC-012: AGENTS_USE.md

---

# 🧠 Agent Implementation & Documentation: Rubrica

---

## 1. Agent Overview & Tech Stack

Rubrica is a multi-agent system designed to automate the lifecycle of SRE incidents. It moves beyond simple "chatbots" by utilizing a stateful Directed Acyclic Graph (DAG) that can hibernate and resume based on external technical events.

| Component | Technology |
|-----------|------------|
| **Orchestration** | LangGraph (Stateful Agentic Workflows) |
| **Primary Reasoning Model** | Gemini 1.5 Pro (used for deep-code analysis) |
| **Utility/Security Model** | Gemini 1.5 Flash (used for sub-second guardrails) |
| **Data Validation** | Instructor (Pydantic-enforced LLM outputs) |
| **Memory/State** | Redis (Checkpointing) & Qdrant (Hybrid RAG) |

---

## 2. Agents & Capabilities

| Agent | Role | Model | Capability |
|-------|------|-------|------------|
| **The Shield** | Security Sentry | 1.5 Flash | Filters prompt injections and off-topic requests. |
| **The Supervisor** | Triage Lead | 1.5 Pro | Correlates multimodal logs/images to plan investigation. |
| **The Librarian** | RAG Specialist | 1.5 Pro | Executes Hybrid Search (Vector + BM25) on Saleor repo. |
| **The ITSM Bridge** | Integration | 1.5 Flash | Maps technical data to Jira tickets and Slack alerts. |

---

## 3. Architecture, Orchestration & Error Handling

Rubrica uses LangGraph to manage the incident state.

| Aspect | Implementation |
|--------|----------------|
| **Orchestration** | A cyclic graph where the Supervisor can request more information from the Librarian if the first search results are insufficient. |
| **Wait-State Logic** | When a Jira ticket is created, the graph saves its state to Redis and terminates the active process. It only resumes when a Jira Webhook confirms the ticket is "Resolved." |
| **Error Handling** | We use Instructor's retry logic. If the Librarian returns malformed code context, the Supervisor catches the validation error and re-prompts for a corrected search. |

---

## 4. Context Engineering Approach

We solve the "Massive Codebase" problem using a tiered approach:

| Strategy | Description |
|----------|-------------|
| **Multimodal Fusion** | We pass UI screenshots and server logs in a single prompt turn to Gemini 1.5 Pro. |
| **Hybrid RAG** | We use Qdrant (semantic) to find the right module and BM25 (keyword) to find exact error classes in the Saleor repo. |
| **Long-Context Injection** | Instead of small snippets, we feed the entire failing module (e.g., all files in `saleor/checkout/`) into Gemini's 2M context window to provide full architectural awareness. |

---

## 5. Use Case: "The Checkout Crisis"

| Stage | Description |
|-------|-------------|
| **Intake** | User uploads a "500 Error" screenshot + `TaxError` logs. |
| **Shield** | Validates input as a legitimate technical report. |
| **Triage** | Supervisor identifies a tax calculation mismatch in the checkout module. |
| **Retrieval** | Librarian pulls the `calculations.py` file from the Saleor index. |
| **Action** | A "Critical" Jira ticket is created; Slack notifies the `#sre-alerts` channel. |
| **Resolution** | Once the fix is merged in Jira, the agent wakes up and notifies the reporter. |

---

## 6. Observability (Evidence)

| Platform | Purpose | Evidence |
|----------|---------|----------|
| **Tracing** | LangSmith to visualize the handoffs between nodes. | [INSERT LINK TO YOUR LANGSMITH PUBLIC TRACE HERE] |
| **Metrics** | Opik tracks our token costs and triage latency. | [INSERT SCREENSHOT OF OPIK DASHBOARD SHOWING LATENCY/COST] |

---

## 7. Security & Guardrails (Evidence)

| Layer | Implementation | Evidence |
|-------|----------------|----------|
| **Input Protection** | The Shield Node acts as a semantic firewall. | [INSERT SCREENSHOT OF SHIELD BLOCKING A PROMPT INJECTION ATTACK] |
| **Output Protection** | All tool calls are gated by Pydantic schemas. The agent cannot "guess" Jira fields; it must conform to the defined enums. |

---

## 8. Scalability & Reflections

| Topic | Details |
|-------|---------|
| **Scalability** | Horizontal scaling is achieved via the Redis checkpointer. Any instance of the Bunker can resume any incident thread. |
| **Lessons Learned** | The multimodal correlation between UI and Logs was the most significant "Aha!" moment—vision provides the what, while logs provide the why. |
| **Reflection** | Moving the codebase search to a specialized "Librarian" agent significantly reduced the hallucination rate compared to a single-agent approach. |
