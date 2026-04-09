#!/bin/bash
# Rubrica Development Environment Helper Script for Colima

# Set Docker host to Colima
export DOCKER_HOST=unix:///Users/moebious/.colima/default/docker.sock

# Activate Python virtual environment
source .venv/bin/activate

# Show menu
case "$1" in
    start)
        echo "🚀 Starting infrastructure services..."
        $HOME/.local/bin/uv run docker compose up -d redis qdrant
        ;;
    stop)
        echo "🛑 Stopping infrastructure services..."
        $HOME/.local/bin/uv run docker compose down
        ;;
    status)
        echo "📊 Service status:"
        $HOME/.local/bin/uv run docker compose ps
        echo ""
        echo "Redis: $(redis-cli -h localhost -p 6379 ping 2>/dev/null || echo 'Not reachable')"
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
    test-api)
        echo "🧪 Testing OpenRouter API..."
        python test_openrouter.py
        ;;
    shell)
        echo "🐚 Entering Python shell with Rubrica environment..."
        python
        ;;
    *)
        echo "Rubrica Development Commands:"
        echo "  ./dev.sh start   - Start Redis + Qdrant"
        echo "  ./dev.sh stop    - Stop all services"
        echo "  ./dev.sh status  - Check service status"
        echo "  ./dev.sh backend - Start FastAPI backend (hot-reload)"
        echo "  ./dev.sh frontend- Start Next.js frontend (hot-reload)"
        echo "  ./dev.sh test-api- Test OpenRouter API connectivity"
        echo "  ./dev.sh shell   - Enter Python shell"
        ;;
esac
