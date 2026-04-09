# SPEC-004: Agents & Capabilities (The Personas)

**Status:** OPERATIONAL
**Focus:** Separation of Concerns
**Required for:** AGENTS_USE.md

---

## 1. The Shield (Security Agent)

**Persona:** A non-permissive security researcher.

**Model:** Gemini 1.5 Flash (Optimized for speed/latency).

**Mission:** Inspect the `IncidentIntake` for adversarial attacks.

### Capabilities
| Capability | Description |
|------------|-------------|
| **Prompt Injection Detection** | Scans for "system overrides." |
| **Off-Topic Filtering** | Ensures the input is actually an SRE incident, not a request for a poem or a pizza. |

### Output
A strict boolean `is_safe` and a risk score.

---

## 2. The Triage Supervisor (The Architect)

**Persona:** A Senior SRE with 15 years of experience in distributed systems.

**Model:** Gemini 1.5 Pro (Optimized for deep reasoning).

**Mission:** Synthesize multimodal input and plan the technical investigation.

### Capabilities
| Capability | Description |
|------------|-------------|
| **Multimodal Correlation** | Matches pixels in a screenshot to specific stack traces in logs. |
| **Path Planning** | Decides which modules of the Saleor repository to query. |

### Output
A `InvestigationPlan` Pydantic model.

---

## 3. The Librarian (RAG Worker)

**Persona:** A specialized code indexer and search expert.

**Model:** Gemini 1.5 Pro (Massive context window).

**Mission:** Retrieve exact code snippets and technical documentation.

### Capabilities
| Capability | Description |
|------------|-------------|
| **Hybrid Retrieval** | Executes Qdrant Vector searches for concepts and BM25 for exact error codes. |
| **Context Compression** | Ingests up to 2 million tokens of code and returns only the relevant functions. |

### Output
`CodeContext` snippets.

---

## 4. The ITSM Bridge (Integration Worker)

**Persona:** A meticulous technical project manager.

**Model:** Gemini 1.5 Flash.

**Mission:** Translate messy technical hypotheses into professional business formats.

### Capabilities
| Capability | Description |
|------------|-------------|
| **Jira Mapping** | Translates "Priority" (0-3) to Jira "Critical-Low" labels. |
| **Slack Summarization** | Creates "Executive Summaries" for the #sre-alerts channel. |

### Output
Successful API payloads and ticket IDs.

---

## 🛡️ Why This Strategy Wins

By using Gemini 1.5 Flash for the Shield and ITSM Bridge, we keep the UI responsive and the token costs low. We reserve the "heavy lifting" of Gemini 1.5 Pro for the Supervisor and Librarian, where deep-code reasoning is mandatory.

**This is "Economic Agent Design."**
