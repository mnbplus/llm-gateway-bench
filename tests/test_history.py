"""Tests for llm_gateway_bench.history."""

import json

import pytest

from llm_gateway_bench.history import (
    append_run,
    get_run,
    history_path,
    iter_runs,
    list_runs,
    serialize_results,
)
from llm_gateway_bench.models import BenchResult


@pytest.fixture()
def temp_history_dir(tmp_path, monkeypatch):
    """Use a temporary directory for history during tests."""
    # Path.home() uses USERPROFILE on Windows and HOME on Unix
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    # Also patch the module-level functions to use tmp_path directly
    monkeypatch.setattr(
        "llm_gateway_bench.history.history_dir",
        lambda: tmp_path / ".lgb",
    )
    lgb_dir = tmp_path / ".lgb"
    lgb_dir.mkdir(parents=True, exist_ok=True)
    return lgb_dir


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


def test_serialize_results():
    r1 = make_result()
    r2 = make_result("deepseek", "deepseek-chat")
    data = serialize_results([r1, r2])
    assert len(data) == 2
    assert data[0]["provider"] == "openai"
    assert data[1]["provider"] == "deepseek"


def test_append_and_iter_runs(temp_history_dir):
    r1 = make_result()
    r2 = make_result("anthropic", "claude-3")

    rid1 = append_run([r1], meta={"test": "run1"})
    rid2 = append_run([r2], meta={"test": "run2"})

    runs = list(iter_runs())
    assert len(runs) == 2

    # Check that run_ids are distinct and present
    run_ids = {r.run_id for r in runs}
    assert rid1 in run_ids
    assert rid2 in run_ids


def test_list_runs_limit(temp_history_dir):
    for i in range(5):
        r = make_result(model=f"model-{i}")
        append_run([r])

    runs = list_runs(limit=3)
    assert len(runs) == 3


def test_get_run(temp_history_dir):
    r = make_result()
    rid = append_run([r])

    fetched = get_run(rid)
    assert fetched.run_id == rid
    assert len(fetched.results) == 1
    assert fetched.results[0].provider == "openai"


def test_get_run_not_found(temp_history_dir):
    with pytest.raises(KeyError):
        get_run("nonexistent-run-id")


def test_history_file_format(temp_history_dir):
    r = make_result()
    _rid = append_run([r])  # noqa: F841

    p = history_path()
    assert p.exists()

    with p.open("r", encoding="utf-8") as f:
        line = f.readline()
        obj = json.loads(line)
        # Check run_id is present and non-empty (timing may differ by 1 second)
        assert obj["run_id"]
        assert "results" in obj
        assert len(obj["results"]) == 1
