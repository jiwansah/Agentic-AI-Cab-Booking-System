import os

from app.llm.base import LLMAdapter
from app.llm.openai_compatible import (
    OpenAICompatibleAdapter,
)


def create_llm() -> LLMAdapter:

    provider = os.getenv(
        "LLM_PROVIDER",
        "ollama"
    ).lower()

    if provider == "ollama":
        return OpenAICompatibleAdapter(
            model=os.getenv(
                "OLLAMA_MODEL",
                "gpt-oss:20b"
            ),
            base_url=os.getenv(
                "OLLAMA_BASE_URL",
                "http://localhost:11434/v1"
            ),
            api_key="ollama",
        )

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is required "
                "when LLM_PROVIDER=openai"
            )

        return OpenAICompatibleAdapter(
            model=os.getenv(
                "OPENAI_MODEL",
                "gpt-5.6-luna"
            ),
            base_url=os.getenv(
                "OPENAI_BASE_URL",
                "https://api.openai.com/v1"
            ),
            api_key=api_key,
        )

    else:
        raise ValueError(
            f"Unsupported LLM provider: {provider}"
        )
