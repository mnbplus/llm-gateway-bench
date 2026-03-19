"""Config loader for bench.yaml."""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from pydantic import ValidationError

from .exceptions import ConfigError
from .models import BenchConfig


def _expand_provider_env_vars(config: BenchConfig) -> None:
    """Resolve ${ENV_NAME} placeholders in provider api_key fields."""

    for provider in config.providers:
        if (
            provider.api_key
            and provider.api_key.startswith("${")
            and provider.api_key.endswith("}")
        ):
            env_name = provider.api_key[2:-1]
            provider.api_key = os.getenv(env_name, "")


def load_config(path: str) -> BenchConfig:
    """Load and validate a benchmark YAML config file."""

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

    try:
        config = BenchConfig.model_validate(raw)
    except ValidationError as exc:
        raise ConfigError(str(exc)) from exc

    _expand_provider_env_vars(config)
    return config
