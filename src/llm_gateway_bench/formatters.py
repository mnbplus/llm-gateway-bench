"""Output formatters for benchmark results."""
from __future__ import annotations

import csv
import io
import json
from typing import Any, List, Optional, Sequence, Tuple

from rich import box
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)
from rich.table import Table
from rich.text import Text

console = Console()


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------

def make_progress() -> Progress:
    """Return a Rich Progress bar configured for benchmark runs."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(bar_width=None),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False,
    )


# ---------------------------------------------------------------------------
# Best / worst highlighting helpers
# ---------------------------------------------------------------------------

def _best_worst(
    values: Sequence[float], *, higher_is_better: bool
) -> Tuple[float, float]:
    """Return (best, worst) from values."""
    if not values:
        return (0.0, 0.0)
    return (max(values), min(values)) if higher_is_better else (min(values), max(values))


def _style_extrema(
    value: str,
    raw_value: float,
    best: float,
    worst: float,
    *,
    better_when_higher: bool,
) -> Text:
    """Colorize best (green) and worst (red) values.

    Parameters
    ----------
    value:           formatted string to display
    raw_value:       numeric value used for comparison
    best:            the best value in the set
    worst:           the worst value in the set
    better_when_higher: True if higher raw values are better
    """
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


# Alias used internally
_highlight = _style_extrema


# ---------------------------------------------------------------------------
# ASCII horizontal histogram
# ---------------------------------------------------------------------------

def _histogram_bins(
    latencies: Sequence[float], bins: int
) -> List[Tuple[float, float, int]]:
    """Bucket latencies into bins equal-width buckets."""
    if not latencies:
        return []
    lo, hi = min(latencies), max(latencies)
    if hi == lo:
        return [(lo, hi, len(latencies))]
    step = (hi - lo) / bins
    counts = [0] * bins
    for v in latencies:
        idx = min(int((v - lo) / step), bins - 1)
        counts[idx] += 1
    return [(lo + i * step, lo + (i + 1) * step, c) for i, c in enumerate(counts)]


def latency_histogram_table(
    latencies_ms: Sequence[float], *, bins: int = 10, width: int = 36
) -> Table:
    """Return a Rich Table with a horizontal ASCII bar chart for latency distribution."""
    t = Table(title="Latency Distribution", show_header=True, header_style="bold")
    t.add_column("Bucket (ms)", style="dim")
    t.add_column("Count", justify="right")
    t.add_column("Bar")

    data = _histogram_bins(list(latencies_ms), bins=bins)
    if not data:
        t.add_row("\u2014", "0", "")
        return t

    max_count = max(c for _, _, c in data) or 1

    for start, end, c in data:
        frac = c / max_count
        bar_len = max(0, int(frac * width))
        bar = "\u2588" * bar_len

        if frac >= 0.66:
            style = "bold red"
        elif frac >= 0.33:
            style = "yellow"
        else:
            style = "green"

        label = f"{start:,.0f}\u2013{end:,.0f}"
        t.add_row(label, str(c), Text(bar, style=style))

    return t


# ---------------------------------------------------------------------------
# Full results table (used by tests and render_results)
# ---------------------------------------------------------------------------

def results_table(results: List[Any]) -> Table:
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
            _style_extrema(
                f"{r.ttft_ms:.0f}", r.ttft_ms,
                ttft_best, ttft_worst, better_when_higher=False,
            ),
            _style_extrema(
                f"{r.total_ms:.0f}", r.total_ms,
                total_best, total_worst, better_when_higher=False,
            ),
            _style_extrema(
                f"{r.tokens_per_sec:.1f}", r.tokens_per_sec,
                tps_best, tps_worst, better_when_higher=True,
            ),
            _style_extrema(
                f"{r.success_rate:.0%}", r.success_rate,
                succ_best, succ_worst, better_when_higher=True,
            ),
            _style_extrema(
                f"{r.p95_ms:.0f}", r.p95_ms,
                p95_best, p95_worst, better_when_higher=False,
            ),
        )

    return table


def compare_table(
    left: Optional[Any],
    right: Optional[Any],
    *,
    left_name: str,
    right_name: str,
) -> Table:
    """A small comparison table for two runs of the same provider/model."""
    t = Table(title=f"Compare: {left_name} vs {right_name}")
    t.add_column("Metric", style="cyan")
    t.add_column(left_name, justify="right")
    t.add_column(right_name, justify="right")
    t.add_column("\u0394", justify="right")

    if left is None or right is None:
        t.add_row("\u2014", "missing data", "missing data", "\u2014")
        return t

    def row(metric: str, a: float, b: float, *, lower_is_better: bool) -> None:
        delta = b - a
        if lower_is_better:
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


def render_results(con: Console, results: List[Any]) -> None:
    """Print results table + per-provider latency histograms."""
    con.print(results_table(results))
    for r in results:
        raw: List[float] = []
        if hasattr(r, "raw_latencies") and r.raw_latencies:
            raw = list(r.raw_latencies)
        elif hasattr(r, "latencies") and r.latencies:
            raw = list(r.latencies)
        if raw:
            con.print(latency_histogram_table(raw))


# ---------------------------------------------------------------------------
# ResultFormatter class (used by cli.py)
# ---------------------------------------------------------------------------

class ResultFormatter:
    """Render benchmark results in multiple formats."""

    def print_table(self, results: List[Any]) -> None:
        """Print a Rich table with best/worst latency highlighted."""
        if not results:
            console.print("[yellow]No results to display.[/yellow]")
            return

        avg_lats = [r.avg_latency for r in results]
        p50s = [r.p50_latency for r in results]
        p95s = [r.p95_latency for r in results]
        tpss = [r.avg_tokens_per_second for r in results]
        succs = [r.success_rate for r in results]

        avg_best, avg_worst = _best_worst(avg_lats, higher_is_better=False)
        p50_best, p50_worst = _best_worst(p50s, higher_is_better=False)
        p95_best, p95_worst = _best_worst(p95s, higher_is_better=False)
        tps_best, tps_worst = _best_worst(tpss, higher_is_better=True)
        succ_best, succ_worst = _best_worst(succs, higher_is_better=True)

        table = Table(
            title="[bold]Benchmark Results[/bold]",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
            border_style="bright_black",
        )
        table.add_column("Provider", style="bold", min_width=12)
        table.add_column("Model", style="dim")
        table.add_column("Avg Latency", justify="right")
        table.add_column("P50", justify="right")
        table.add_column("P95", justify="right")
        table.add_column("Tokens/s", justify="right")
        table.add_column("Success", justify="right")
        table.add_column("Errors", justify="right")

        for r in results:
            table.add_row(
                r.provider,
                r.model,
                _style_extrema(
                    f"{r.avg_latency:.2f}s", r.avg_latency,
                    avg_best, avg_worst, better_when_higher=False,
                ),
                _style_extrema(
                    f"{r.p50_latency:.2f}s", r.p50_latency,
                    p50_best, p50_worst, better_when_higher=False,
                ),
                _style_extrema(
                    f"{r.p95_latency:.2f}s", r.p95_latency,
                    p95_best, p95_worst, better_when_higher=False,
                ),
                _style_extrema(
                    f"{r.avg_tokens_per_second:.1f}", r.avg_tokens_per_second,
                    tps_best, tps_worst, better_when_higher=True,
                ),
                _style_extrema(
                    f"{r.success_rate:.0%}", r.success_rate,
                    succ_best, succ_worst, better_when_higher=True,
                ),
                str(r.error_count),
            )

        console.print(table)

    def print_latency_histogram(
        self, results: List[Any], *, bins: int = 8, bar_width: int = 40
    ) -> None:
        """Print a horizontal ASCII bar chart of latency distribution per provider."""
        for r in results:
            raw: List[float] = []
            if hasattr(r, "raw_latencies") and r.raw_latencies:
                raw = list(r.raw_latencies)
            elif hasattr(r, "latencies") and r.latencies:
                raw = list(r.latencies)

            if not raw:
                continue

            data = _histogram_bins(raw, bins)
            max_count = max(c for _, _, c in data) or 1

            table = Table(
                title=f"Latency Distribution \u2014 {r.provider}",
                box=box.SIMPLE,
                show_header=True,
                header_style="dim",
                border_style="bright_black",
                show_edge=False,
            )
            table.add_column("Bucket (s)", style="dim", min_width=16, no_wrap=True)
            table.add_column("n", justify="right", width=5)
            table.add_column("Bar", min_width=bar_width)

            for lo, hi, count in data:
                frac = count / max_count
                filled = max(1 if count else 0, int(frac * bar_width))
                bar_str = "\u2588" * filled

                if frac >= 0.75:
                    bar_style = "bold red"
                elif frac >= 0.4:
                    bar_style = "yellow"
                else:
                    bar_style = "green"

                table.add_row(
                    f"{lo:.3f}\u2013{hi:.3f}",
                    str(count),
                    Text(bar_str, style=bar_style),
                )

            console.print(table)

    def print_json(self, results: List[Any]) -> None:
        """Print results as formatted JSON."""
        data = [r.model_dump() if hasattr(r, "model_dump") else r for r in results]
        console.print_json(json.dumps(data, default=str))

    def print_csv(self, results: List[Any]) -> None:
        """Print results as CSV to stdout."""
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow([
            "provider", "model", "avg_latency", "p50", "p95",
            "tokens_per_second", "success_rate", "errors",
        ])
        for r in results:
            writer.writerow([
                r.provider,
                r.model,
                r.avg_latency,
                r.p50_latency,
                r.p95_latency,
                r.avg_tokens_per_second,
                r.success_rate,
                r.error_count,
            ])
        print(buf.getvalue(), end="")
