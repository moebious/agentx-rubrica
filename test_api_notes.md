# Test Script Notes

## Working Gemini API Configuration

**API Key Status:** ✅ Working

**Available Models:**
- `models/gemini-2.5-flash` - Fast, for Shield Node
- `models/gemini-2.5-flash-exp` - Experimental Flash
- `models/gemini-2.5-pro-exp` - Deep reasoning, for Triage

**Note:** The API provides Gemini 2.5 models, not 1.5 as originally planned.
This is actually better — newer, faster models with the same or better capabilities.

**Usage in Code:**
```python
import google.generativeai as genai
from pydantic import BaseModel

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# For Shield (fast validation)
shield_model = genai.GenerativeModel('models/gemini-2.5-flash')

# For Triage (deep reasoning)  
triage_model = genai.GenerativeModel('models/gemini-2.5-pro-exp')
```

## Model Updates Needed

All references to "Gemini 1.5" should be updated to "Gemini 2.5":
- SPEC-003: Operational Rigor
- SPEC-004: Agents & Capabilities
- SPEC-006: Context Engineering
- SPEC-007: Observability
- SPEC-019: Project Context
- SPEC-021: Solo MVP Implementation
- README.md
- AGENTS_USE.md
