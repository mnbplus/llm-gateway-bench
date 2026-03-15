"""Report generation for benchmark results."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .models import BenchResult


def generate_report(results: List[BenchResult], output_path: str) -> None:
    """Generate a report in md, json, or csv format based on file extension."""
    ext = Path(output_path).suffix.lower()

    if ext == ".json":
        _write_json(results, output_path)
    elif ext == ".csv":
        _write_csv(results, output_path)
    else:
        _write_markdown(results, output_path)


def _write_markdown(results: List[BenchResult], path: str) -> None:
    lines = [
        "# LLM Gateway Bench Report\n",
        "| Provider | Model | TTFT (ms) | Total (ms) | Tokens/sec | P95 (ms) | Success Rate |\n",
        "|----------|-------|-----------|------------|------------|----------|--------------|\n",
    ]
    for r in results:
        lines.append(
            f"| {r.provider} | {r.model} | {r.ttft_ms:.0f} | {r.total_ms:.0f} "
            f"| {r.tokens_per_sec:.1f} | {r.p95_ms:.0f} | {r.success_rate:.0%} |\n"
        )
    Path(path).write_text("".join(lines), encoding="utf-8")


def _write_json(results: List[BenchResult], path: str) -> None:
    data = [
        {
            "provider": r.provider,
            "model": r.model,
            "ttft_ms": r.ttft_ms,
            "total_ms": r.total_ms,
            "tokens_per_sec": r.tokens_per_sec,
            "p95_ms": r.p95_ms,
            "p50_ms": r.p50_ms,
            "success_rate": r.success_rate,
            "errors": r.errors,
            "total_tokens": r.total_tokens,
        }
        for r in results
    ]
    Path(path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def _write_csv(results: List[BenchResult], path: str) -> None:
    fields = [
        "provider",
        "model",
        "ttft_ms",
        "total_ms",
        "tokens_per_sec",
        "p95_ms",
        "p50_ms",
        "success_rate",
        "errors",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow({k: getattr(r, k) for k in fields})
