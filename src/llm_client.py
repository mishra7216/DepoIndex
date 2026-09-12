"""
DepoIndex – OpenAI LLM client wrapper.

Provides a thin, retry-capable interface for calling GPT-4o-mini
with JSON-structured output.
"""

from __future__ import annotations

import json
import time
from typing import Any, Optional

from openai import OpenAI, APIError, RateLimitError


class LLMClient:
    """
    Wrapper around the OpenAI chat completion API.

    Parameters
    ----------
    api_key : str
        OpenAI API key (sk-...)
    model   : str
        Model identifier, default "gpt-4o-mini"
    max_retries : int
        Number of automatic retries on transient API errors.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
    ) -> None:
        self._client = OpenAI(api_key=api_key)
        self.model = model
        self.max_retries = max_retries

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.0,
        response_format: Optional[str] = "json_object",
    ) -> dict[str, Any]:
        """
        Send a chat completion request and return the parsed JSON response.

        Parameters
        ----------
        system_prompt   : system-role instruction string
        user_prompt     : user-role content
        temperature     : sampling temperature (0 = deterministic)
        response_format : "json_object" to request JSON mode, or None

        Returns
        -------
        dict parsed from the model's response content
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        if response_format == "json_object":
            kwargs["response_format"] = {"type": "json_object"}

        last_exc: Optional[Exception] = None
        for attempt in range(self.max_retries):
            try:
                response = self._client.chat.completions.create(**kwargs)
                raw = response.choices[0].message.content or "{}"
                return json.loads(raw)
            except RateLimitError as exc:
                wait = 2 ** attempt
                time.sleep(wait)
                last_exc = exc
            except APIError as exc:
                wait = 2 ** attempt
                time.sleep(wait)
                last_exc = exc
            except json.JSONDecodeError as exc:
                last_exc = exc
                break

        raise RuntimeError(
            f"LLM call failed after {self.max_retries} attempts: {last_exc}"
        )
