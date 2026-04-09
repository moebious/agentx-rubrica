# SPEC-015: docker-compose.yml

**Status:** FINALIZED
**Architecture:** Multi-Container Stack
**Environment:** Production-Ready

---

## Configuration

```yaml
version: '3.8'

services:
  # --- THE BORDE: Frontend (Next.js) ---
  web:
    build:
      context: .
      dockerfile: frontend/Dockerfile
    container_name: rubrica-web
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - api
    restart: always

  # --- THE BUNKER: Backend (FastAPI + LangGraph) ---
  api:
    build:
      context: .
      dockerfile: backend/Dockerfile
    container_name: rubrica-api
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_URL=http://qdrant:6333
    depends_on:
      - redis
      - qdrant
    volumes:
      - ./backend:/app/backend
      - ./shared:/app/shared
    restart: always

  # --- STATE PERSISTENCE: Redis (LangGraph Checkpointer) ---
  redis:
    image: redis:7-alpine
    container_name: rubrica-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: always

  # --- VECTOR INTELLIGENCE: Qdrant (Codebase RAG) ---
  qdrant:
    image: qdrant/qdrant:latest
    container_name: rubrica-qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: always

volumes:
  redis_data:
  qdrant_data:
```

---

## 📂 Critical Configuration Notes

### 1. The Build Context
Notice that both `web` and `api` use the root directory (`.`) as the build context. This is **mandatory** because both services need to import files from the `shared/` directory. If you set the context to `backend/`, the Docker build will fail when it tries to find `shared/schemas.py`.

### 2. Persistence (Volumes)
I have included named volumes (`redis_data` and `qdrant_data`). This ensures that if the judge stops the containers and restarts them, the Saleor index and the Incident history remain intact. This is a massive **"Reliability"** point for the judges.

### 3. Networking
| Port | Purpose |
|------|---------|
| **3000** | Exposed for the user to access the UI. |
| **8000** | Exposed for the UI to talk to the API (and for the judges to explore the `/docs`). |
| **6379/6333** | Exposed locally so you can use external tools (like Redis Insight or Qdrant Dashboard) during the demo if needed. |

### 4. Environment Injection
The `api` service pulls from `.env`. This keeps your Gemini and Jira keys secure. **Never hardcode these.**
