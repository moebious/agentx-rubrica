# 🧠 Agent Implementation & Documentation: Rubrica

## 📋 Agent Overview & Tech Stack

Rubrica is a multi-agent system designed to automate the lifecycle of SRE incidents.

| Component | Technology |
|-----------|------------|
| **Orchestration** | LangGraph (Stateful Agentic Workflows) |
| **Primary Reasoning Model** | OpenRouter (Gemini 2.5 Pro, Claude 3.5, etc.) |
| **Utility/Security Model** | OpenRouter (Gemini 2.5 Flash, Claude Haiku, etc.) |
| **Data Validation** | Instructor (Pydantic-enforced LLM outputs) |
| **Memory/State** | Redis (Checkpointing) & Qdrant (Hybrid RAG) |

## 🤖 Agents & Capabilities

| Agent | Role | Model | Capability |
|-------|------|-------|------------|
| **The Shield** | Security Sentry | 2.5 Flash / Claude Haiku | Filters prompt injections and off-topic requests. |
| **The Triage Agent** | Lead Investigator | 2.5 Pro / Claude 3.5 Sonnet | Correlates multimodal logs/images to plan investigation. |

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
