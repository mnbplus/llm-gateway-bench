"""CLI entry point for llm-gateway-bench."""

from __future__ import annotations

import asyncio
import platform
import sys
from typing import Dict, Iterable, Optional, Sequence, Tuple

import click
from rich import box
from rich.console import Console
from rich.table import Table

from . import __version__
from .bench import compare_providers, run_benchmark
from .config import load_config
from .exceptions import ConfigError, LlmGatewayBenchError
from .formatters import ResultFormatter, compare_table
from .history import append_run, compare_runs, list_runs
from .models import BenchConfig, BenchResult, ProviderConfig, SettingsConfig
from .providers import PROVIDER_DEFAULTS
from .report import generate_report
from .warmup import WarmupChecker

console = Console()


def _print_results(
    results: Sequence[BenchResult],
    *,
    output_format: str,
    show_histogram: bool = True,
) -> None:
    formatter = ResultFormatter()
    if output_format == "table":
        formatter.print_table(list(results))
        if show_histogram:
            formatter.print_latency_histogram(list(results))
    elif output_format == "json":
        formatter.print_json(list(results))
    elif output_format == "csv":
        formatter.print_csv(list(results))
    else:  # pragma: no cover - click constrains this
        raise click.UsageError(f"Unsupported output format: {output_format}")


def _save_results(
    results: Sequence[BenchResult],
    *,
    meta: Optional[Dict[str, object]] = None,
) -> str:
    run_id = append_run(results, meta=meta or {})
    console.print(f"[green]Saved history run:[/green] {run_id}")
    return run_id


def _write_report(results: Sequence[BenchResult], output_path: Optional[str]) -> None:
    if not output_path:
        return
    generate_report(list(results), output_path)
    console.print(f"[green]Wrote report:[/green] {output_path}")


def _single_provider_config(
    *,
    provider: str,
    model: str,
    base_url: Optional[str],
    api_key: Optional[str],
    prompt: str,
    requests: int,
    concurrency: int,
    timeout: int,
) -> BenchConfig:
    return BenchConfig(
        prompts=[prompt],
        providers=[
            ProviderConfig(
                name=provider,
                model=model,
                base_url=base_url,
                api_key=api_key,
            )
        ],
        settings=SettingsConfig(
            requests=requests,
            concurrency=concurrency,
            timeout=timeout,
        ),
    )


def _history_index(results: Iterable[BenchResult]) -> dict[Tuple[str, str], BenchResult]:
    return {(r.provider, r.model): r for r in results}


@click.group()
@click.version_option(version=__version__, prog_name="lgb")
def cli() -> None:
    """Benchmark LLM API gateways with a single-provider or YAML-driven workflow."""


@cli.command()
@click.option("--provider", required=True, help="Provider name, such as openai or custom.")
@click.option("--model", required=True, help="Model identifier to benchmark.")
@click.option("--base-url", default=None, help="Optional OpenAI-compatible base URL.")
@click.option("--api-key", default=None, help="Explicit API key. Defaults to env var lookup.")
@click.option("--prompt", default="Say hello.", show_default=True, help="Prompt text.")
@click.option("--requests", default=20, show_default=True, type=int, help="Total requests.")
@click.option("--concurrency", default=3, show_default=True, type=int, help="Concurrent requests.")
@click.option("--timeout", default=30, show_default=True, type=int, help="Per-request timeout in seconds.")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    show_default=True,
    help="Stdout format.",
)
@click.option("--output", default=None, help="Optional report path (.md, .json, or .csv).")
@click.option("--save", is_flag=True, help="Save the run to local history (~/.lgb/history.jsonl).")
@click.option("--warmup/--no-warmup", default=False, show_default=True, help="Run a reachability warmup before benchmarking.")
def run(
    provider: str,
    model: str,
    base_url: Optional[str],
    api_key: Optional[str],
    prompt: str,
    requests: int,
    concurrency: int,
    timeout: int,
    output_format: str,
    output: Optional[str],
    save: bool,
    warmup: bool,
) -> None:
    """Run a benchmark for a single provider/model pair."""

    cfg = _single_provider_config(
        provider=provider,
        model=model,
        base_url=base_url,
        api_key=api_key,
        prompt=prompt,
        requests=requests,
        concurrency=concurrency,
        timeout=timeout,
    )

    if warmup:
        ok = asyncio.run(WarmupChecker(cfg, timeout=float(timeout)).run_warmup())
        if not ok:
            raise SystemExit(1)

    result = run_benchmark(
        provider=provider,
        model=model,
        prompt=prompt,
        n_requests=requests,
        concurrency=concurrency,
        base_url=base_url,
        api_key=api_key,
        timeout=timeout,
    )
    results = [result]
    _print_results(results, output_format=output_format, show_histogram=output_format == "table")
    _write_report(results, output)

    if save:
        _save_results(
            results,
            meta={
                "mode": "run",
                "provider": provider,
                "model": model,
                "requests": requests,
                "concurrency": concurrency,
                "timeout": timeout,
            },
        )


@cli.command()
@click.argument("config_file", default="bench.yaml", required=False)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    show_default=True,
    help="Stdout format.",
)
@click.option("--output", default=None, help="Optional report path (.md, .json, or .csv).")
@click.option("--save", is_flag=True, help="Save the run to local history (~/.lgb/history.jsonl).")
@click.option("--warmup/--no-warmup", default=False, show_default=True, help="Run a reachability warmup before benchmarking.")
def compare(
    config_file: str,
    output_format: str,
    output: Optional[str],
    save: bool,
    warmup: bool,
) -> None:
    """Run a YAML-defined benchmark across multiple providers."""

    cfg = load_config(config_file)

    if warmup:
        ok = asyncio.run(WarmupChecker(cfg, timeout=float(cfg.settings.timeout)).run_warmup())
        if not ok:
            raise SystemExit(1)

    results = compare_providers(cfg)
    _print_results(results, output_format=output_format, show_histogram=output_format == "table")
    _write_report(results, output)

    if save:
        _save_results(
            results,
            meta={
                "mode": "compare",
                "config_file": config_file,
                "provider_count": len(cfg.providers),
            },
        )


@cli.command()
def providers() -> None:
    """List built-in provider defaults."""

    table = Table(
        title="Built-in Providers",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Provider", style="bold")
    table.add_column("Default Base URL", style="blue")
    table.add_column("Env Var", style="green")

    for name in sorted(PROVIDER_DEFAULTS):
        defaults = PROVIDER_DEFAULTS[name]
        base_url = defaults.get("base_url", "-")
        env_key = defaults.get("env_key") or "(none)"
        table.add_row(name, base_url, env_key)

    table.add_row("custom", "(required via --base-url or YAML)", "(explicit api_key or none)")
    console.print(table)
    console.print(f"[dim]Total: {len(PROVIDER_DEFAULTS) + 1} provider targets[/dim]")


@cli.group(invoke_without_command=True)
@click.option(
    "--compare",
    nargs=2,
    metavar="<ID1> <ID2>",
    default=(None, None),
    help="Compare two saved runs side by side.",
)
@click.option("--limit", default=20, show_default=True, type=int, help="Number of runs to list.")
@click.pass_context
def history(
    ctx: click.Context,
    compare: Tuple[Optional[str], Optional[str]],
    limit: int,
) -> None:
    """List and compare historical benchmark runs."""

    left_id, right_id = compare
    if left_id and right_id:
        _compare_history(left_id, right_id)
        return

    if ctx.invoked_subcommand is None:
        _list_history(limit)


def _list_history(limit: int) -> None:
    runs = list_runs(limit=limit)
    if not runs:
        console.print(
            "[yellow]No history found.[/yellow] "
            "Run `lgb run --save` or `lgb compare --save` first."
        )
        return

    table = Table(
        title="Benchmark History",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", style="dim", justify="right", width=4)
    table.add_column("Run ID", style="bold", no_wrap=True)
    table.add_column("Timestamp", style="dim")
    table.add_column("Providers", justify="right")
    table.add_column("Mode", style="blue")

    for idx, run in enumerate(runs, 1):
        mode = str(run.meta.get("mode", "-"))
        table.add_row(str(idx), run.run_id, run.ts, str(len(run.results)), mode)

    console.print(table)


def _compare_history(left_id: str, right_id: str) -> None:
    try:
        left_run, right_run = compare_runs(left_id, right_id)
    except KeyError as exc:
        raise click.ClickException(str(exc)) from exc

    left_index = _history_index(left_run.results)
    right_index = _history_index(right_run.results)
    common_keys = sorted(set(left_index) & set(right_index))

    if not common_keys:
        console.print("[yellow]No overlapping provider/model pairs between the two runs.[/yellow]")
        return

    for provider, model in common_keys:
        result_table = compare_table(
            left_index[(provider, model)],
            right_index[(provider, model)],
            left_name=left_run.run_id,
            right_name=right_run.run_id,
        )
        result_table.title = f"{provider} / {model}: {left_run.run_id} vs {right_run.run_id}"
        console.print(result_table)


@cli.command()
@click.argument("config_file", default="bench.yaml", required=False)
@click.option(
    "--timeout",
    "-t",
    default=10.0,
    show_default=True,
    type=float,
    help="Timeout in seconds for each warmup request.",
)
def warmup(config_file: str, timeout: float) -> None:
    """Send one warmup request to each provider in a YAML config."""

    cfg = load_config(config_file)
    ok = asyncio.run(WarmupChecker(cfg, timeout=timeout).run_warmup())
    if not ok:
        raise SystemExit(1)


@cli.command(name="version")
def version_cmd() -> None:
    """Show version, Python, and platform information."""

    console.print(f"[bold cyan]lgb[/bold cyan] version [bold]{__version__}[/bold]")
    console.print(f"Python      {sys.version}")
    console.print(f"Platform    {platform.platform()}")
    console.print(f"Machine     {platform.machine()}")


def main() -> None:
    try:
        cli.main(standalone_mode=False)
    except (ConfigError, LlmGatewayBenchError) as exc:
        err = click.ClickException(str(exc))
        err.show()
        raise SystemExit(err.exit_code) from exc
    except click.ClickException as exc:
        exc.show()
        raise SystemExit(exc.exit_code) from exc
    except click.Abort as exc:
        raise SystemExit(1) from exc


def app() -> None:
    main()


if __name__ == "__main__":  # pragma: no cover
    main()
