"""
shared/clients/llm_client.py
────────────────────────────
Thin client wrapping the Anthropic Claude API.
Provides `call_text` and `call_json` with:
  • 10-second timeout
  • 1 automatic retry on failure
  • Safe JSON parsing fallback
"""

import json
import logging
from typing import Any, TypeVar

import anthropic
from anthropic import NOT_GIVEN
from pydantic import BaseModel

from core.config import get_settings
from core.exceptions import AITimeout

settings = get_settings()
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

# ── Client singleton ──────────────────────────────────────────────────────────
_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY or "dummy-key")
    return _client


# ── Public API ───────────────────────────────────────────────────────────────


def call_text(
    prompt: str,
    system_prompt: str = "You are a helpful AI assistant.",
    *,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1024,
    temperature: float = 0.7,
) -> str:
    """
    Call Claude for a plain text completion.

    Args:
        prompt:        The user-facing prompt.
        system_prompt:  System-level instructions.
        model:          Claude model ID.
        max_tokens:     Maximum tokens in the response.
        temperature:    Sampling temperature (0–1).

    Returns:
        The raw text response from Claude.

    Raises:
        AITimeout: if the request times out after 10 s.
    """
    client = _get_client()

    # ── first attempt ────────────────────────────────────────────────────────
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            timeout=10.0,
        )
        return response.content[0].text  # type: ignore[union-attr]

    except anthropic.APIError as exc:
        logger.warning("Claude API error (attempt 1): %s", exc)

    # ── retry once ───────────────────────────────────────────────────────────
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": prompt}],
            timeout=10.0,
        )
        return response.content[0].text  # type: ignore[union-attr]

    except (anthropic.APIError, anthropic.APIConnectionError) as exc:
        logger.error("Claude API failed after retry: %s", exc)
        raise AITimeout(message="Claude API failed after retry") from exc


def call_json(
    prompt: str,
    system_prompt: str,
    schema: type[T],
    *,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> T:
    """
    Call Claude and parse the response as a Pydantic model.

    The system prompt instructs Claude to output valid JSON only.
    A fallback regex-based parse is attempted before raising AITimeout.

    Args:
        prompt:        The user-facing prompt.
        system_prompt: System instructions (should mention JSON output).
        schema:        Pydantic model class to deserialize into.
        model:         Claude model ID.
        max_tokens:    Maximum tokens in response.
        temperature:   Sampling temperature (lower = more deterministic).

    Returns:
        An instance of `schema` populated from Claude's JSON response.

    Raises:
        AITimeout: if both the API call and JSON fallback parsing fail.
    """
    # Build a JSON-output instruction into the system prompt
    full_system = (
        f"{system_prompt}\n\n"
        "IMPORTANT: Respond ONLY with valid JSON that matches the schema below. "
        "Do not include any explanation or markdown formatting."
    )

    raw = call_text(
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
                logger.error("Failed to parse Claude JSON response: %s", raw[:200])
                raise AITimeout(message="Claude returned malformed JSON")
        else:
            raise AITimeout(message="Claude returned no JSON block")

    return schema.model_validate(data)
