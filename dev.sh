#!/bin/bash
# Rubrica Development Environment Helper Script for Colima

# Set Docker host to Colima
export DOCKER_HOST=unix:///Users/moebious/.colima/default/docker.sock

# Activate Python virtual environment
source ./venv/bin/activate

# Show menu
case "$1" in
    start)
        echo "🚀 Starting infrastructure services..."
        docker compose up -d redis qdrant
        ;;
    stop)
        echo "🛑 Stopping infrastructure services..."
        docker compose down
        ;;
    status)
        echo "📊 Service status:"
        docker compose ps
        echo ""
        echo "Redis: $(curl -s http://localhost:6379 2>&1 | head -1 || echo 'Not reachable')"
        echo "Qdrant: $(curl -s http://localhost:6333/collections | jq -r '.status' 2>/dev/null || echo 'Not reachable')"
        ;;
    backend)
        echo "🔧 Starting FastAPI backend..."
        uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
        ;;
    frontend)
        echo "🎨 Starting Next.js frontend..."
        cd frontend && npm run dev
        ;;
    *)
        echo "Rubrica Development Commands:"
        echo "  ./dev.sh start   - Start Redis + Qdrant"
        echo "  ./dev.sh stop    - Stop all services"
        echo "  ./dev.sh status  - Check service status"
        echo "  ./dev.sh backend - Start FastAPI backend"
        echo "  ./dev.sh frontend- Start Next.js frontend"
        ;;
esac
