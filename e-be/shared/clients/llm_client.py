"""
shared/clients/llm_client.py
────────────────────────────
Thin async client wrapping the OpenAI Chat Completions API.
Provides `call_text` and `call_json` with:
  • 10-second timeout
  • 1 automatic retry on failure
  • Safe JSON parsing fallback
"""

import json
import logging
from typing import Any, TypeVar

import openai
from openai import APIError, APIConnectionError, RateLimitError
from pydantic import BaseModel

from core.config import get_settings
from core.exceptions import AITimeout

settings = get_settings()
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# ── Client singleton ──────────────────────────────────────────────────────────
_client: openai.AsyncOpenAI | None = None


def _get_client() -> openai.AsyncOpenAI:
    global _client
    if _client is None:
        _client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY or "dummy-key")
    return _client


async def _create_chat_completion(
    *,
    prompt: str,
    system_prompt: str,
    model: str,
    max_tokens: int,
    temperature: float,
) -> str:
    """Single place to call Chat Completions with shared parameters."""
    client = _get_client()

    # Prefer max_completion_tokens for newer models (e.g. GPT-5 family),
    # but fall back to max_tokens for older model compatibility.
    request_base: dict[str, Any] = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        "timeout": 10.0,
    }

    try:
        response = await client.chat.completions.create(
            **request_base,
            max_completion_tokens=max_tokens,
        )
    except APIError as exc:
        message = str(exc)
        if "max_completion_tokens" not in message:
            raise

        response = await client.chat.completions.create(
            **request_base,
            max_tokens=max_tokens,
        )

    return response.choices[0].message.content or ""  # type: ignore[union-attr]


# ── Public API ───────────────────────────────────────────────────────────────


async def call_text(
    prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
    *,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """
    Call OpenAI for a plain text completion (async).

    Args:
        prompt:        The user-facing prompt.
        system_prompt: System-level instructions.
        model:         OpenAI model ID.
        max_tokens:    Maximum tokens in the response.
        temperature:   Sampling temperature (0–1).

    Returns:
        The raw text response from OpenAI.

    Raises:
        AITimeout: if the request times out after 10 s.
    """
    resolved_model = model or settings.OPENAI_MODEL

    # ── first attempt ────────────────────────────────────────────────────────
    try:
        return await _create_chat_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            model=resolved_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    except APIError as exc:
        logger.warning("OpenAI API error (attempt 1): %s", exc)

    # ── retry once ───────────────────────────────────────────────────────────
    try:
        return await _create_chat_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            model=resolved_model,
            max_tokens=max_tokens,
            temperature=temperature,
        )

    except (APIError, APIConnectionError, RateLimitError) as exc:
        logger.error("OpenAI API failed after retry: %s", exc)
        raise AITimeout(message="OpenAI API failed after retry") from exc


async def call_json(
    prompt: str,
    system_prompt: str,
    schema: type[T],
    *,
    model: str | None = None,
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> T:
    """
    Call OpenAI and parse the response as a Pydantic model (async).

    The system prompt instructs the model to output valid JSON only.
    A fallback regex-based parse is attempted before raising AITimeout.

    Args:
        prompt:        The user-facing prompt.
        system_prompt: System instructions (should mention JSON output).
        schema:        Pydantic model class to deserialize into.
        model:         OpenAI model ID.
        max_tokens:    Maximum tokens in response.
        temperature:   Sampling temperature (lower = more deterministic).

    Returns:
        An instance of `schema` populated from OpenAI's JSON response.

    Raises:
        AITimeout: if both the API call and JSON fallback parsing fail.
    """
    # Build a JSON-output instruction into the system prompt
    full_system = (
        f"{system_prompt}\n\n"
        "IMPORTANT: Respond ONLY with valid JSON that matches the schema below. "
        "Do not include any explanation or markdown formatting."
    )

    raw = await call_text(
        prompt=prompt,
        system_prompt=full_system,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    # ── safe JSON parse ──────────────────────────────────────────────────────
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract the first {...} or [...] block
        import re

        match = re.search(r"(\{[\s\S]*\}|\[[\s\S]*\])", raw)
        if match:
            try:
                data = json.loads(match.group(1))
            except json.JSONDecodeError:
                logger.error("Failed to parse OpenAI JSON response: %s", raw[:200])
                raise AITimeout(message="OpenAI returned malformed JSON")
        else:
            raise AITimeout(message="OpenAI returned no JSON block")

    return schema.model_validate(data)
