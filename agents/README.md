# Agents

## Survey Agent

- **Entrypoint**: `uvicorn agents.survey.api.main:app`
- **Framework**: FastAPI
- **Endpoints**:
  - `GET /health` – readiness
  - `POST /surveys/followups/decide` – invoke the follow-up recommendation agent
- **Core logic**: `agents/survey/core/`
- **Shared dependencies**: `shared/` (config plus optional speech helpers)

The follow-up agent accepts a survey question + respondent answer and returns a JSON payload with `should_ask` (bool) and `follow_up_question` (string, empty when no follow up is required).
