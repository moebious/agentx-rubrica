"""Test cases for ITSM Bridge integration.

Tests cover:
1. Jira ticket creation (with mock)
2. Slack notifications (with mock)
3. Email notifications (with mock)
4. Integration with TriageAgent
5. Error handling when services are not configured
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import ValidationError

from backend.itsm_bridge import (
    JiraClient,
    SlackClient,
    EmailClient,
    ITSMBridge,
    handle_itsm,
    JiraConfig,
    SlackConfig,
    EmailConfig,
)
from shared.schemas import TriageResult, CodeContext


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_triage_result():
    """Sample triage result for testing."""
    return TriageResult(
        incident_summary="Payment gateway timeout during checkout",
        root_cause_hypothesis="Payment service is experiencing connectivity issues",
        affected_components=["payment-gateway", "checkout-service"],
        priority_level="P1",
        suggested_fix="Check payment service health and restart if needed",
        code_references=[
            CodeContext(
                file_path="src/payment/service.py",
                language="python",
                code_snippet="def process_payment():\n    timeout = 30",
                line_numbers="42-45",
                relevance_score=0.9,
            )
        ],
        confidence_score=0.85,
    )


@pytest.fixture
def sample_routing():
    """Sample routing configuration."""
    return {
        "channels": ["slack", "jira"],
        "ticket_required": True,
        "notify_automatically": False,
    }


# ============================================================================
# JIRA CLIENT TESTS
# ============================================================================

class TestJiraClient:
    """Test Jira client functionality."""

    def test_not_configured(self):
        """Test that unconfigured Jira client returns False."""
        config = JiraConfig(
            domain="your-domain.atlassian.net",
            user_email="your-email@example.com",
            api_token="your_jira_token_here",
        )
        client = JiraClient(config)

        assert not client.is_configured()

    def test_configured(self):
        """Test that configured Jira client returns True."""
        config = JiraConfig(
            domain="company.atlassian.net",
            user_email="user@company.com",
            api_token="real_token_here",
        )
        client = JiraClient(config)

        assert client.is_configured()

    @pytest.mark.asyncio
    async def test_create_ticket_when_not_configured(self, sample_triage_result):
        """Test that ticket creation is skipped when not configured."""
        config = JiraConfig(
            domain="your-domain.atlassian.net",
            user_email="your-email@example.com",
            api_token="your_jira_token_here",
        )
        client = JiraClient(config)

        result = await client.create_ticket(sample_triage_result, "Test incident")

        assert result["success"] is False
        assert "Jira not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_create_ticket_success(self, sample_triage_result):
        """Test successful ticket creation with mocked API."""
        config = JiraConfig(
            domain="company.atlassian.net",
            user_email="user@company.com",
            api_token="real_token",
        )
        client = JiraClient(config)

        # Mock httpx.AsyncClient
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "INC-123"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client.create_ticket(sample_triage_result, "Test incident")

            assert result["success"] is True
            assert result["ticket_id"] == "INC-123"
            assert "company.atlassian.net" in result["url"]


# ============================================================================
# SLACK CLIENT TESTS
# ============================================================================

class TestSlackClient:
    """Test Slack client functionality."""

    def test_not_configured(self):
        """Test that unconfigured Slack client returns False."""
        config = SlackConfig(
            webhook_url="https://hooks.slack.com/services/xxx/yyy/zzz",
        )
        client = SlackClient(config)

        assert not client.is_configured()

    def test_configured(self):
        """Test that configured Slack client returns True."""
        config = SlackConfig(
            webhook_url="https://hooks.slack.com/services/T00/B00/C00",
        )
        client = SlackClient(config)

        assert client.is_configured()

    @pytest.mark.asyncio
    async def test_send_alert_when_not_configured(self, sample_triage_result):
        """Test that alert is skipped when Slack not configured."""
        config = SlackConfig(
            webhook_url="https://hooks.slack.com/services/xxx/yyy/zzz",
        )
        client = SlackClient(config)

        result = await client.send_alert(sample_triage_result, "Test incident")

        assert result["success"] is False
        assert "Slack not configured" in result["error"]

    @pytest.mark.asyncio
    async def test_send_alert_success(self, sample_triage_result):
        """Test successful alert sending with mocked API."""
        config = SlackConfig(
            webhook_url="https://hooks.slack.com/services/T00/B00/C00",
        )
        client = SlackClient(config)

        # Mock httpx.AsyncClient
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "ok"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client.send_alert(
                sample_triage_result,
                "Test incident",
                "https://company.atlassian.net/browse/INC-123",
            )

            assert result["success"] is True
            assert result["message"] == "Notification sent"


# ============================================================================
# EMAIL CLIENT TESTS
# ============================================================================

class TestEmailClient:
    """Test email client functionality."""

    def test_not_configured(self):
        """Test that unconfigured email client returns False."""
        config = EmailConfig(
            sendgrid_api_key="your_sendgrid_key_here",
        )
        client = EmailClient(config)

        assert not client.is_configured()

    def test_configured(self):
        """Test that configured email client returns True."""
        config = EmailConfig(
            sendgrid_api_key="SG.real_key_here",
        )
        client = EmailClient(config)

        assert client.is_configured()

    @pytest.mark.asyncio
    async def test_send_email_when_not_configured(self):
        """Test that email is skipped when not configured."""
        config = EmailConfig(
            sendgrid_api_key="your_sendgrid_key_here",
        )
        client = EmailClient(config)

        result = await client.send_resolution_notification(
            "user@example.com",
            "INC-123",
            "Issue resolved",
        )

        assert result["success"] is False
        assert "Email not configured" in result["error"]


# ============================================================================
# ITSM BRIDGE TESTS
# ============================================================================

class TestITSMBridge:
    """Test ITSM Bridge orchestration."""

    @pytest.mark.asyncio
    async def test_handle_incident_no_config(self, sample_triage_result, sample_routing):
        """Test handling incident when no integrations are configured."""
        bridge = ITSMBridge()

        result = await bridge.handle_incident(
            triage=sample_triage_result,
            incident_description="Test incident",
            routing=sample_routing,
            reporter_email="user@example.com",
        )

        # Should complete but with no ticket/notification
        assert result["ticket_id"] is None
        assert result["slack_sent"] is False
        assert result["reporter_email"] == "user@example.com"
        assert len(result["errors"]) > 0  # Should have errors for unconfigured services

    @pytest.mark.asyncio
    async def test_handle_incident_with_configured_jira(self, sample_triage_result, sample_routing):
        """Test handling incident with mocked Jira configuration."""
        bridge = ITSMBridge()

        # Mock Jira client to be configured
        bridge.jira.config.domain = "company.atlassian.net"
        bridge.jira.config.user_email = "user@company.com"
        bridge.jira.config.api_token = "real_token"

        # Mock Jira API call
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"key": "INC-123"}

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await bridge.handle_incident(
                triage=sample_triage_result,
                incident_description="Test incident",
                routing=sample_routing,
            )

            assert result["ticket_id"] == "INC-123"
            assert result["ticket_url"] is not None
            # Slack will have an error since it's not configured, but Jira succeeded
            assert any("Jira" not in error for error in result["errors"])


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestITSMIntegration:
    """Test ITSM Bridge integration with TriageAgent."""

    @pytest.mark.asyncio
    async def test_full_triage_with_itsm(self):
        """Test full triage flow with ITSM integration (mocked)."""
        from backend.triage import TriageAgent
        from shared.schemas import IncidentIntake

        agent = TriageAgent()

        # Mock both Shield and ITSM Bridge
        with patch("backend.itsm_bridge.handle_itsm") as mock_itsm, \
             patch("backend.shield.validate_incident") as mock_shield:

            # Mock Shield to pass
            from shared.schemas import SecurityCheck
            mock_shield.return_value = SecurityCheck(
                is_safe=True,
                risk_score=5,
                risk_reasons=[],
                blocked_content=None,
            )

            # Mock ITSM Bridge
            mock_itsm.return_value = {
                "ticket_id": "INC-999",
                "ticket_url": "https://jira.example.com/browse/INC-999",
                "slack_sent": True,
                "reporter_email": "user@example.com",
                "errors": [],
            }

            incident = IncidentIntake(
                description="Database connection timeout during checkout",
                logs_text="Error: Connection timeout after 30s",
                reporter_email="user@example.com",
            )

            result = await agent.process_incident(incident)

            assert result["status"] == "success"
            assert "itsm" in result
            assert result["itsm"]["ticket_id"] == "INC-999"
            assert result["itsm"]["slack_sent"] is True
            assert "itsm_bridge" in result["tools_called"]


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestITSMErrorHandling:
    """Test error handling in ITSM Bridge."""

    @pytest.mark.asyncio
    async def test_jira_api_error(self, sample_triage_result):
        """Test handling of Jira API errors."""
        config = JiraConfig(
            domain="company.atlassian.net",
            user_email="user@company.com",
            api_token="real_token",
        )
        client = JiraClient(config)

        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client.create_ticket(sample_triage_result, "Test incident")

            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_slack_api_error(self, sample_triage_result):
        """Test handling of Slack API errors."""
        config = SlackConfig(
            webhook_url="https://hooks.slack.com/services/T00/B00/C00",
        )
        client = SlackClient(config)

        # Mock failed API response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"

        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await client.send_alert(sample_triage_result, "Test incident")

            assert result["success"] is False
            assert "error" in result
