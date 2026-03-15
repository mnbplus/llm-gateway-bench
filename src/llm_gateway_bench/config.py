"""Config loader for bench.yaml."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

from .exceptions import ConfigError
from .models import BenchConfig


def load_config(path: str) -> Dict[str, Any]:
    """Load and validate a bench.yaml config file.

    Args:
        path: Path to the YAML configuration file.

    Returns:
        The validated configuration as a plain dictionary.
    """
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        with p.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except yaml.YAMLError as exc:
        raise ConfigError(f"Invalid YAML: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError("Config root must be a mapping.")

    config = BenchConfig.model_validate(raw)

    # Expand env vars in api_key fields
    for provider in config.providers:
        if provider.api_key and provider.api_key.startswith("${") and provider.api_key.endswith("}"):
            env_name = provider.api_key[2:-1]
            provider.api_key = os.getenv(env_name, "")

    return config.model_dump()
