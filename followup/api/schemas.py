from __future__ import annotations

from pydantic import BaseModel, Field


class FollowUpRequest(BaseModel):
    """Payload describing the question/response pair for follow-up decisions."""

    question: str = Field(..., min_length=1)
    response: str = Field(..., min_length=1)


class HealthResponse(BaseModel):
    """Basic health payload used for readiness probes."""

    status: str = Field(default="ok")


__all__ = [
    "FollowUpRequest",
    "HealthResponse",
]
