"""Basic tests for llm-gateway-bench."""

import pytest
from llm_gateway_bench.bench import BenchResult
from llm_gateway_bench.report import generate_report
import tempfile
import os
import json


def make_result(provider="openai", model="gpt-4o-mini"):
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
        with open(path) as f:
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
        with open(path) as f:
            content = f.read()
        assert "openai" in content
        assert "gpt-4o-mini" in content
    finally:
        os.unlink(path)
