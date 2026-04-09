# SPEC-014: QUICKGUIDE.md

---

# ⚡ Rubrica Quickstart Guide

Follow these steps to deploy the Rubrica SRE Agent stack locally for testing and evaluation.

---

## 📋 Prerequisites

- Docker & Docker Compose installed.
- Git installed.
- **API Key:** A Google Gemini API Key ([Get one here](https://aistudio.google.com/app/apikey)) **OR** an OpenRouter API Key.

---

## 🚀 Step 1: Clone & Prepare

```bash
# Clone the repository
git clone https://github.com/your-username/rubrica.git
cd rubrica

# Create your environment file
cp .env.example .env
```

---

## 🔑 Step 2: Configure Keys

Open the `.env` file in your editor. At a minimum, you must provide one LLM provider:

### Option A: Direct Google Gemini (Recommended)
```env
LLM_PROVIDER=google
GEMINI_API_KEY=your_key_here
```

### Option B: OpenRouter Support
If you prefer using OpenRouter to access Gemini or other models:
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key_here
# Optional: Change the model string if not using Gemini 1.5 Pro
# MODEL_NAME=google/gemini-pro-1.5
```

---

## 🏗️ Step 3: Launch the Stack

Run the following command to build and start the Bunker (Backend), Borde (Frontend), Redis, and Qdrant.

```bash
docker compose up --build
```

Wait for the logs to show: `Application startup complete.`

---

## 📚 Step 4: Ingest the Codebase (The "Smart" Step)

To allow the agent to triage the Saleor repository, you must run the indexing script. In a new terminal window:

```bash
# This populates your local Qdrant instance with Saleor context
docker compose exec api python scripts/ingest_saleor.py
```

---

## 🧪 Step 5: Test the Flow

1. **Open the UI:** Navigate to http://localhost:3000.
2. **Submit a Report:**
   - Enter a description: "The checkout page is throwing a 500 error when I click pay."
   - Upload a sample log or screenshot (find samples in `tests/samples/`).
3. **Check the Dashboard:** Watch the LangGraph state transition from Shield → Triage → Action.
4. **Verify Integrations:** Check your console logs to see the (mocked or real) Jira ticket and Slack notification payloads.

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port Conflict** | Ensure ports 3000, 8000, 6379, and 6333 are free. |
| **OpenRouter 401** | Double-check your credits and API key validity on the OpenRouter dashboard. |
| **Docker Memory** | Ensure Docker has at least 4GB of RAM allocated (Qdrant and Gemini processing require it). |
