from __future__ import annotations

import logging
from fastapi import Depends, FastAPI, HTTPException, status

from followup.api.schemas import FollowUpRequest, HealthResponse
from followup.core import FollowUpAgent, FollowUpRecommendation

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Survey Agent API",
    version="0.1.0",
    description="HTTP surface that exposes the follow-up recommendation agent.",
)


_FOLLOW_UP_AGENT = FollowUpAgent()


def get_follow_up_agent() -> FollowUpAgent:
    """Dependency hook for the follow-up decision agent."""

    return _FOLLOW_UP_AGENT


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    """Simple readiness endpoint used for container health checks."""

    return HealthResponse()


@app.post(
    "/surveys/followups/decide",
    response_model=FollowUpRecommendation,
    tags=["followups"],
)
def decide_follow_up(
    payload: FollowUpRequest,
    agent: FollowUpAgent = Depends(get_follow_up_agent),
) -> FollowUpRecommendation:
    """Return whether a follow-up question should be asked."""

    try:
        return agent.decide(payload.question, payload.response)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:  # pragma: no cover - runtime failure path
        logger.exception("Follow-up agent failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Follow-up agent is unavailable.",
        ) from exc
