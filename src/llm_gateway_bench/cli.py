"""CLI entry point for llm-gateway-bench."""

from __future__ import annotations

from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .bench import compare_providers, run_benchmark
from .config import load_config
from .formatters import (
    compare_table,
    render_results,
    request_progress,
    results_table,
)
from .history import append_run, compare_runs, list_runs
from .report import generate_report

app = typer.Typer(
    name="lgb",
    help="LLM Gateway Bench — benchmark LLM API providers for latency, TTFT, and throughput.",
    add_completion=False,
)

console = Console()


@app.command()
def run(
    provider: str = typer.Option(..., "--provider", "-p", help="Provider name (openai, anthropic, deepseek, etc.)"),
    model: str = typer.Option(..., "--model", "-m", help="Model ID to benchmark"),
    requests: int = typer.Option(20, "--requests", "-n", help="Number of requests to send"),
    concurrency: int = typer.Option(3, "--concurrency", "-c", help="Concurrent requests"),
    prompt: str = typer.Option("Say hello in one sentence.", "--prompt", help="Prompt to use"),
    base_url: Optional[str] = typer.Option(None, "--base-url", help="Custom base URL for OpenAI-compatible APIs"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for results (md/json/csv)"),
    timeout: int = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    save_history: bool = typer.Option(True, "--history/--no-history", help="Save results to history"),
):
    """Run a benchmark against a single provider."""
    console.print(f"[bold cyan]🚀 Benchmarking {provider}/{model}[/bold cyan]")
    console.print(f" Requests: {requests} | Concurrency: {concurrency}")

    # Run with progress bar
    with request_progress(f"{provider}/{model}", requests) as handle:
        results = run_benchmark(
            provider=provider,
            model=model,
            prompt=prompt,
            n_requests=requests,
            concurrency=concurrency,
            base_url=base_url,
            timeout=timeout,
            on_progress=lambda: handle.advance(1),
        )

    # Display results with histogram
    render_results(console, [results])

    if output:
        generate_report([results], output)
        console.print(f"[green]✓ Report saved to {output}[/green]")

    if save_history:
        run_id = append_run([results], meta={"command": "run", "provider": provider, "model": model})
        console.print(f"[dim]Run saved with id: {run_id}[/dim]")


@app.command()
def compare(
    config: str = typer.Argument(..., help="Path to bench.yaml config file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for report"),
    save_history: bool = typer.Option(True, "--history/--no-history", help="Save results to history"),
):
    """Compare multiple providers using a YAML config file."""
    console.print(f"[bold cyan]🔍 Loading config: {config}[/bold cyan]")
    cfg = load_config(config)

    providers = cfg.get("providers", [])
    settings = cfg.get("settings", {})
    total_requests = len(providers) * settings.get("requests", 20)

    results = []

    # Overall progress across all providers
    with request_progress("Comparing providers", total_requests) as handle:
        results = compare_providers(
            cfg,
            on_progress=lambda: handle.advance(1),
        )

    # Display results with highlighting
    render_results(console, results)

    if output:
        generate_report(results, output)
        console.print(f"[green]✓ Report saved to {output}[/green]")

    if save_history:
        run_id = append_run(results, meta={"command": "compare", "config": config})
        console.print(f"[dim]Run saved with id: {run_id}[/dim]")


@app.command()
def history(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of runs to show"),
    compare_ids: Optional[List[str]] = typer.Option(
        None, "--compare", "-c", help="Compare two run IDs (pass two values)"
    ),
):
    """View benchmark history or compare two runs."""
    if compare_ids:
        if len(compare_ids) != 2:
            console.print("[red]Error: --compare requires exactly two run IDs[/red]")
            raise typer.Exit(1)
        left_run, right_run = compare_runs(compare_ids[0], compare_ids[1])
        console.print(
            compare_table(
                left_run.results[0] if left_run.results else None,
                right_run.results[0] if right_run.results else None,
                left_name=left_run.run_id,
                right_name=right_run.run_id,
            )
        )
        return

    runs = list_runs(limit=limit)
    if not runs:
        console.print("[dim]No history found. Run a benchmark first.[/dim]")
        return

    table = Table(title="Benchmark History")
    table.add_column("Run ID", style="cyan")
    table.add_column("Timestamp", style="dim")
    table.add_column("Providers", justify="right")
    table.add_column("Best TTFT", justify="right")
    table.add_column("Best TPS", justify="right")

    for run in runs:
        best_ttft = min((r.ttft_ms for r in run.results), default=0)
        best_tps = max((r.tokens_per_sec for r in run.results), default=0)
        table.add_row(
            run.run_id,
            run.ts,
            str(len(run.results)),
            f"{best_ttft:.0f} ms",
            f"{best_tps:.1f}",
        )

    console.print(table)


@app.command()
def version():
    """Show version information."""
    try:
        from importlib.metadata import version as get_version

        v = get_version("llm-gateway-bench")
    except Exception:
        from . import __version__

        v = __version__
    console.print(f"[bold cyan]llm-gateway-bench[/bold cyan] version {v}")


@app.command()
def providers():
    """List supported providers."""
    table = Table(title="Supported Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Models (examples)", style="white")
    table.add_column("Notes", style="dim")
    table.add_row("openai", "gpt-5.4, gpt-5-mini, o3, o4-mini, gpt-4.1, gpt-4.1-mini", "Requires OPENAI_API_KEY")
    table.add_row("anthropic", "claude-opus-4, claude-sonnet-4-5, claude-haiku-4", "Requires ANTHROPIC_API_KEY")
    table.add_row("gemini", "gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash", "Requires GEMINI_API_KEY")
    table.add_row("deepseek", "deepseek-v3, deepseek-r2, deepseek-v3-0324", "Requires DEEPSEEK_API_KEY")
    table.add_row("siliconflow", "Pro/deepseek-ai/DeepSeek-V3, Qwen/Qwen3-235B-A22B", "Requires SILICONFLOW_API_KEY")
    table.add_row("dashscope", "qwen3-max, qwen3-plus, qwen3-turbo, qwen3-235b-a22b", "Requires DASHSCOPE_API_KEY")
    table.add_row("groq", "llama-3.3-70b-versatile, llama-3.1-8b-instant, gemma2-9b-it", "Requires GROQ_API_KEY")
    table.add_row("mistral", "mistral-large-latest, mistral-small-latest, codestral-latest", "Requires MISTRAL_API_KEY")
    table.add_row("openrouter", "100+ models: meta-llama/*, google/*, mistralai/*", "Requires OPENROUTER_API_KEY")
    table.add_row("ollama", "llama3.2, qwen2.5, mistral, phi4, gemma3", "base_url=http://localhost:11434/v1, api_key=ollama")
    table.add_row("vllm", "Any HuggingFace model", "base_url=http://your-server:8000/v1")
    table.add_row("custom", "any model", "Use --base-url for any OpenAI-compat API")
    console.print(table)


def _display_results(results: list):
    """Display benchmark results as a rich table (legacy, kept for compatibility)."""
    console.print(results_table(results))


if __name__ == "__main__":
    app()
