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
        api_key: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
    ) -> None:
        self.api_key = api_key or ""
        self.model = model
        self.max_retries = max_retries
        self._is_offline = (
            not self.api_key
            or self.model.lower() in ("mock", "offline", "demo", "heuristic")
        )
        if not self._is_offline:
            self._client = OpenAI(api_key=self.api_key)
        else:
            self._client = None

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
        if self._is_offline or self._client is None:
            return self._heuristic_classify(user_prompt)

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

    def _heuristic_classify(self, user_prompt: str) -> dict[str, Any]:
        """
        Deterministic, offline fallback topic classifier based on keyword scoring.
        Allows full pipeline execution, testing, and UI demonstration without an active API key.
        """
        text = user_prompt.lower()

        # Extract prev_topic if present in prompt
        prev_topic = None
        if "previous topic (if any):" in text:
            pt_line = text.split("previous topic (if any):")[-1].strip().splitlines()[0]
            if pt_line and "(none)" not in pt_line:
                prev_topic = pt_line.strip()

        categories = [
            ("Employment History", ["employment", "job", "career", "hired", "worked", "salary", "position", "worked for", "resigned"], "Discussion of witness's past employment, titles, and job responsibilities."),
            ("Apex Software Acquisition", ["apex", "acquisition", "purchase agreement", "buyout", "merger", "due diligence", "closing"], "Testimony regarding the acquisition terms, valuation, and transaction of Apex Software."),
            ("Offshore Financial Accounts", ["cayman", "offshore", "bank", "wire", "transfer", "financial", "funds", "account", "deposit", "balance"], "Inquiries regarding offshore bank accounts, transaction flows, and wire transfers."),
            ("Email Communications", ["email", "inbox", "sent", "forwarded", "subject line", "thread", "message", "attachment"], "Review of email correspondence, messages, and electronic communications between key parties."),
            ("Board of Directors Meetings", ["board", "directors", "meeting", "minutes", "resolution", "vote", "quorum"], "Discussions of board meetings, corporate governance, and voting resolutions."),
            ("Contractual Agreements and Exhibits", ["contract", "agreement", "exhibit", "clause", "signed", "document", "provision"], "Examination of signed contracts, exhibits, and formal legal agreements."),
            ("Legal Objections and Colloquy", ["objection", "instruct", "form", "privilege", "colloquy", "strike"], "Procedural objections by counsel regarding form, relevance, or privilege."),
        ]

        best_topic = "General Deposition Testimony"
        best_desc = "General factual questions and answers regarding case background."
        max_score = 0

        for name, keywords, desc in categories:
            score = sum(text.count(kw) for kw in keywords)
            if score > max_score:
                max_score = score
                best_topic = name
                best_desc = desc

        # Event type detection
        if "objection" in text and ("instruct" in text or "form" in text):
            event_type = "digression"
        elif prev_topic and best_topic.lower() == prev_topic.lower():
            event_type = "continuation"
        elif prev_topic and prev_topic.lower() != best_topic.lower() and max_score > 0:
            event_type = "new_topic"
        else:
            event_type = "new_topic"

        confidence = 0.92 if max_score >= 2 else (0.80 if max_score == 1 else 0.55)

        return {
            "topic": best_topic,
            "description": best_desc,
            "event_type": event_type,
            "confidence": confidence,
        }
