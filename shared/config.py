from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


def _strip_or_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


@dataclass(frozen=True)
class SpeechSettings:
    provider: str
    stt_model: str
    tts_model: str
    tts_voice: Optional[str]
    tts_format: str
    language: Optional[str] = None


class Settings:

    def __init__(self) -> None:
        api_key = (
            _strip_or_none(os.getenv("LLM_API_KEY"))
            or _strip_or_none(os.getenv("OPENAI_API_KEY"))
            or _strip_or_none(os.getenv("GOOGLE_API_KEY"))
        )
        if not api_key:
            raise RuntimeError("Missing LLM/OpenAI API key in environment or .env file.")
        self.llm_api_key = api_key

        model_name = _strip_or_none(os.getenv("LLM_MODEL")) or _strip_or_none(os.getenv("OPENAI_MODEL"))
        if not model_name:
            raise RuntimeError("Missing LLM/OpenAI model name in environment or .env file.")
        self.llm_model = model_name

        provider = _strip_or_none(os.getenv("LLM_PROVIDER")) or "openai"
        provider_spec = _strip_or_none(os.getenv("LLM_PROVIDER_SPEC"))
        if provider_spec:
            self.llm_provider_spec = provider_spec
        else:
            self.llm_provider_spec = f"{provider}:{model_name}"
        self.llm_provider = provider

        if provider == "openai":
            os.environ.setdefault("OPENAI_API_KEY", self.llm_api_key)
            os.environ.setdefault("OPENAI_MODEL", model_name)
        elif provider == "google":
            os.environ.setdefault("GOOGLE_API_KEY", self.llm_api_key)

        speech_provider = _strip_or_none(os.getenv("SPEECH_PROVIDER")) or "openai"
        speech_stt_model = _strip_or_none(os.getenv("SPEECH_STT_MODEL")) or "whisper-1"
        speech_tts_model = _strip_or_none(os.getenv("SPEECH_TTS_MODEL")) or "gpt-4o-mini-tts"
        speech_tts_voice = _strip_or_none(os.getenv("SPEECH_TTS_VOICE")) or "nova"
        speech_tts_format = _strip_or_none(os.getenv("SPEECH_TTS_FORMAT")) or "mp3"
        speech_language = _strip_or_none(os.getenv("SPEECH_LANGUAGE"))

        self.speech = SpeechSettings(
            provider=speech_provider,
            stt_model=speech_stt_model,
            tts_model=speech_tts_model,
            tts_voice=speech_tts_voice,
            tts_format=speech_tts_format,
            language=speech_language,
        )


settings = Settings()
