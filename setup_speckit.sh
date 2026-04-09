#!/bin/bash
mkdir -p .speckit/specs

# Create Manifest
cat << 'EOM' > .speckit/manifest.json
{
  "project": "Rubrica SRE Agent",
  "methodology": "Ralph Loops",
  "foundation_specs": ["000", "001", "010"],
  "logic_specs": ["002", "005", "006", "008"],
  "docs_specs": ["011", "012", "013", "014", "015", "016", "017", "018"]
}
EOM

# Create the core Specs (Abbreviated for the handover)
echo "SPEC-000: Mission Mandate. Build a production-ready SRE Intake Agent for Saleor." > .speckit/specs/000-mission.md
echo "SPEC-001: Architecture. Bunker (FastAPI) and Borde (Next.js). Monorepo." > .speckit/specs/001-architecture.md
echo "SPEC-010: Filesystem. rubrica/ with backend, frontend, shared, and scripts." > .speckit/specs/010-filesystem.md
echo "SPEC-002: Logic. Use Instructor for Pydantic enforcement and LangGraph for state." > .speckit/specs/002-logic.md
echo "SPEC-008: Security. Implement a Shield Node for prompt injection filtering." > .speckit/specs/008-security.md

# Create the .clauderules
cat << 'EOM' > .clauderules
# Rubrica Rules
1. ALWAYS read .speckit/specs/ before coding.
2. FOLLOW the Ralph Loop (Research, Align, Logic, Proof, Handoff).
3. TECH: FastAPI, LangGraph, Redis, Qdrant, Next.js.
EOM

echo "Speckit initialized successfully."
