"""Tests for llm_gateway_bench.formatters."""

from rich.text import Text

from llm_gateway_bench.formatters import (
    _best_worst,
    _style_extrema,
    compare_table,
    latency_histogram_table,
    results_table,
)
from llm_gateway_bench.models import BenchResult


def make_result(
    provider: str = "openai",
    model: str = "gpt-4o-mini",
    ttft_ms: float = 312.0,
    total_ms: float = 1840.0,
    tokens_per_sec: float = 68.2,
    success_rate: float = 1.0,
    p95_ms: float = 2100.0,
) -> BenchResult:
    return BenchResult(
        provider=provider,
        model=model,
        ttft_ms=ttft_ms,
        total_ms=total_ms,
        tokens_per_sec=tokens_per_sec,
        success_rate=success_rate,
        p95_ms=p95_ms,
        p50_ms=1800.0,
        errors=0,
        total_tokens=150,
    )


def test_best_worst_higher_better():
    vals = [1.0, 2.0, 3.0]
    best, worst = _best_worst(vals, higher_is_better=True)
    assert best == 3.0
    assert worst == 1.0


def test_best_worst_lower_better():
    vals = [1.0, 2.0, 3.0]
    best, worst = _best_worst(vals, higher_is_better=False)
    assert best == 1.0
    assert worst == 3.0


def test_best_worst_empty():
    best, worst = _best_worst([], higher_is_better=True)
    assert best == 0.0
    assert worst == 0.0


def test_style_extrema_best_lower():
    text = _style_extrema("100", 100, 100, 200, better_when_higher=False)
    assert isinstance(text, Text)
    assert "green" in text.style


def test_style_extrema_worst_lower():
    text = _style_extrema("200", 200, 100, 200, better_when_higher=False)
    assert "red" in text.style


def test_results_table_basic():
    r1 = make_result()
    r2 = make_result("deepseek", "deepseek-chat", ttft_ms=400, total_ms=2000)

    table = results_table([r1, r2])
    # Check that table has rows
    assert table.row_count == 2


def test_latency_histogram_table_empty():
    t = latency_histogram_table([])
    assert t.row_count >= 1  # at least one row with placeholder


def test_latency_histogram_table_basic():
    latencies = [100, 150, 200, 250, 300, 350, 400, 450, 500, 550]
    t = latency_histogram_table(latencies, bins=5)
    assert t.row_count == 5


def test_compare_table_basic():
    left = make_result(ttft_ms=300, total_ms=1800, tokens_per_sec=50)
    right = make_result(ttft_ms=400, total_ms=2000, tokens_per_sec=60)

    t = compare_table(left, right, left_name="run1", right_name="run2")
    assert t.row_count == 5  # 5 metrics


def test_compare_table_missing():
    t = compare_table(None, None, left_name="a", right_name="b")
    assert t.row_count == 1  # placeholder row
