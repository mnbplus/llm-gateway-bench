"""Warmup checker for llm-gateway-bench.

Sends a single lightweight request to each configured provider to:
- Verify reachability before a full benchmark run
- Warm up connection pools and server-side caches
- Detect misconfigured API keys or endpoints early
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx
from rich import box
from rich.console import Console
from rich.table import Table

console = Console()

_WARMUP_PROMPT = "Reply with one word: ready"
_WARMUP_MAX_TOKENS = 5


class WarmupChecker:
    """Send one warmup request per provider and report reachability."""

    def __init__(self, cfg: Any, *, timeout: float = 10.0) -> None:
        self.cfg = cfg
        self.timeout = timeout

    async def _check_provider(self, provider: Any) -> dict[str, Any]:
        """Send a single chat completion request to *provider*.

        Returns a status dict with keys: name, ok, latency_ms, error.
        """
        start = time.perf_counter()
        error: str | None = None
        ok = False

        try:
            headers = {"Content-Type": "application/json"}
            api_key = getattr(provider, "api_key", None)
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            payload = {
                "model": provider.model,
                "messages": [{"role": "user", "content": _WARMUP_PROMPT}],
                "max_tokens": _WARMUP_MAX_TOKENS,
                "stream": False,
            }

            url = provider.base_url.rstrip("/") + "/chat/completions"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                ok = True

        except httpx.TimeoutException:
            error = f"Timeout after {self.timeout:.0f}s"
        except httpx.HTTPStatusError as exc:
            error = f"HTTP {exc.response.status_code}"
        except Exception as exc:  # noqa: BLE001
            error = str(exc)[:80]

        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "name": provider.name,
            "ok": ok,
            "latency_ms": elapsed_ms,
            "error": error,
        }

    async def run_warmup(self) -> bool:
        """Run warmup checks for all providers concurrently.

        Prints a summary table and returns True if all providers are reachable.
        """
        providers = self.cfg.providers
        if not providers:
            console.print("[yellow]No providers configured — skipping warmup.[/yellow]")
            return True

        console.print(
            f"[bold cyan]Warming up {len(providers)} provider(s)...[/bold cyan]"
        )

        tasks = [self._check_provider(p) for p in providers]
        results = await asyncio.gather(*tasks)

        table = Table(
            title="Warmup Results",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
            border_style="bright_black",
        )
        table.add_column("Provider", style="bold", min_width=12)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Latency", justify="right", width=12)
        table.add_column("Note", style="dim")

        all_ok = True
        for r in results:
            if r["ok"]:
                status = "[bold green]OK[/bold green]"
                latency = f"{r['latency_ms']:.0f} ms"
                note = ""
            else:
                status = "[bold red]FAIL[/bold red]"
                latency = f"{r['latency_ms']:.0f} ms"
                note = r["error"] or "unknown error"
                all_ok = False

            table.add_row(r["name"], status, latency, note)

        console.print(table)

        if all_ok:
            console.print("[green]All providers reachable. Proceeding to benchmark.[/green]")
        else:
            console.print(
                "[red]One or more providers failed the warmup check.[/red] "
                "Review the errors above before running a full benchmark."
            )

        return all_ok
