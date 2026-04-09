# SPEC-000: Mission Mandate & Rules of Engagement

**Project:** Rubrica SRE Agent
**Event:** AgentX Hackathon 2026
**Status:** ACTIVE
**Deadline:** April 9, 2026, @ 9:00 PM COT (~6 Hours Remaining)

---

## 1. The Assignment: SRE Incident Intake & Triage

We are building a production-ready SRE Agent for our e-commerce platform (Saleor). The mission is to bridge the gap between failure reports and technical resolution with zero manual friction.

### Core E2E Flow
1. **Intake:** Submit multimodal reports via UI.
2. **Triage:** Extract key details + produce a technical summary using codebase RAG.
3. **Ticket:** Auto-create tickets in Jira/Linear.
4. **Internal Notify:** Alert the tech team via Email/Slack.
5. **External Notify:** Automatically email the original reporter once the ticket is resolved.

---

## 2. Technical Minimum Requirements

To pass the automated screening, Rubrica must meet these five "Hard Gates":

| Requirement | Rubrica Implementation (SPEC-001/002) |
|-------------|----------------------------------------|
| **Multimodal Input** | Text + Image (Screenshots) + Log Files via Gemini 1.5. |
| **Guardrails** | The Shield Node: Prompt injection defense & safe tool handling. |
| **Observability** | E2E Traces via LangSmith and metrics/evals via Opik. |
| **Integrations** | Demoable Jira (Ticketing), Slack (Comms), and Email. |
| **Complex Codebase** | Saleor (Python/Django/GraphQL). |

---

## 3. The Evaluation Dimensions

The judges aren't looking for "cool ideas"; they are looking for **Production-Readiness**.

| Dimension | What We Must Prove |
|-----------|-------------------|
| **Reliability** | Does it handle edge cases? Does the Redis checkpoint work? |
| **Observability** | Are the logs structured? Can we see the "Thinking" in LangSmith? |
| **Scalability** | Are our assumptions about codebase growth documented? |
| **Context Engineering** | How well do we use the 2M token window vs. RAG? |
| **Security** | How robust is our Shield Node against malicious overrides? |

---

## 4. Mandatory Deliverables

Failure to include these files in our public MIT-licensed repository will result in immediate disqualification.

| File | Purpose |
|------|---------|
| **QUICKGUIDE.md** | How to run the Bunker and the Borde. |
| **.env.example** | Placeholders for Gemini, Jira, Slack, and Redis keys. |
| **AGENTS_USE.md** | (Crucial) Detailed breakdown of:<br>• Agent capabilities and tech stack.<br>• Orchestration logic and error handling.<br>• Evidence of observability and guardrails.<br>• Lessons learned and team reflections. |

---

## 5. Official FAQ & Constraints

| Rule | Details |
|------|---------|
| **English Only** | All code, documentation, and the demo video must be in English (B2+ level). |
| **Public MIT License** | The repo must be public. |
| **No Direct Mentor DMs** | All technical queries must go through #ask-mentors. |
| **Multimodal Requirement** | We MUST use an LLM that supports more than just text. (Gemini 1.5 Pro confirmed). |
