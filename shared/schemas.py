"""Shared Pydantic schemas for Rubrica SRE Agent.

This file defines the data contracts used across both backend (FastAPI)
and frontend (Next.js). All changes here require corresponding frontend
updates to maintain type safety.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ============================================================================
# INCIDENT INTAKE & SUBMISSION
# ============================================================================

class IncidentIntake(BaseModel):
    """Initial incident submission from the user."""

    description: str = Field(
        ...,
        description="User's description of the issue",
        min_length=10,
        max_length=5000,
    )

    screenshot_base64: Optional[str] = Field(
        None,
        description="Base64-encoded screenshot of the issue",
    )

    logs_text: Optional[str] = Field(
        None,
        description="Raw log text from the user",
    )

    reporter_email: Optional[str] = Field(
        None,
        description="Email for resolution notification",
    )

    severity: Optional[str] = Field(
        "medium",
        description="User-reported severity: low, medium, high, critical",
    )


# ============================================================================
# SECURITY & VALIDATION
# ============================================================================

class SecurityCheck(BaseModel):
    """Output from Shield Node security validation."""

    is_safe: bool = Field(
        ...,
        description="Whether the input passed security validation",
    )

    risk_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Risk score (0 = safe, 100 = definitely malicious)",
    )

    risk_reasons: List[str] = Field(
        default_factory=list,
        description="Specific security concerns detected",
    )

    blocked_content: Optional[str] = Field(
        None,
        description="The specific content that was blocked",
    )


# ============================================================================
# TRIAGE & INVESTIGATION
# ============================================================================

class InvestigationPlan(BaseModel):
    """Plan for investigating the incident."""

    search_queries: List[str] = Field(
        ...,
        description="Search queries for the codebase",
    )

    modules_to_investigate: List[str] = Field(
        ...,
        description="Code modules that need investigation",
    )

    suspected_components: List[str] = Field(
        ...,
        description="Components suspected to be involved",
    )


class CodeContext(BaseModel):
    """Relevant code snippets retrieved from the codebase."""

    file_path: str = Field(
        ...,
        description="Path to the file in the codebase",
    )

    language: str = Field(
        ...,
        description="Programming language",
    )

    code_snippet: str = Field(
        ...,
        description="Relevant code snippet",
    )

    line_numbers: Optional[str] = Field(
        None,
        description="Line numbers (e.g., '42-56')",
    )

    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Relevance score from search",
    )


class TriageResult(BaseModel):
    """Final triage result with technical summary."""

    incident_summary: str = Field(
        ...,
        description="Plain language summary of the incident",
    )

    root_cause_hypothesis: str = Field(
        ...,
        description="Best guess at the root cause",
    )

    affected_components: List[str] = Field(
        ...,
        description="Components affected by the issue",
    )

    priority_level: str = Field(
        ...,
        description="Priority: P0 (critical), P1, P2, P3",
    )

    suggested_fix: Optional[str] = Field(
        None,
        description="Suggested fix based on analysis",
    )

    code_references: List[CodeContext] = Field(
        default_factory=list,
        description="Relevant code snippets",
    )

    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in the triage result",
    )


# ============================================================================
# INCIDENT STATE & TRACKING
# ============================================================================

class IncidentStatus(str, Enum):
    """Status of an incident in the workflow."""

    SUBMITTED = "submitted"
    VALIDATING = "validating"
    TRIAGING = "triaging"
    INVESTIGATING = "investigating"
    ACTION_REQUIRED = "action_required"
    RESOLVED = "resolved"
    FAILED = "failed"


class IncidentState(BaseModel):
    """Current state of an incident in the system."""

    incident_id: str = Field(
        ...,
        description="Unique incident identifier",
    )

    status: IncidentStatus = Field(
        default=IncidentStatus.SUBMITTED,
        description="Current status",
    )

    intake: IncidentIntake = Field(
        ...,
        description="Original incident submission",
    )

    security_check: Optional[SecurityCheck] = Field(
        None,
        description="Security validation result",
    )

    triage_result: Optional[TriageResult] = Field(
        None,
        description="Final triage result",
    )

    ticket_id: Optional[str] = Field(
        None,
        description="External ticket ID (Jira, etc.)",
    )

    slack_message_id: Optional[str] = Field(
        None,
        description="Slack message ID",
    )

    error_message: Optional[str] = Field(
        None,
        description="Error if status is FAILED",
    )

    created_at: str = Field(
        ...,
        description="ISO timestamp of creation",
    )

    updated_at: str = Field(
        ...,
        description="ISO timestamp of last update",
    )


# ============================================================================
# API RESPONSE MODELS
# ============================================================================

class IncidentSubmissionResponse(BaseModel):
    """Response when submitting an incident."""

    incident_id: str = Field(
        ...,
        description="Unique incident identifier",
    )

    status: IncidentStatus = Field(
        ...,
        description="Initial status",
    )

    message: str = Field(
        ...,
        description="User-facing message",
    )


class IncidentStatusResponse(BaseModel):
    """Response when checking incident status."""

    incident: IncidentState = Field(
        ...,
        description="Current incident state",
    )

    langsmith_trace_url: Optional[str] = Field(
        None,
        description="Link to LangSmith trace if available",
    )


# ============================================================================
# HEALTH & SYSTEM STATUS
# ============================================================================

class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(
        ...,
        description="System status: healthy, degraded, or unhealthy",
    )

    version: str = Field(
        ...,
        description="API version",
    )

    services: dict = Field(
        ...,
        description="Status of dependent services",
    )


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "IncidentIntake",
    "SecurityCheck",
    "InvestigationPlan",
    "CodeContext",
    "TriageResult",
    "IncidentStatus",
    "IncidentState",
    "IncidentSubmissionResponse",
    "IncidentStatusResponse",
    "HealthResponse",
]
