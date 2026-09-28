from typing import Any

from openai import OpenAI, APIStatusError

from app.llm.base import LLMAdapter
import logging

logger = logging.getLogger(__name__)

class OpenAICompatibleAdapter(LLMAdapter):

    def __init__(
        self,
        model: str,
        base_url: str | None = None,
        api_key: str | None = None,
    ):
        self.model = model

        client_args = {
            "api_key": api_key or "ollama",
        }

        if base_url:
            client_args["base_url"] = base_url

        self.client = OpenAI(**client_args)

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:

        request = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            request["tools"] = tools

        try:
            return self.client.chat.completions.create(
                **request
            )
        except APIStatusError as exc:
            print("Status:", exc.status_code)
            print("Request URL:", exc.request.url)
            print("Response:", exc.response.text)
            raise
        except Exception:
            import traceback
            traceback.print_exc()
            logger.exception("LLM request failed")
            raise

