"""CLI entry point for llm-gateway-bench."""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table

from .bench import run_benchmark, compare_providers
from .config import load_config
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
):
    """Run a benchmark against a single provider."""
    console.print(f"[bold cyan]🚀 Benchmarking {provider}/{model}[/bold cyan]")
    console.print(f"   Requests: {requests} | Concurrency: {concurrency}")

    results = run_benchmark(
        provider=provider,
        model=model,
        prompt=prompt,
        n_requests=requests,
        concurrency=concurrency,
        base_url=base_url,
        timeout=timeout,
    )

    _display_results([results])

    if output:
        generate_report([results], output)
        console.print(f"[green]✓ Report saved to {output}[/green]")


@app.command()
def compare(
    config: str = typer.Argument(..., help="Path to bench.yaml config file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for report"),
):
    """Compare multiple providers using a YAML config file."""
    console.print(f"[bold cyan]🔍 Loading config: {config}[/bold cyan]")
    cfg = load_config(config)

    results = compare_providers(cfg)
    _display_results(results)

    if output:
        generate_report(results, output)
        console.print(f"[green]✓ Report saved to {output}[/green]")


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
    """Display benchmark results as a rich table."""
    table = Table(title="Benchmark Results")
    table.add_column("Provider", style="cyan")
    table.add_column("Model", style="white")
    table.add_column("TTFT (ms)", justify="right", style="green")
    table.add_column("Total (ms)", justify="right")
    table.add_column("Tokens/sec", justify="right", style="yellow")
    table.add_column("Success", justify="right")
    table.add_column("P95 (ms)", justify="right", style="dim")

    for r in results:
        table.add_row(
            r.provider,
            r.model,
            f"{r.ttft_ms:.0f}",
            f"{r.total_ms:.0f}",
            f"{r.tokens_per_sec:.1f}",
            f"{r.success_rate:.0%}",
            f"{r.p95_ms:.0f}",
        )

    console.print(table)


if __name__ == "__main__":
    app()
