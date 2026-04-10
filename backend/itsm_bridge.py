"""Rubrica ITSM Bridge - Integration with external systems.

This module implements the ITSM Bridge that:
1. Creates Jira tickets from triage results
2. Sends Slack notifications for incident alerts
3. Sends email notifications to reporters on resolution
4. Tracks external system references (ticket IDs, message IDs)

Integrations:
- Jira: Ticket creation and updates
- Slack: Channel notifications and alerts
- Email: Reporter notifications
"""

import os
import asyncio
from typing import Optional, Dict, Any, List
from loguru import logger
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

from shared.schemas import TriageResult, SecurityCheck
from backend.config import get_settings


# ============================================================================
# CONFIGURATION
# ============================================================================

class JiraConfig(BaseModel):
    """Jira integration configuration."""
    domain: str
    user_email: str
    api_token: str
    project_key: str = "INC"
    default_issue_type: str = "Incident"


class SlackConfig(BaseModel):
    """Slack integration configuration."""
    webhook_url: str
    default_channel: str = "#sre-alerts"
    alert_channel: str = "#incidents"


class EmailConfig(BaseModel):
    """Email integration configuration."""
    sendgrid_api_key: Optional[str] = None
    from_email: str = "noreply@sre-rubrica.com"
    from_name: str = "Rubrica SRE Agent"


# ============================================================================
# JIRA INTEGRATION
# ============================================================================

class JiraClient:
    """Client for Jira API operations."""

    def __init__(self, config: JiraConfig):
        """Initialize Jira client.

        Args:
            config: Jira configuration
        """
        self.config = config
        self.base_url = f"https://{config.domain}/rest/api/3"
        self.auth = (config.user_email, config.api_token)

    def is_configured(self) -> bool:
        """Check if Jira is properly configured.

        Returns:
            True if credentials are set and valid
        """
        return (
            self.config.domain and
            self.config.domain != "your-domain.atlassian.net" and
            self.config.user_email and
            self.config.user_email != "your-email@example.com" and
            self.config.api_token and
            self.config.api_token != "your_jira_token_here"
        )

    async def create_ticket(self, triage: TriageResult, incident_description: str) -> Dict[str, Any]:
        """Create a Jira ticket from triage results.

        Args:
            triage: Triage analysis results
            incident_description: Original incident description

        Returns:
            Ticket creation response with ticket ID
        """
        if not self.is_configured():
            logger.warning("Jira not configured, skipping ticket creation")
            return {"success": False, "error": "Jira not configured"}

        try:
            import httpx

            # Build ticket payload
            priority_map = {
                "P0": "Highest",
                "P1": "High",
                "P2": "Medium",
                "P3": "Low",
            }

            payload = {
                "fields": {
                    "project": {"key": self.config.project_key},
                    "summary": f"[{triage.priority_level}] {triage.incident_summary[:50]}...",
                    "description": self._build_ticket_description(triage, incident_description),
                    "issuetype": {"name": self.config.default_issue_type},
                    "priority": {"name": priority_map.get(triage.priority_level, "Medium")},
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/issue",
                    json=payload,
                    auth=self.auth,
                    headers={"Accept": "application/json"},
                )

                if response.status_code == 201:
                    data = response.json()
                    ticket_id = data["key"]
                    logger.info(f"Jira ticket created: {ticket_id}")
                    return {
                        "success": True,
                        "ticket_id": ticket_id,
                        "url": f"https://{self.config.domain}/browse/{ticket_id}",
                    }
                else:
                    logger.error(f"Jira API error: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Failed to create Jira ticket: {e}")
            return {"success": False, "error": str(e)}

    def _build_ticket_description(self, triage: TriageResult, incident_description: str) -> dict:
        """Build Jira ticket description from triage results.

        Args:
            triage: Triage analysis results
            incident_description: Original incident description

        Returns:
            Jira description object
        """
        parts = [
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "h2. Incident Summary", "marks": [{"type": "strong"}]},
                ],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": triage.incident_summary}],
            },
            {"type": "rule"},
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "h2. Root Cause Hypothesis", "marks": [{"type": "strong"}]},
                ],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": triage.root_cause_hypothesis}],
            },
            {"type": "rule"},
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "h2. Affected Components", "marks": [{"type": "strong"}]},
                ],
            },
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": ", ".join(triage.affected_components)}],
            },
            {"type": "rule"},
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "h2. Suggested Fix", "marks": [{"type": "strong"}]},
                ],
            },
        ]

        if triage.suggested_fix:
            parts.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": triage.suggested_fix}],
            })

        parts.append({"type": "rule"})

        # Add code references if available
        if triage.code_references:
            parts.append({
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "h2. Code References", "marks": [{"type": "strong"}]},
                ],
            })

            for ref in triage.code_references[:5]:
                parts.append({
                    "type": "paragraph",
                    "content": [
                        {"type": "text", "text": f"{ref.file_path}:{ref.line_numbers} ", "marks": [{"type": "code"}]},
                        {"type": "text", "text": f"(relevance: {ref.relevance_score:.2f})"},
                    ],
                })

        # Add metadata
        parts.extend([
            {"type": "rule"},
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Confidence: ", "marks": [{"type": "strong"}]},
                    {"type": "text", "text": f"{triage.confidence_score:.0%}"},
                ],
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Priority: ", "marks": [{"type": "strong"}]},
                    {"type": "text", "text": triage.priority_level},
                ],
            },
        ])

        return {"type": "doc", "version": 1, "content": parts}


# ============================================================================
# SLACK INTEGRATION
# ============================================================================

class SlackClient:
    """Client for Slack webhook notifications."""

    def __init__(self, config: SlackConfig):
        """Initialize Slack client.

        Args:
            config: Slack configuration
        """
        self.config = config

    def is_configured(self) -> bool:
        """Check if Slack is properly configured.

        Returns:
            True if webhook URL is set and valid
        """
        return (
            self.config.webhook_url and
            not self.config.webhook_url.startswith("https://hooks.slack.com/services/xxx")
        )

    async def send_alert(
        self,
        triage: TriageResult,
        incident_description: str,
        ticket_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Send incident alert to Slack.

        Args:
            triage: Triage analysis results
            incident_description: Original incident description
            ticket_url: Optional Jira ticket URL

        Returns:
            Notification response
        """
        if not self.is_configured():
            logger.warning("Slack not configured, skipping notification")
            return {"success": False, "error": "Slack not configured"}

        try:
            import httpx

            # Build message
            priority_emoji = {
                "P0": ":rotating_light:",
                "P1": ":warning:",
                "P2": ":information_source:",
                "P3": ":speech_balloon:",
            }

            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{priority_emoji.get(triage.priority_level, '')} New Incident: {triage.priority_level}",
                    },
                },
                {"type": "divider"},
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Summary:*\n{triage.incident_summary}",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Root Cause:*\n{triage.root_cause_hypothesis}",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Affected Components:*\n{', '.join(triage.affected_components)}",
                    },
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Confidence: {triage.confidence_score:.0%} | Reporter: Rubrica SRE Agent",
                        },
                    ],
                },
            ]

            # Add ticket link if available
            if ticket_url:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*< {ticket_url} | View Jira Ticket>*",
                    },
                })

            # Add code references if available
            if triage.code_references:
                code_refs = "\n".join([
                    f"• `{ref.file_path}:{ref.line_numbers}`" for ref in triage.code_references[:3]
                ])
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Code References:*\n{code_refs}",
                    },
                })

            payload = {"blocks": blocks}

            async with httpx.AsyncClient() as client:
                response = await client.post(self.config.webhook_url, json=payload)

                if response.status_code == 200:
                    logger.info("Slack notification sent successfully")
                    return {"success": True, "message": "Notification sent"}
                else:
                    logger.error(f"Slack API error: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return {"success": False, "error": str(e)}


# ============================================================================
# EMAIL INTEGRATION
# =============================================================================

class EmailClient:
    """Client for sending email notifications."""

    def __init__(self, config: EmailConfig):
        """Initialize email client.

        Args:
            config: Email configuration
        """
        self.config = config

    def is_configured(self) -> bool:
        """Check if email is properly configured.

        Returns:
            True if SendGrid API key is set and valid
        """
        return (
            self.config.sendgrid_api_key and
            self.config.sendgrid_api_key != "your_sendgrid_key_here"
        )

    async def send_resolution_notification(
        self,
        to_email: str,
        ticket_id: str,
        resolution: str,
    ) -> Dict[str, Any]:
        """Send resolution notification to reporter.

        Args:
            to_email: Reporter's email address
            ticket_id: Jira ticket ID
            resolution: Resolution description

        Returns:
            Email response
        """
        if not self.is_configured():
            logger.warning("Email not configured, skipping notification")
            return {"success": False, "error": "Email not configured"}

        try:
            import httpx

            payload = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": f"Your incident has been resolved [{ticket_id}]",
                    }
                ],
                "from": {"email": self.config.from_email, "name": self.config.from_name},
                "content": [
                    {
                        "type": "text/plain",
                        "value": self._build_resolution_email(ticket_id, resolution),
                    }
                ],
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.config.sendgrid_api_key}"},
                )

                if response.status_code in [200, 202]:
                    logger.info(f"Resolution email sent to {to_email}")
                    return {"success": True, "message": "Email sent"}
                else:
                    logger.error(f"SendGrid API error: {response.status_code} - {response.text}")
                    return {"success": False, "error": response.text}

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return {"success": False, "error": str(e)}

    def _build_resolution_email(self, ticket_id: str, resolution: str) -> str:
        """Build resolution email body.

        Args:
            ticket_id: Jira ticket ID
            resolution: Resolution description

        Returns:
            Email body
        """
        return f"""
Your incident has been resolved.

Ticket: {ticket_id}

Resolution:
{resolution}

Thank you for reporting this issue. If you have any questions,
please reply to this email or reference the ticket ID.

--
Rubrica SRE Agent
""".strip()


# ============================================================================
# ITSM BRIDGE
# ============================================================================

class ITSMBridge:
    """Bridge to external ITSM systems.

    Orchestrates integrations with Jira, Slack, and Email based on
    triage results and routing configuration.
    """

    def __init__(self):
        """Initialize the ITSM Bridge."""
        settings = get_settings()

        # Initialize clients
        self.jira = JiraClient(JiraConfig(
            domain=settings.jira_domain or "your-domain.atlassian.net",
            user_email=settings.jira_user_email or "your-email@example.com",
            api_token=settings.jira_api_token or "your_jira_token_here",
        ))

        self.slack = SlackClient(SlackConfig(
            webhook_url=settings.slack_webhook_url or "https://hooks.slack.com/services/xxx/yyy/zzz",
        ))

        self.email = EmailClient(EmailConfig(
            sendgrid_api_key=settings.sendgrid_api_key,
        ))

        logger.info("ITSM Bridge initialized")

    async def handle_incident(
        self,
        triage: TriageResult,
        incident_description: str,
        routing: Dict[str, Any],
        reporter_email: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Handle incident by creating tickets and sending notifications.

        Args:
            triage: Triage analysis results
            incident_description: Original incident description
            routing: Routing configuration from TriageAgent
            reporter_email: Optional reporter email for notifications

        Returns:
            Dictionary with ticket IDs and notification status
        """
        results = {
            "ticket_id": None,
            "slack_sent": False,
            "email_sent": False,
            "errors": [],
        }

        # Step 1: Create Jira ticket if required
        if routing.get("ticket_required"):
            logger.info("Creating Jira ticket...")
            ticket_result = await self.jira.create_ticket(triage, incident_description)

            if ticket_result.get("success"):
                results["ticket_id"] = ticket_result["ticket_id"]
                results["ticket_url"] = ticket_result.get("url")
            else:
                error_msg = ticket_result.get("error", "Unknown error")
                results["errors"].append(f"Jira: {error_msg}")
                logger.error(f"Failed to create Jira ticket: {error_msg}")

        # Step 2: Send Slack notifications
        channels = routing.get("channels", [])
        if "slack" in channels or "jira" in channels:
            logger.info("Sending Slack notification...")
            slack_result = await self.slack.send_alert(
                triage,
                incident_description,
                results.get("ticket_url"),
            )

            if slack_result.get("success"):
                results["slack_sent"] = True
            else:
                error_msg = slack_result.get("error", "Unknown error")
                results["errors"].append(f"Slack: {error_msg}")
                logger.error(f"Failed to send Slack notification: {error_msg}")

        # Step 3: Store reporter email for later notification
        if reporter_email:
            results["reporter_email"] = reporter_email
            logger.info(f"Reporter email stored: {reporter_email}")

        return results

    async def notify_resolution(
        self,
        ticket_id: str,
        resolution: str,
        reporter_email: str,
    ) -> Dict[str, Any]:
        """Notify reporter of incident resolution.

        Args:
            ticket_id: Jira ticket ID
            resolution: Resolution description
            reporter_email: Reporter's email address

        Returns:
            Notification status
        """
        logger.info(f"Notifying resolution for ticket {ticket_id}...")

        result = await self.email.send_resolution_notification(
            reporter_email,
            ticket_id,
            resolution,
        )

        if result.get("success"):
            logger.info(f"Resolution notification sent to {reporter_email}")
        else:
            logger.error(f"Failed to send resolution notification: {result.get('error')}")

        return result


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def handle_itsm(
    triage: TriageResult,
    incident_description: str,
    routing: Dict[str, Any],
    reporter_email: Optional[str] = None,
) -> Dict[str, Any]:
    """Convenience function to handle ITSM integrations.

    Args:
        triage: Triage analysis results
        incident_description: Original incident description
        routing: Routing configuration
        reporter_email: Optional reporter email

    Returns:
        ITSM operation results
    """
    bridge = ITSMBridge()
    return await bridge.handle_incident(triage, incident_description, routing, reporter_email)
