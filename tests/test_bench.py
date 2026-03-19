"""Basic tests for llm-gateway-bench."""

import json
import os
import tempfile

from llm_gateway_bench.bench import compare_providers
from llm_gateway_bench.models import (
    BenchConfig,
    BenchResult,
    ProviderConfig,
    SettingsConfig,
)
from llm_gateway_bench.report import generate_report


def make_result(provider: str = "openai", model: str = "gpt-4o-mini") -> BenchResult:
    return BenchResult(
        provider=provider,
        model=model,
        ttft_ms=312.0,
        total_ms=1840.0,
        tokens_per_sec=68.2,
        success_rate=1.0,
        p95_ms=2100.0,
        p50_ms=1800.0,
        errors=0,
        total_tokens=150,
    )


def test_bench_result_fields():
    r = make_result()
    assert r.provider == "openai"
    assert r.ttft_ms == 312.0
    assert r.success_rate == 1.0


def test_report_json():
    results = [make_result(), make_result("deepseek", "deepseek-chat")]
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        generate_report(results, path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        assert len(data) == 2
        assert data[0]["provider"] == "openai"
    finally:
        os.unlink(path)


def test_report_markdown():
    results = [make_result()]
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
        path = f.name
    try:
        generate_report(results, path)
        with open(path, encoding="utf-8") as f:
            content = f.read()
        assert "openai" in content
        assert "gpt-4o-mini" in content
    finally:
        os.unlink(path)


def test_compare_providers_uses_provider_api_key(monkeypatch):
    captured = {}

    def fake_run_benchmark(
        provider,
        model,
        prompt,
        n_requests=20,
        concurrency=3,
        base_url=None,
        api_key=None,
        timeout=30,
        on_progress=None,
    ):
        captured["provider"] = provider
        captured["model"] = model
        captured["prompt"] = prompt
        captured["api_key"] = api_key
        return make_result(provider=provider, model=model)

    monkeypatch.setattr("llm_gateway_bench.bench.run_benchmark", fake_run_benchmark)

    cfg = BenchConfig(
        prompts=["Ping"],
        providers=[
            ProviderConfig(
                name="openai",
                model="gpt-4o-mini",
                api_key="yaml-key",
            )
        ],
        settings=SettingsConfig(requests=2, concurrency=1, timeout=5),
    )

    results = compare_providers(cfg)

    assert len(results) == 1
    assert captured["provider"] == "openai"
    assert captured["model"] == "gpt-4o-mini"
    assert captured["prompt"] == "Ping"
    assert captured["api_key"] == "yaml-key"
