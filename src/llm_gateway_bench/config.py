"""Config loader for bench.yaml."""

import yaml
import os
from pathlib import Path


def load_config(path: str) -> dict:
    """Load and validate a bench.yaml config file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(p, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Expand env vars in api_key fields
    for provider in cfg.get("providers", []):
        if "api_key" in provider:
            key = provider["api_key"]
            if key.startswith("${") and key.endswith("}"):
                env_name = key[2:-1]
                provider["api_key"] = os.getenv(env_name, "")

    return cfg
