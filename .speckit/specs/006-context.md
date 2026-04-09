# SPEC-006: Context Engineering Approach

**Status:** TECHNICAL LOCK
**Focus:** Data Density & Multimodal Fusion
**Primary Model:** Gemini 2.5 Pro

---

## 1. The "Silver Bullet": 2-Million Token Context

While other teams are trying to truncate their prompts to fit 8,000 or 32,000 tokens, we are utilizing the Gemini 2.5 Pro 1M window.

| Aspect | Details |
|--------|---------|
| **The Strategy** | Instead of just sending a small snippet of code, we send the entire module context. |
| **The Implementation** | If an error occurs in the checkout module, the agent receives the full `saleor/checkout/` directory structure and the primary `models.py`, `views.py`, and `calculations.py` files. |
| **The Result** | The agent understands the relationship between functions across files, which standard RAG usually misses. |

---

## 2. Hybrid Retrieval (The Safety Net)

Even with a 1M window, we can't send the entire Saleor repo (it's too much noise). We use a dual-path retrieval system:

### Path A: Semantic (Qdrant)
**Used for "vague" queries.**

| Example | Action |
|---------|--------|
| "Find code related to gift card validation." | Returns the most relevant functions based on meaning. |

### Path B: Exact (BM25 Keyword)
**Used for "precise" technical triggers.**

| Example | Action |
|---------|--------|
| `CheckoutNotCalculated` or `AttributeError` | Returns the exact line where that class or variable is defined. |

### Synthesis
The Triage Supervisor merges these two paths into a single "Context Block."

---

## 3. Multimodal Context Fusion

This is a core hackathon requirement. We don't just "read" the screenshot; we fuse it with the logs.

| Encoding | Process |
|----------|---------|
| **Vision Encoding** | The agent analyzes the UI screenshot to identify UI-side state (e.g., "The 'Pay' button is greyed out"). |
| **Text Encoding** | The agent reads the server logs to find the backend cause (e.g., "Database timeout on payment_intent"). |
| **The Fusion** | The agent is prompted to: "Explain why the UI is in State A (Greyed Button) given the Backend is in State B (Database Timeout)." This provides a true end-to-end SRE perspective. |

---

## 4. Contextual Pruning (Noise Reduction)

To keep the agent from getting "lost" in the 1M window, we use **Folder Summaries**.

- We pre-generate a 1-sentence description of every major folder in Saleor.
- Before deep-diving into code, the Supervisor reads the folder map to decide which "Haystacks" are worth searching.

---

## 🏁 CTO's Blitz Command

SPEC-006 is the "Secret Sauce." It explains why our agent will be more accurate than anyone else's. You've now got the content for the "Context Engineering" section of your `AGENTS_USE.md`.
