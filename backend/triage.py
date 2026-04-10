"""Rubrica Triage Agent - Intelligent incident analysis and routing.

This module implements the core Triage Agent that:
1. Runs Shield validation first (security gate)
2. Analyzes incident severity and root cause
3. Searches codebase for relevant context (via Librarian)
4. Creates ITSM tickets (via ITSM Bridge)
5. Routes to appropriate response channel

CRITICAL: Tools are ONLY called when Shield.is_safe = True
"""

import os
import json
from typing import List, Optional, Dict, Any
from loguru import logger
from pydantic import BaseModel, Field
from enum import Enum

from shared.schemas import (
    IncidentIntake,
    SecurityCheck,
    TriageResult,
    CodeContext,
    IncidentStatus,
)
from backend.shield import ShieldNode, validate_incident
from backend.db.llm_client import get_instructor_client, get_model_name, get_provider


# ============================================================================
# TRIAGE PROMPT
# ============================================================================

TRIAGE_SYSTEM_PROMPT = """You are an expert SRE Triage Engineer analyzing an incident.

Your task is to:
1. Understand what broke
2. Assess the severity (P0=critical, P1=high, P2=medium, P3=low)
3. Form a root cause hypothesis
4. Identify affected components
5. Suggest next steps

Analyze the incident description and any provided logs/screenshots.

Output your findings as a structured JSON response."""

SEARCH_QUERIES_PROMPT = """You are an expert SRE investigating an incident.

Based on the incident description, generate 3-5 search queries that would help find:
1. Relevant code in the codebase
2. Similar past incidents
3. Configuration files
4. Related services

Output ONLY a list of search queries, one per line."""


# ============================================================================
# TRIAGE AGENT CLASS
# ============================================================================

class TriageAgent:
    """Main Triage Agent with security-gated tool access.

    Security First:
    - Shield validation runs BEFORE any tool calls
    - Tools are ONLY accessible when Shield.is_safe = True
    - Fail-closed: if Shield fails, no tools are called
    """

    def __init__(self):
        """Initialize the Triage Agent."""
        self.provider = get_provider()
        self.triage_model = get_model_name("triage")
        self.shield = ShieldNode()
        logger.info(f"TriageAgent initialized: {self.provider} + {self.triage_model}")

    async def process_incident(self, incident: IncidentIntake) -> Dict[str, Any]:
        """Process an incident through the full triage pipeline.

        Pipeline:
        1. Shield validation (security gate)
        2. If safe: Analyze + search + route
        3. If unsafe: Return blocked response

        Args:
            incident: The incident intake to process

        Returns:
            Dictionary with triage results and security status
        """
        logger.info(f"TriageAgent processing incident: {len(incident.description)} chars")

        # STEP 1: SECURITY GATE (Shield validation)
        logger.info("STEP 1: Running Shield validation...")
        security_check = await self.shield.validate(incident)

        # STEP 2: Check if safe to proceed
        if not security_check.is_safe:
            logger.warning(f"Incident BLOCKED by Shield: {security_check.risk_reasons}")
            return {
                "status": "blocked",
                "security_check": security_check,
                "message": "Incident blocked by security validation. Please rephrase your report.",
                "tools_called": [],  # No tools called when blocked
            }

        logger.info(f"Shield PASSED: risk_score={security_check.risk_score}")

        # STEP 3: Analyze the incident (only if safe)
        logger.info("STEP 2: Analyzing incident with LLM...")
        triage_result = await self._analyze_incident(incident)

        # STEP 4: Search codebase for context (only if safe)
        logger.info("STEP 3: Searching codebase for relevant context...")
        search_queries = await self._generate_search_queries(incident)
        code_contexts = await self._search_codebase(search_queries)

        # Add code contexts to triage result
        triage_result.code_references = code_contexts

        # STEP 5: Determine routing (only if safe)
        logger.info("STEP 4: Determining response routing...")
        routing = self._determine_routing(triage_result)

        result = {
            "status": "success",
            "security_check": security_check,
            "triage_result": triage_result,
            "search_queries": search_queries,
            "routing": routing,
            "tools_called": ["shield", "triage_llm", "code_search"],  # Track tool usage
        }

        logger.success(f"TriageAgent completed: priority={triage_result.priority_level}")
        return result

    async def _analyze_incident(self, incident: IncidentIntake) -> TriageResult:
        """Analyze the incident using the triage LLM.

        Args:
            incident: The incident to analyze

        Returns:
            TriageResult with analysis findings
        """
        provider = get_provider()

        if provider == "google":
            # Use new genai API
            from google.genai import Client
            client = Client(api_key=os.getenv("GEMINI_API_KEY"))

            prompt = self._build_triage_prompt(incident)
            response = client.models.generate_content(
                model="models/gemini-2.5-pro",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": TriageAnalysis.model_json_schema(),
                },
            )
            parsed = json.loads(response.candidates[0].content.parts[0].text)
            analysis = TriageAnalysis(**parsed)

        else:
            # Use OpenRouter/OpenAI format
            client = get_instructor_client("triage")
            analysis = client.messages.create(
                messages=[
                    {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                    {"role": "user", "content": self._build_triage_prompt(incident)},
                ],
                response_model=TriageAnalysis,
            )

        # Convert to TriageResult
        return TriageResult(
            incident_summary=analysis.summary,
            root_cause_hypothesis=analysis.root_cause,
            affected_components=analysis.components,
            priority_level=analysis.priority,
            suggested_fix=analysis.suggested_fix,
            code_references=[],
            confidence_score=analysis.confidence,
        )

    def _build_triage_prompt(self, incident: IncidentIntake) -> str:
        """Build the prompt for triage analysis.

        Args:
            incident: The incident to analyze

        Returns:
            Formatted prompt string
        """
        parts = [
            "Analyze this SRE incident:",
            "",
            f"Description: {incident.description}",
        ]

        if incident.severity:
            parts.append(f"Reported Severity: {incident.severity}")

        if incident.logs_text:
            parts.extend([
                "",
                "Logs:",
                incident.logs_text[:2000],  # Truncate
            ])

        if incident.screenshot_base64:
            parts.append("(Screenshot attached)")

        parts.extend([
            "",
            "Provide: summary, root cause, affected components, priority (P0-P3), confidence (0-1).",
        ])

        return "\n".join(parts)

    async def _generate_search_queries(self, incident: IncidentIntake) -> List[str]:
        """Generate search queries for codebase investigation.

        Args:
            incident: The incident to investigate

        Returns:
            List of search queries
        """
        # For now, use simple keyword extraction
        # TODO: Use LLM to generate better queries
        queries = []

        # Extract key terms from description
        words = incident.description.lower().split()

        # Look for service/component names
        if "checkout" in words:
            queries.append("checkout service")
        if "payment" in words:
            queries.append("payment processing")
        if "database" in words or "db" in words:
            queries.append("database connection")
        if "api" in words:
            queries.append("api endpoint")

        # Add error-specific queries
        if "500" in incident.description or "error" in words:
            queries.append("error handling")
        if "timeout" in words:
            queries.append("timeout configuration")

        return queries[:5] if queries else ["incident", "error", "failure"]

    async def _search_codebase(self, queries: List[str]) -> List[CodeContext]:
        """Search codebase for relevant context using Librarian agent.

        Args:
            queries: Search queries to execute

        Returns:
            List of relevant code contexts
        """
        from backend.librarian import LibrarianAgent

        all_contexts = []
        librarian = LibrarianAgent()

        for query in queries[:3]:  # Limit to top 3 queries
            try:
                contexts = await librarian.search(query, top_k=2)
                all_contexts.extend(contexts)
            except Exception as e:
                logger.warning(f"Search failed for query '{query}': {e}")

        # Deduplicate by file_path and line_numbers
        seen = set()
        unique_contexts = []
        for ctx in all_contexts:
            key = f"{ctx.file_path}:{ctx.line_numbers}"
            if key not in seen:
                seen.add(key)
                unique_contexts.append(ctx)

        # Sort by relevance and return top 5
        unique_contexts.sort(key=lambda x: x.relevance_score, reverse=True)
        return unique_contexts[:5]

    def _determine_routing(self, triage: TriageResult) -> Dict[str, str]:
        """Determine how to route the incident response.

        Args:
            triage: The triage result

        Returns:
            Routing configuration
        """
        routing = {
            "channels": [],
            "ticket_required": False,
            "notify_automatically": False,
        }

        # P0 (Critical) -> All channels
        if triage.priority_level == "P0":
            routing["channels"] = ["slack", "jira", "pagerduty"]
            routing["ticket_required"] = True
            routing["notify_automatically"] = True

        # P1 (High) -> Slack + Jira
        elif triage.priority_level == "P1":
            routing["channels"] = ["slack", "jira"]
            routing["ticket_required"] = True

        # P2 (Medium) -> Jira only
        elif triage.priority_level == "P2":
            routing["channels"] = ["jira"]
            routing["ticket_required"] = True

        # P3 (Low) -> No ticket, just log
        else:
            routing["channels"] = ["log"]

        return routing


# ============================================================================
# INTERNAL ANALYSIS MODEL
# ============================================================================

class TriageAnalysis(BaseModel):
    """Internal model for triage analysis results."""

    summary: str = Field(description="Plain language summary of the incident")
    root_cause: str = Field(description="Best guess at the root cause")
    components: List[str] = Field(description="Affected components or services")
    priority: str = Field(description="Priority level: P0, P1, P2, P3")
    confidence: float = Field(description="Confidence score 0-1", ge=0.0, le=1.0)
    suggested_fix: Optional[str] = Field(default=None, description="Suggested fix based on analysis")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def triage_incident(incident: IncidentIntake) -> Dict[str, Any]:
    """Convenience function to triage an incident.

    Args:
        incident: The incident intake to triage

    Returns:
        Triage results with security status
    """
    agent = TriageAgent()
    return await agent.process_incident(incident)
