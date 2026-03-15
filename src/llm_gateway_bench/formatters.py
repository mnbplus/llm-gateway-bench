"""Rich formatting helpers for llm-gateway-bench.

This module focuses on *presentation*:
- Progress bars for request execution
- ASCII latency distribution charts (horizontal bars)
- Highlighting best/worst values in comparison tables
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator, List, Sequence, Tuple

from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

from .models import BenchResult


def make_progress() -> Progress:
    """Create a nice default progress bar."""

    return Progress(
        SpinnerColumn(),
        TextColumn("[bold]{task.description}[/bold]"),
        BarColumn(bar_width=None),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        transient=True,
    )


@dataclass(frozen=True)
class ProgressHandle:
    progress: Progress
    task_id: TaskID

    def advance(self, step: int = 1) -> None:
        self.progress.advance(self.task_id, step)


@contextmanager
def request_progress(description: str, total: int) -> Iterator[ProgressHandle]:
    """Context manager that renders a Rich progress bar for ``total`` steps."""

    progress = make_progress()
    with progress:
        task_id = progress.add_task(description, total=total)
        yield ProgressHandle(progress=progress, task_id=task_id)


def _best_worst(values: Sequence[float], higher_is_better: bool) -> Tuple[float, float]:
    if not values:
        return (0.0, 0.0)
    if higher_is_better:
        return (max(values), min(values))
    return (min(values), max(values))


def _style_extrema(
    value: str,
    raw_value: float,
    best: float,
    worst: float,
    *,
    better_when_higher: bool,
) -> Text:
    """Colorize best (green) and worst (red) values."""

    if raw_value == best and raw_value == worst:
        return Text(value)

    if better_when_higher:
        if raw_value == best:
            return Text(value, style="bold green")
        if raw_value == worst:
            return Text(value, style="bold red")
        return Text(value)

    # lower is better
    if raw_value == best:
        return Text(value, style="bold green")
    if raw_value == worst:
        return Text(value, style="bold red")
    return Text(value)


def results_table(results: List[BenchResult]) -> Table:
    """Render results as a Rich table with best/worst highlighting."""

    table = Table(title="Benchmark Results")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="white")
    table.add_column("TTFT (ms)", justify="right")
    table.add_column("Total (ms)", justify="right")
    table.add_column("Tokens/sec", justify="right")
    table.add_column("Success", justify="right")
    table.add_column("P95 (ms)", justify="right")

    ttft_vals = [r.ttft_ms for r in results]
    total_vals = [r.total_ms for r in results]
    tps_vals = [r.tokens_per_sec for r in results]
    succ_vals = [r.success_rate for r in results]
    p95_vals = [r.p95_ms for r in results]

    ttft_best, ttft_worst = _best_worst(ttft_vals, higher_is_better=False)
    total_best, total_worst = _best_worst(total_vals, higher_is_better=False)
    tps_best, tps_worst = _best_worst(tps_vals, higher_is_better=True)
    succ_best, succ_worst = _best_worst(succ_vals, higher_is_better=True)
    p95_best, p95_worst = _best_worst(p95_vals, higher_is_better=False)

    for r in results:
        table.add_row(
            r.provider,
            r.model,
            _style_extrema(f"{r.ttft_ms:.0f}", r.ttft_ms, ttft_best, ttft_worst, better_when_higher=False),
            _style_extrema(
                f"{r.total_ms:.0f}", r.total_ms, total_best, total_worst, better_when_higher=False
            ),
            _style_extrema(
                f"{r.tokens_per_sec:.1f}",
                r.tokens_per_sec,
                tps_best,
                tps_worst,
                better_when_higher=True,
            ),
            _style_extrema(
                f"{r.success_rate:.0%}",
                r.success_rate,
                succ_best,
                succ_worst,
                better_when_higher=True,
            ),
            _style_extrema(f"{r.p95_ms:.0f}", r.p95_ms, p95_best, p95_worst, better_when_higher=False),
        )

    return table


def _histogram_bins(latencies: Sequence[float], bins: int) -> List[Tuple[float, float, int]]:
    if not latencies:
        return []
    lo = min(latencies)
    hi = max(latencies)
    if hi == lo:
        return [(lo, hi, len(latencies))]

    step = (hi - lo) / bins
    edges = [lo + i * step for i in range(bins)] + [hi]

    counts = [0 for _ in range(bins)]
    for v in latencies:
        # put max into the last bin
        idx = min(int((v - lo) / step), bins - 1)
        counts[idx] += 1

    out: List[Tuple[float, float, int]] = []
    for i, c in enumerate(counts):
        start = edges[i]
        end = edges[i + 1]
        out.append((start, end, c))
    return out


def latency_histogram_table(
    latencies_ms: Sequence[float], *, bins: int = 10, width: int = 36
) -> Table:
    """ASCII horizontal bar chart for latency distribution."""

    t = Table(title="Latency Distribution", show_header=True, header_style="bold")
    t.add_column("Bucket (ms)", style="dim")
    t.add_column("Count", justify="right")
    t.add_column("Bar")

    data = _histogram_bins(list(latencies_ms), bins=bins)
    if not data:
        t.add_row("—", "0", "")
        return t

    max_count = max(c for _, _, c in data) or 1

    for start, end, c in data:
        frac = c / max_count
        bar_len = max(0, int(frac * width))
        bar = "█" * bar_len

        # simple color ramp
        if frac >= 0.66:
            style = "bold red"
        elif frac >= 0.33:
            style = "yellow"
        else:
            style = "green"

        label = f"{start:,.0f}–{end:,.0f}"
        t.add_row(label, str(c), Text(bar, style=style))

    return t


def render_results(console: Console, results: List[BenchResult]) -> None:
    console.print(results_table(results))

    # Show latency distributions when raw latencies are available
    for r in results:
        if not r.raw_latencies:
            continue
        console.print(
            Panel(
                latency_histogram_table(r.raw_latencies),
                title=f"{r.provider}/{r.model}",
                border_style="cyan",
            )
        )


def compare_table(
    left: BenchResult, right: BenchResult, *, left_name: str, right_name: str
) -> Table:
    """A small comparison table for two runs of the same provider/model."""

    t = Table(title=f"Compare: {left_name} vs {right_name}")
    t.add_column("Metric", style="cyan")
    t.add_column(left_name, justify="right")
    t.add_column(right_name, justify="right")
    t.add_column("Δ", justify="right")

    def row(metric: str, a: float, b: float, *, lower_is_better: bool) -> None:
        delta = b - a
        if lower_is_better:
            # improvement when delta < 0
            style = "green" if delta < 0 else ("red" if delta > 0 else "dim")
        else:
            style = "green" if delta > 0 else ("red" if delta < 0 else "dim")
        t.add_row(
            metric,
            f"{a:,.2f}",
            f"{b:,.2f}",
            Text(f"{delta:+,.2f}", style=style),
        )

    row("TTFT (ms)", left.ttft_ms, right.ttft_ms, lower_is_better=True)
    row("Total (ms)", left.total_ms, right.total_ms, lower_is_better=True)
    row("P95 (ms)", left.p95_ms, right.p95_ms, lower_is_better=True)
    row("Tokens/sec", left.tokens_per_sec, right.tokens_per_sec, lower_is_better=False)
    row("Success rate", left.success_rate * 100, right.success_rate * 100, lower_is_better=False)

    return t
