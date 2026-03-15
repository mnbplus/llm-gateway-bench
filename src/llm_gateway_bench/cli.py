"""CLI entry point for llm-gateway-bench."""
from __future__ import annotations

import asyncio
import platform
import sys

import click
from rich import box
from rich.console import Console
from rich.table import Table

from . import __version__
from .bench import BenchmarkRunner
from .config import load_config
from .formatters import ResultFormatter

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="lgb")
def cli():
    """lgb - Benchmark LLM API gateways with ease.

    Examples:

    \b
      lgb run --config bench.yaml
      lgb run --config bench.yaml --save
      lgb history
      lgb history --compare bench_20240101_120000 bench_20240102_130000
      lgb providers
      lgb version
    """


@cli.command()
@click.option(
    "--config", "-c",
    default="bench.yaml",
    show_default=True,
    help="Path to the benchmark config YAML file.",
)
@click.option(
    "--output", "-o",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    show_default=True,
    help="Output format for results.",
)
@click.option(
    "--save", "-s",
    is_flag=True,
    help="Save results to local history (~/.lgb/history/).",
)
@click.option(
    "--runs", "-r",
    default=None,
    type=int,
    help="Number of benchmark runs per provider (overrides config value).",
)
@click.option(
    "--warmup", "-w",
    is_flag=True,
    help="Send one warmup request per provider before benchmarking.",
)
def run(config, output, save, runs, warmup):
    """Run benchmarks against all configured providers.

    Reads provider definitions from CONFIG (default: bench.yaml) and
    executes concurrent requests to measure latency, throughput, and
    error rates.

    Examples:

    \b
      lgb run
      lgb run --config custom.yaml --runs 20 --save
      lgb run --output json > results.json
      lgb run --warmup --save
    """
    cfg = load_config(config)
    if runs:
        cfg.runs = runs

    if warmup:
        from .warmup import WarmupChecker
        checker = WarmupChecker(cfg)
        asyncio.run(checker.run_warmup())

    runner = BenchmarkRunner(cfg)
    results = asyncio.run(runner.run_all())
    formatter = ResultFormatter()

    if output == "table":
        formatter.print_table(results)
        formatter.print_latency_histogram(results)
    elif output == "json":
        formatter.print_json(results)
    elif output == "csv":
        formatter.print_csv(results)

    if save:
        from .history import HistoryManager
        hm = HistoryManager()
        path = hm.save(results, cfg)
        console.print(f"[green]Results saved:[/green] {path}")


@cli.command(name="version")
def version_cmd():
    """Show version, Python, and platform information.

    Useful for bug reports and verifying your installation.
    """
    console.print(f"[bold cyan]lgb[/bold cyan] version [bold]{__version__}[/bold]")
    console.print(f"Python      {sys.version}")
    console.print(f"Platform    {platform.platform()}")
    console.print(f"Machine     {platform.machine()}")


@cli.command()
def providers():
    """List all providers defined in bench.yaml.

    Shows provider name, base URL, and model for each configured
    entry. Requires a bench.yaml file in the current directory.

    Examples:

    \b
      lgb providers
    """
    try:
        cfg = load_config("bench.yaml")
    except Exception:
        console.print("[yellow]No bench.yaml found.[/yellow] Create one to get started.")
        return

    table = Table(
        title="Configured Providers",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", justify="right", width=3)
    table.add_column("Name", style="bold")
    table.add_column("Base URL", style="blue")
    table.add_column("Model", style="green")

    for idx, p in enumerate(cfg.providers, 1):
        table.add_row(
            str(idx),
            p.name,
            p.base_url,
            getattr(p, "model", "-"),
        )

    console.print(table)
    console.print(f"[dim]Total: {len(cfg.providers)} provider(s)[/dim]")


@cli.group(invoke_without_command=True)
@click.option(
    "--compare",
    nargs=2,
    metavar="<ID1> <ID2>",
    default=(None, None),
    help="Compare two benchmark runs side by side.",
)
@click.pass_context
def history(ctx, compare):
    """List and compare historical benchmark runs.

    History entries are stored in ~/.lgb/history/ when you run
    `lgb run --save`.

    Examples:

    \b
      lgb history
      lgb history --compare bench_20240101_120000 bench_20240102_130000
    """
    from .history import HistoryManager
    hm = HistoryManager()

    id1, id2 = compare
    if id1 and id2:
        _compare_runs(hm, id1, id2)
        return

    if ctx.invoked_subcommand is None:
        _list_history(hm)


def _list_history(hm) -> None:
    """Print a table of all saved benchmark runs."""
    entries = hm.list()
    if not entries:
        console.print(
            "[yellow]No history found.[/yellow] "
            "Run `lgb run --save` to record results."
        )
        return

    table = Table(
        title="Benchmark History",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", justify="right", width=4)
    table.add_column("ID", style="bold", no_wrap=True)
    table.add_column("Timestamp", style="dim")
    table.add_column("Providers", justify="right")

    for idx, entry in enumerate(entries, 1):
        table.add_row(
            str(idx),
            entry["id"],
            entry["timestamp"],
            str(entry["providers"]),
        )

    console.print(table)
    console.print(f"[dim]{len(entries)} run(s) saved in {hm.history_dir}[/dim]")


def _compare_runs(hm, id1: str, id2: str) -> None:
    """Print a side-by-side comparison of two benchmark runs."""
    try:
        data1 = hm.load(id1)
        data2 = hm.load(id2)
    except FileNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise SystemExit(1) from exc

    results1 = {r["provider"]: r for r in data1.get("results", [])}
    results2 = {r["provider"]: r for r in data2.get("results", [])}
    all_providers = sorted(set(results1) | set(results2))

    table = Table(
        title=f"Comparison: {id1}  vs  {id2}",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Provider", style="bold")
    table.add_column(f"{id1[:16]}\nAvg Latency", justify="right")
    table.add_column(f"{id2[:16]}\nAvg Latency", justify="right")
    table.add_column("Delta", justify="right")
    table.add_column(f"{id1[:16]}\nTokens/s", justify="right")
    table.add_column(f"{id2[:16]}\nTokens/s", justify="right")

    for provider in all_providers:
        r1 = results1.get(provider)
        r2 = results2.get(provider)

        lat1 = f"{r1['avg_latency']:.2f}s" if r1 else "[dim]—[/dim]"
        lat2 = f"{r2['avg_latency']:.2f}s" if r2 else "[dim]—[/dim]"
        tps1 = f"{r1['avg_tokens_per_second']:.1f}" if r1 else "[dim]—[/dim]"
        tps2 = f"{r2['avg_tokens_per_second']:.1f}" if r2 else "[dim]—[/dim]"

        if r1 and r2:
            delta_val = r2["avg_latency"] - r1["avg_latency"]
            sign = "+" if delta_val > 0 else ""
            color = "green" if delta_val < 0 else "red" if delta_val > 0 else "dim"
            delta = f"[{color}]{sign}{delta_val:.2f}s[/{color}]"
        else:
            delta = "[dim]—[/dim]"

        table.add_row(provider, lat1, lat2, delta, tps1, tps2)

    console.print(table)


@cli.command()
@click.argument("config_file", default="bench.yaml", required=False)
@click.option(
    "--timeout", "-t",
    default=10.0,
    show_default=True,
    help="Timeout in seconds for each warmup request.",
)
def warmup(config_file, timeout):
    """Send a warmup request to each provider and check reachability.

    Useful for verifying all providers are reachable before a full
    benchmark run. Exits with code 1 if any provider fails.

    Examples:

    \b
      lgb warmup
      lgb warmup bench.yaml --timeout 15
    """
    from .warmup import WarmupChecker
    cfg = load_config(config_file)
    checker = WarmupChecker(cfg, timeout=timeout)
    ok = asyncio.run(checker.run_warmup())
    if not ok:
        raise SystemExit(1)


def main() -> None:
    cli()
