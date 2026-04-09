# 🧠 Agent Implementation & Documentation: Rubrica

## 📋 Agent Overview & Tech Stack

Rubrica is a multi-agent system designed to automate the lifecycle of SRE incidents.

| Component | Technology |
|-----------|------------|
| **Orchestration** | LangGraph (Stateful Agentic Workflows) |
| **Primary Reasoning Model** | Gemini 1.5 Pro (deep-code analysis) |
| **Utility/Security Model** | Gemini 1.5 Flash (sub-second guardrails) |
| **Data Validation** | Instructor (Pydantic-enforced LLM outputs) |
| **Memory/State** | Redis (Checkpointing) & Qdrant (Hybrid RAG) |

## 🤖 Agents & Capabilities

| Agent | Role | Model | Capability |
|-------|------|-------|------------|
| **The Shield** | Security Sentry | 1.5 Flash | Filters prompt injections and off-topic requests. |
| **The Triage Agent** | Lead Investigator | 1.5 Pro | Correlates multimodal logs/images to plan investigation. |

## 🔄 Architecture & Error Handling

| Aspect | Implementation |
|--------|----------------|
| **Orchestration** | Linear graph: Shield → Triage → Action |
| **Error Handling** | Instructor's retry logic for validation failures |

## 📊 Observability

| Platform | Purpose | Evidence |
|----------|---------|----------|
| **LangSmith** | Visualize agent reasoning | [TODO: Add trace link] |

## 🛡️ Security

| Layer | Implementation |
|-------|----------------|
| **Input Protection** | Shield Node acts as semantic firewall |
| **Output Protection** | All tool calls gated by Pydantic schemas |

## 📈 Scalability

| Topic | Details |
|---------|---------|
| **Scalability** | Horizontal scaling via Redis checkpointer |
| **Lessons Learned** | Multimodal correlation is key |

---

**🚧 Documentation under construction - Full implementation in progress**
