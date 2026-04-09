# SPEC-017: Dockerfile(s)

**Status:** OPERATIONAL
**Focus:** Multi-Stage Builds & Dependency Isolation

---

## 1. The Bunker (Backend Dockerfile)

**Path:** `backend/Dockerfile`

This container runs our FastAPI engine and LangGraph logic. We install the requirements and then copy the `backend/` and `shared/` directories.

```dockerfile
# Use a slim Python 3.12 image for a smaller footprint
FROM python:3.12-slim

# Set environment variables to prevent Python from buffering logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code AND the shared directory
COPY backend/ ./backend
COPY shared/ ./shared

# Ensure the app can find the shared module
ENV PYTHONPATH=/app

# Expose the FastAPI port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 2. The Borde (Frontend Dockerfile)

**Path:** `frontend/Dockerfile`

We use a multi-stage build. The first stage builds the Next.js app using Node/Bun, and the second stage serves it. This reduces the image size by ~80%.

```dockerfile
# Stage 1: Building the application
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies based on the preferred package manager
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy the frontend code AND the shared directory
# Next.js may need the schemas for static type checking/generation
COPY frontend/ .
COPY shared/ ./shared

# Build the Next.js application
RUN npm run build

# Stage 2: Production server
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production

# Copy only the necessary files from the builder
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Expose the Next.js port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
```

---

## 📂 Critical Deployment Notes

| Aspect | Details |
|--------|---------|
| **Shared Visibility** | Notice both files copy the `shared/` directory. This is why our `docker-compose.yml` uses the root as the context. |
| **Environment Variables** | We don't hardcode keys here. Docker will pull them from the `.env` via the compose file. |
| **Optimization** | The `api` Dockerfile uses `--no-cache-dir` to keep the image slim, which is crucial for fast deployments on Railway. |
