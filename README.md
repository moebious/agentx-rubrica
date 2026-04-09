# 🛡️ Rubrica: The Autonomous SRE Layer for Saleor

**AgentX Hackathon 2026 Submission** | **Project Rubrica**

Rubrica is a production-ready, stateful SRE Incident Intake & Triage Agent designed specifically for the Saleor e-commerce ecosystem. It bridges the gap between chaotic failure reports and structured technical resolution by combining multimodal intelligence with agentic orchestration.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/rubrica.git
cd rubrica

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Start all services
docker compose up --build

# Ingest sample codebase (when implemented)
docker compose exec api python scripts/ingest_sample.py
```

## 📊 Tech Stack

| Layer | Technology |
|-------|------------|
| **LLMs** | Google Gemini 2.5 Pro & Flash |
| **Backend** | FastAPI (Python 3.12) |
| **Frontend** | Next.js 14 |
| **State** | Redis |
| **Memory** | Qdrant (Vector DB) |
| **Observability** | LangSmith |

## 🏗️ Architecture

```
User uploads via Next.js UI
    ↓
Shield validates (Gemini Flash)
    ↓
Triage analyzes (Gemini Pro + Qdrant)
    ↓
Store in Redis
    ↓
Inline notification
```

## 📝 Project Status

🚧 **Under Construction - Initial Skeleton**

This is the initial scaffolding for the Rubrica SRE Agent. The core architecture is in place, but implementation is ongoing.

### Completed
- ✅ Monorepo structure
- ✅ Shared Pydantic schemas
- ✅ Docker infrastructure
- ✅ FastAPI backend skeleton
- ✅ Next.js frontend skeleton
- ✅ Environment configuration

### In Progress
- 🔄 Shield Node implementation
- 🔄 Triage Agent implementation
- 🔄 Qdrant integration
- 🔄 Sample codebase ingestion

### TODO
- ⏳ ITSM integrations (Jira/Slack)
- ⏳ LangSmith observability
- ⏳ Complete frontend intake form
- ⏳ Documentation completion

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

**Built for the AgentX Hackathon 2026**
