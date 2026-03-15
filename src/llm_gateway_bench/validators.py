"""Input validation for llm-gateway-bench."""

from __future__ import annotations

import os
from typing import Optional
from urllib.parse import urlparse

from .exceptions import ProviderError
from .providers import PROVIDER_DEFAULTS


def validate_provider_name(provider: str) -> str:
    p = provider.strip().lower()
    if not p:
        raise ProviderError("Provider name cannot be empty")
    if p not in PROVIDER_DEFAULTS and p != "custom":
        supported = ", ".join(sorted(list(PROVIDER_DEFAULTS.keys()) + ["custom"]))
        raise ProviderError(f"Unsupported provider: {p}. Supported: {supported}")
    return p


def env_key_for_provider(provider: str) -> str:
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    return defaults.get("env_key", "")


def validate_api_key(provider: str, api_key: Optional[str], env_fallback: bool = True) -> str:
    """Ensure api key exists when provider requires it.

    Args:
        provider: normalized provider name.
        api_key: an explicit key passed in or resolved from config.
        env_fallback: when true, check env var based on provider.

    Returns:
        effective key string (may be dummy for local providers).
    """

    provider = validate_provider_name(provider)
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    env_key = defaults.get("env_key", "")

    # Local/self-hosted providers are intentionally allowed to be keyless.
    if not env_key:
        return api_key.strip() if api_key and api_key.strip() else "dummy"

    if api_key and api_key.strip():
        return api_key.strip()

    if env_fallback:
        env_val = os.getenv(env_key, "").strip()
        if env_val:
            return env_val

    raise ProviderError(
        f"API key is required for provider '{provider}'. Set {env_key} or pass via config."  # noqa: E501
    )


def validate_base_url(base_url: Optional[str]) -> Optional[str]:
    if base_url is None:
        return None
    u = base_url.strip()
    if not u:
        return None

    parsed = urlparse(u)
    if parsed.scheme not in {"http", "https"}:
        raise ProviderError("base_url must start with http:// or https://")
    if not parsed.netloc:
        raise ProviderError("base_url must include a host")
    return u
