"""Load parent-agent prompts from YAML files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_PROMPT_CACHE: dict[str, dict[str, Any]] = {}


def load_parent_agent_prompt() -> dict[str, Any]:
    """Load and cache parent-agent prompt config."""
    cache_key = "parent_agent"
    if cache_key in _PROMPT_CACHE:
        return _PROMPT_CACHE[cache_key]

    prompt_path = (
        Path(__file__).resolve().parents[2] / "prompts" / "parent_agent.yaml"
    )
    with prompt_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    _PROMPT_CACHE[cache_key] = data
    return data
