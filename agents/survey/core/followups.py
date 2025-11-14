from __future__ import annotations

from textwrap import dedent

from pydantic import BaseModel, Field, model_validator
from pydantic_ai import Agent, exceptions as ai_exceptions
from pydantic_ai.settings import ModelSettings

from shared.config import settings


class FollowUpRecommendation(BaseModel):
    """Structured result returned by the follow-up agent."""

    should_ask: bool = Field(
        ...,
        description="Whether a follow-up question should be asked.",
    )
    follow_up_question: str = Field(
        default="",
        description="The follow-up question text (empty when none is required).",
    )

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def _normalize_question(self) -> "FollowUpRecommendation":
        cleaned = (self.follow_up_question or "").strip()
        if not self.should_ask:
            object.__setattr__(self, "follow_up_question", "")
            return self

        if not cleaned:
            raise ValueError("follow_up_question must be provided when should_ask is true.")

        object.__setattr__(self, "follow_up_question", cleaned)
        return self


class FollowUpAgent:
    """Thin wrapper around a PydanticAI agent for deciding follow-up questions."""

    _agent: Agent[None, FollowUpRecommendation]

    def __init__(self) -> None:
        provider_spec = settings.llm_provider_spec
        try:
            self._agent = Agent(
                provider_spec,
                output_type=FollowUpRecommendation,
                instructions=dedent(
                    """
                    You are a professional survey assistant tasked with judging whether a follow-up question is needed.
                    Consider the original survey question and the respondent's answer.

                    - Return `should_ask = true` when you need more detail to understand the answer.
                      Include a concise follow_up_question that invites elaboration.
                    - Return `should_ask = false` when the answer is already specific enough or a follow up question would not make sense.
                      Set follow_up_question to an empty string when no follow up is required.

                    Avoid repeating the original question verbatim and keep follow-up questions single-sentence and neutral.
                    """
                ).strip(),
                model_settings=ModelSettings(temperature=0.2),
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize follow-up agent: {exc}") from exc

    def decide(self, question: str, response: str) -> FollowUpRecommendation:
        """Run the agent and return its structured recommendation."""

        if not question or not response:
            raise ValueError("Both question and response must be provided.")

        prompt = dedent(
            f"""
            Survey question: {question}
            Respondent answer: {response}

            Provide your recommendation.
            """
        ).strip()

        try:
            run_result = self._agent.run_sync(prompt)
        except (ai_exceptions.AgentRunError, ai_exceptions.UserError) as exc:  # pragma: no cover - runtime path
            raise RuntimeError(f"Follow-up agent failed: {exc}") from exc
        except Exception as exc:  # pragma: no cover - runtime path
            raise RuntimeError(f"Follow-up agent encountered an unexpected error: {exc}") from exc

        return run_result.output
