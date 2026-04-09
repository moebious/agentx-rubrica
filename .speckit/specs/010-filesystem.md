# SPEC-010: Project Filesystem & Monorepo Structure

**Status:** MANDATORY
**Pattern:** Flattened Monorepo
**Focus:** Deployment & Data Integrity

---

## 1. The "Single Source of Truth" Design

We are avoiding the most common hackathon error: duplicating code between the frontend and backend.

| Component | Purpose |
|-----------|---------|
| **The `shared/` Folder** | This is our most critical directory. By placing `schemas.py` here, we ensure that the Bunker (FastAPI) and the Borde (Next.js) speak the exact same language. If a field name changes in the backend, the frontend build will fail immediately, preventing "silent failures" during the live demo. |

---

## 2. The Bunker (Backend) Hierarchy

| File | Purpose |
|------|---------|
| **`graph.py`** | The "Central Nervous System." This is where the LangGraph logic lives. |
| **`shield.py`** | The "Firewall." We keep the security logic isolated so it can be audited or replaced without touching the core triage intelligence. |
| **`tools.py`** | The "Hands." This is where we implement the FastMCP integrations for Jira and the Hybrid Search logic for Saleor. |

---

## 3. The Borde (Frontend) Hierarchy

| Directory | Purpose |
|-----------|---------|
| **App Router (`app/`)** | We use Next.js 14 for speed. The "Intake" page handles the multimodal uploads, while the "Dashboard" shows the real-time status of the LangGraph state. |
| **`lib/`** | This will house our auto-generated API client. |

---

## 4. Automation & Dev-Ops

| File | Purpose |
|------|---------|
| **`scripts/ingest_saleor.py`** | This script is our "Pre-computation" engine. It takes the Saleor codebase, chunks it, and populates Qdrant. Without this, our agent is "blind." |
| **`docker-compose.yml`** | The "Dev-Environment-in-a-Box." This allows us to test Redis, Qdrant, and the API locally with one command before we trust the Railway cloud deployment. |

---

## 📂 The Final Locked Structure

```
rubrica/
├── backend/                # The Bunker: Logic & State
├── frontend/               # The Borde: UX & Visualization
├── shared/                 # Shared Pydantic Schemas
├── scripts/                # Indexing & Maintenance
├── .env.example            # The Secret Map
├── AGENTS_USE.md           # The Evaluation Document
└── QUICKGUIDE.md           # The Judge's Manual
```
