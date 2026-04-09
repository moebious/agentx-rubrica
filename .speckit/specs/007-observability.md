# SPEC-007: Observability (The Glass Box)

**Status:** MANDATORY
**Primary Tech:** LangSmith, Opik, Loguru
**Focus:** Traceability & Truth

---

## 1. Macro Observability: LangSmith (The Decision Tree)

We use LangSmith as our primary window into the LangGraph state machine.

| Aspect | Details |
|--------|---------|
| **The Goal** | Visual evidence of agent reasoning. |
| **The Implementation** | Every run of the Rubrica agent is traced. This captures the exact input/output of every node (Shield, Triage, Action). |
| **Judge Value** | During the demo, we will show a trace of the "Checkout Crisis" where the judges can see the Supervisor deciding to call the Librarian to search the code. |

### Evidence
A public link to a LangSmith trace for the `Incident_001` run.

---

## 2. Quality Observability: Opik (The Eval Engine)

We use Opik to quantify "Accuracy." In 2026, simple logs aren't enough; you need metrics.

| Aspect | Details |
|--------|---------|
| **The Metric** | Faithfulness & Relevance. |
| **The Implementation** | We run a "Golden Dataset" of 5 pre-recorded Saleor incidents. Opik uses an "LLM-as-a-Judge" to compare Rubrica's hypothesis against a "Ground Truth" fix. |
| **Judge Value** | We can state: "Rubrica achieved a 94% faithfulness score across our test incidents." This is a massive differentiator. |

### Evidence
A screenshot of the Opik "Experiment" table showing the scores.

---

## 3. Micro Observability: Loguru (The Pulse)

We use Loguru for structured, asynchronous backend logging.

| Aspect | Details |
|--------|---------|
| **The Goal** | Correlation of system events. |
| **The Implementation** | Every incident request gets a unique `request_id`. Loguru tags every backend event (Redis save, Qdrant search, FastAPI intake) with this ID. |
| **Judge Value** | If the demo crashes, we can pull the logs and show exactly which API call timed out. It shows we built a Production system, not a script. |

### Evidence
A snippet of color-coded terminal logs showing the Shield → Triage handoff.

---

## 🛡️ The "Observability" Checklist for the Submission

To fulfill the `AGENTS_USE.md` requirements, we must capture:

| Requirement | Description |
|-------------|-------------|
| **A "Shield-Block" Trace** | Prove that the guardrail works. |
| **A "Tool-Call" Trace** | Show the agent actually searching the Saleor code. |
| **A "Latency Breakdown"** | Show that Gemini Flash handles the Shield in <1s while the Pro model handles the Triage in ~5s. |

---

## 🏁 CTO's Blitz Command

SPEC-007 is the "Judge's Favorite." It makes your project look 10x more professional than a simple chatbot.
