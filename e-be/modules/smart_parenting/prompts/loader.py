"""YAML prompt loader for Smart Parenting services."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml


@lru_cache(maxsize=1)
def _load_prompt_data() -> dict:
    prompt_path = Path(__file__).resolve().parent / "smart_parenting.yaml"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    with prompt_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    prompts = raw.get("prompts")
    if not isinstance(prompts, dict):
        raise ValueError("Invalid prompt YAML format: 'prompts' section is required")
    return prompts


def get_prompt(section: str, key: str) -> str:
    """Return a prompt value by section/key from smart_parenting.yaml."""
    prompts = _load_prompt_data()
    section_data = prompts.get(section)
    if not isinstance(section_data, dict):
        raise KeyError(f"Prompt section '{section}' not found")

    value = section_data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise KeyError(f"Prompt key '{section}.{key}' not found or empty")

    return value
