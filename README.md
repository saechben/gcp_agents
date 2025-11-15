# Survey Follow-up Agent

Backend service that exposes a single follow-up recommendation agent plus the shared utilities required to run it.

## Repository layout

```
.
├─ followup/              # Survey follow-up agent package
│  ├─ api/                # FastAPI entrypoint and request/response schemas
│  └─ core/               # Follow-up decision agent (Pydantic AI)
├─ shared/                # Common config plus optional speech helpers
├─ docs/                  # Architecture diagrams retained from the original UI
├─ tests/                 # API and service tests
├─ Dockerfile             # Container image for the follow-up agent
└─ pyproject.toml
```

All Streamlit/UI code from the original project has been removed so that only the agent API surface remains.

## Getting started

1. **Install dependencies**
   ```bash
   poetry install
   ```
2. **Configure environment**
   Set at least the LLM credentials (others fall back to sane defaults):
   ```bash
   export LLM_API_KEY=sk-...
   export LLM_PROVIDER=openai        # or google
   export LLM_MODEL=gpt-4o-mini      # or gemini-1.5-flash
   ```
   Alternatively, set `LLM_PROVIDER_SPEC` directly (e.g. `google:gemini-1.5-flash`) if you need advanced routing.
3. **Run the survey agent API**
   ```bash
   poetry run uvicorn followup.api.main:app --reload --host=0.0.0.0 --port=8000
   ```
   The API now exposes:
   - `GET /health` – readiness probe
   - `POST /surveys/followups/decide` – invoke the follow-up agent which returns `{"should_ask": bool, "follow_up_question": str}`

Build an image for deployment (used by Cloud Build/Run):
```bash
docker build -t survey-agent .
```

## Tests

```bash
poetry run pytest
```

The suite covers the speech helper plus a FastAPI smoke test that validates the follow-up agent endpoint.

This repository is dedicated solely to the follow-up agent. Additional agents should live in their own repositories to keep build and deployment pipelines isolated.
