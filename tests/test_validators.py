"""Tests for llm_gateway_bench.validators."""

import pytest

from llm_gateway_bench.exceptions import ProviderError
from llm_gateway_bench.validators import (
    validate_api_key,
    validate_base_url,
    validate_provider_name,
)


def test_validate_provider_name_known():
    assert validate_provider_name("openai") == "openai"
    assert validate_provider_name("OpenAI") == "openai"
    assert validate_provider_name("  deepseek  ") == "deepseek"


def test_validate_provider_name_custom():
    assert validate_provider_name("custom") == "custom"


def test_validate_provider_name_unknown():
    with pytest.raises(ProviderError) as exc:
        validate_provider_name("unknown_provider_xyz")
    assert "Unsupported provider" in str(exc.value)


def test_validate_provider_name_empty():
    with pytest.raises(ProviderError):
        validate_provider_name("")
    with pytest.raises(ProviderError):
        validate_provider_name("   ")


def test_validate_api_key_with_explicit_key():
    key = validate_api_key("openai", "sk-test-key", env_fallback=False)
    assert key == "sk-test-key"


def test_validate_api_key_local_provider_no_key():
    # ollama has no env_key requirement
    key = validate_api_key("ollama", None)
    assert key == "dummy"


def test_validate_api_key_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ProviderError) as exc:
        validate_api_key("openai", None, env_fallback=True)
    assert "API key is required" in str(exc.value)


def test_validate_api_key_from_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-key")
    key = validate_api_key("openai", None, env_fallback=True)
    assert key == "sk-env-key"


def test_validate_base_url_valid():
    assert validate_base_url("https://api.openai.com/v1") == "https://api.openai.com/v1"
    assert validate_base_url("http://localhost:11434/v1") == "http://localhost:11434/v1"


def test_validate_base_url_invalid_scheme():
    with pytest.raises(ProviderError) as exc:
        validate_base_url("ftp://example.com")
    assert "must start with http" in str(exc.value)


def test_validate_base_url_missing_host():
    with pytest.raises(ProviderError) as exc:
        validate_base_url("https://")
    assert "must include a host" in str(exc.value)


def test_validate_base_url_none():
    assert validate_base_url(None) is None
    assert validate_base_url("") is None
    assert validate_base_url("   ") is None
