"""pytest fixtures for llm-gateway-bench."""

from __future__ import annotations

from typing import Dict

import pytest

from llm_gateway_bench.models import BenchResult


@pytest.fixture()
def sample_result() -> BenchResult:
    return BenchResult(
        provider="openai",
        model="gpt-4o-mini",
        ttft_ms=312.0,
        total_ms=1840.0,
        tokens_per_sec=68.2,
        success_rate=1.0,
        p95_ms=2100.0,
        p50_ms=1800.0,
        errors=0,
        total_tokens=150,
    )


@pytest.fixture()
def sample_config_dict(tmp_path, monkeypatch) -> Dict[str, str]:
    monkeypatch.setenv("UNIT_TEST_API_KEY", "abc123")
    config_path = tmp_path / "bench.yaml"
    config_path.write_text(
        """
prompts:
  - "Say hello"
providers:
  - name: openai
    model: gpt-4o-mini
    api_key: ${UNIT_TEST_API_KEY}
settings:
  requests: 2
  concurrency: 1
  timeout: 5
""".lstrip(),
        encoding="utf-8",
    )
    return {"path": str(config_path)}
