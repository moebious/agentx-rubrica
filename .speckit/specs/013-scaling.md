# SPEC-013: SCALING.md

---

# 📈 Scalability & System Evolution: Rubrica

---

## 1. Architectural Scaling Philosophy

Rubrica is built on a **"Stateless Compute, Stateful Memory"** model. By decoupling the execution logic from the incident state, we ensure the system can grow vertically and horizontally without architectural redesign.

---

## 2. Horizontal Scaling (The Bunker)

The FastAPI backend (The Bunker) is designed to be completely stateless.

| Aspect | Implementation |
|--------|----------------|
| **State Externalization** | All LangGraph checkpoints and conversation histories are stored in Redis. |
| **Load Balancing** | We can deploy multiple instances of the Bunker across different regions. Because the state is centralized in Redis, a request can be initiated on Instance A and resumed on Instance B via a Jira Webhook without any data loss. |
| **Concurrency** | Using asynchronous Python (ASGI), a single container can handle hundreds of concurrent triage requests before requiring a replica. |

---

## 3. Context & Intelligence Scaling

One of the primary bottlenecks for SRE agents is codebase growth. Traditional RAG systems degrade as the "noise" in the vector database increases.

| Strategy | Advantage |
|----------|-----------|
| **The 2M Token Advantage** | By utilizing Gemini 1.5 Pro, Rubrica scales with the codebase. Instead of retrieving tiny snippets, we can ingest entire sub-directories (e.g., the entire `saleor/checkout` module). This provides the LLM with full architectural context that traditional RAG cannot match. |
| **Hybrid Retrieval** | Our use of Qdrant allows for horizontal sharding of the vector index. As the Saleor codebase (or multiple repositories) grows, Qdrant can distribute the load across a cluster. |

---

## 4. Technical Decisions & Assumptions

### Decision: Redis vs. Local Memory
| Aspect | Details |
|--------|---------|
| **Reasoning** | Local memory (in-memory sqlite) is the default for LangGraph but fails in production (Railway/Cloud) where containers can restart. We chose Redis to ensure incident persistence during deployment cycles. |

### Decision: Flash vs. Pro Model Split
| Aspect | Details |
|--------|---------|
| **Reasoning** | Scaling isn't just about traffic; it's about cost. We use Gemini 1.5 Flash for the "Shield" and "ITSM" nodes to keep latency low and costs minimal, reserving the expensive Pro model only for high-reasoning triage tasks. |

### Assumption: Human-in-the-Loop
| Aspect | Details |
|--------|---------|
| **Current** | For the current version, we assume a human must resolve the Jira ticket to trigger the "Resume" logic. |
| **Future Scale** | This architecture supports "Autonomous Fixes" (Agentic PRs) by simply adding a new node to the LangGraph that can execute git commands. |

---

## 5. Deployment Scalability

Rubrica is containerized using Docker.

| Component | Deployment Strategy |
|-----------|---------------------|
| **The Borde (Frontend)** | Can be deployed to Edge networks (Vercel/Cloudflare) to reduce latency for global reporters. |
| **The Bunker (Backend)** | Deployed on Railway/Hetzner with auto-scaling triggers based on CPU/RAM usage. |
