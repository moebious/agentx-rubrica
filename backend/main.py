"""Rubrica SRE Agent - FastAPI Backend.

The main entry point for the Rubrica API.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from shared.schemas import HealthResponse, IncidentIntake, SecurityCheck


# Configure logger
logger.remove()
logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Rubrica SRE Agent")

    # Startup diagnostics for demo reliability
    try:
        import os
        from pathlib import Path
        from backend.config import get_settings

        settings = get_settings()

        env_root = os.getenv("CODEBASE_ROOT")
        fallback_root = (Path.cwd() / "codebase").resolve()
        resolved_root = None
        if env_root:
            resolved_root = Path(env_root).expanduser().resolve()
        elif fallback_root.exists():
            resolved_root = fallback_root

        logger.info(f"CODEBASE_ROOT env: {env_root!r}")
        if resolved_root is None:
            logger.warning(
                "No codebase root resolved. Set CODEBASE_ROOT or create ./codebase to enable RAG indexing."
            )
        else:
            logger.info(f"Resolved codebase root: {str(resolved_root)} (exists={resolved_root.exists()})")

        logger.info(f"Qdrant URL: {settings.qdrant_url}")
        try:
            from backend.db.qdrant_client import get_qdrant_client
            from backend.librarian import COLLECTION_NAME

            qdrant = get_qdrant_client()
            info = qdrant.get_collection(COLLECTION_NAME)
            logger.info(f"Qdrant collection '{COLLECTION_NAME}': points={info.points_count}")
        except Exception as e:
            logger.warning(f"Qdrant stats unavailable: {e}")

    except Exception as e:
        logger.warning(f"Startup diagnostics skipped: {e}")

    logger.info("Rubrica is ready")
    yield
    logger.info("Shutting down Rubrica SRE Agent")


# Create FastAPI app
app = FastAPI(
    title="Rubrica SRE Agent",
    description="Autonomous SRE Incident Intake & Triage Agent for Saleor",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        services={
            "redis": "unknown",
            "qdrant": "unknown",
            "llm": "unknown",
        },
    )


# ============================================================================
# INCIDENT ENDPOINTS
# ============================================================================

@app.post("/api/v1/incident", tags=["Incidents"])
async def submit_incident(incident: IncidentIntake):
    """Submit a new incident for triage.

    This endpoint:
    1. Runs Shield validation (security gate)
    2. If safe: Analyzes incident, searches codebase, handles ITSM integrations
    3. If unsafe: Returns blocked response

    Tools are ONLY called when Shield validation passes.
    """
    from backend.triage import triage_incident

    result = await triage_incident(incident)

    # Return appropriate response based on security check
    if result["status"] == "blocked":
        return {
            "status": "blocked",
            "message": result["message"],
            "security_check": result["security_check"],
        }

    triage = result["triage_result"]

    response = {
        "status": "success",
        "incident_id": "inc-" + str(hash(incident.description))[:8],
        "security": result["security_check"],
        "triage": triage,
        "routing": result["routing"],
        "tools_called": result["tools_called"],
        "citations": [
            {
                "path": ref.file_path,
                "language": ref.language,
                "snippet": ref.code_snippet,
                "score": ref.relevance_score,
                "line_numbers": ref.line_numbers,
            }
            for ref in (triage.code_references or [])
        ],
    }

    # Add ITSM results if available
    if "itsm" in result:
        response["itsm"] = {
            "ticket_id": result["itsm"].get("ticket_id"),
            "ticket_url": result["itsm"].get("ticket_url"),
            "jira": result["itsm"].get("jira"),
            "slack": result["itsm"].get("slack"),
            "email": result["itsm"].get("email"),
            "slack_sent": result["itsm"].get("slack_sent"),
            "email_sent": result["itsm"].get("email_sent"),
            "errors": result["itsm"].get("errors", []),
        }

    return response


@app.get("/api/v1/incident/{incident_id}", tags=["Incidents"])
async def get_incident(incident_id: str):
    """Get the status of an incident."""
    return {"message": "Not implemented yet"}


# ============================================================================
# WEBHOOK ENDPOINTS (TODO: Implement)
# ============================================================================

@app.post("/api/v1/webhooks/jira", tags=["Webhooks"])
async def jira_webhook():
    """Handle Jira webhook for ticket resolution."""
    return {"message": "Not implemented yet"}


# ============================================================================
# SHIELD ENDPOINTS
# ============================================================================

@app.post("/api/v1/shield/check", response_model=SecurityCheck, tags=["Security"])
async def shield_check(incident: IncidentIntake):
    """Validate incident input for security threats.

    This endpoint uses the Shield Node to detect:
    - Prompt injection attacks
    - System probing attempts
    - Off-topic or spam submissions
    - Malicious code payloads

    Returns a SecurityCheck with risk assessment.
    """
    from backend.shield import validate_incident

    return await validate_incident(incident)


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Rubrica SRE Agent",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
