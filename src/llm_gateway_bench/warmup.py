"""Warmup checker for llm-gateway-bench."""

from __future__ import annotations

import asyncio
import time
from typing import Any, Optional

import httpx
from rich import box
from rich.console import Console
from rich.table import Table

from .providers import PROVIDER_DEFAULTS
from .validators import validate_api_key, validate_base_url, validate_provider_name

console = Console()

_WARMUP_PROMPT = "Reply with one word: ready"
_WARMUP_MAX_TOKENS = 5


class WarmupChecker:
    """Send one warmup request per provider and report reachability."""

    def __init__(self, cfg: Any, *, timeout: float = 10.0) -> None:
        self.cfg = cfg
        self.timeout = timeout

    @staticmethod
    def _value(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    async def _check_provider(self, provider: Any) -> dict[str, Any]:
        """Send a single non-streaming chat request to a provider."""

        start = time.perf_counter()
        error: Optional[str] = None
        ok = False
        provider_name = self._value(provider, "name", "custom")

        try:
            normalized_name = validate_provider_name(provider_name)
            defaults = PROVIDER_DEFAULTS.get(normalized_name, {})
            base_url = validate_base_url(
                self._value(provider, "base_url") or defaults.get("base_url")
            )
            if not base_url:
                raise ValueError("Provider base_url is required for warmup checks")

            api_key = validate_api_key(
                normalized_name,
                self._value(provider, "api_key"),
                env_fallback=True,
            )

            headers = {"Content-Type": "application/json"}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            payload = {
                "model": self._value(provider, "model"),
                "messages": [{"role": "user", "content": _WARMUP_PROMPT}],
                "max_tokens": _WARMUP_MAX_TOKENS,
                "stream": False,
            }
            url = base_url.rstrip("/") + "/chat/completions"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                ok = True
        except httpx.TimeoutException:
            error = f"Timeout after {self.timeout:.0f}s"
        except httpx.HTTPStatusError as exc:
            error = f"HTTP {exc.response.status_code}"
        except Exception as exc:  # pragma: no cover - network errors vary
            error = str(exc)[:80]

        elapsed_ms = (time.perf_counter() - start) * 1000
        return {
            "name": provider_name,
            "ok": ok,
            "latency_ms": elapsed_ms,
            "error": error,
        }

    async def run_warmup(self) -> bool:
        """Run warmup checks for all providers concurrently."""

        providers = self._value(self.cfg, "providers", [])
        if not providers:
            console.print("[yellow]No providers configured; skipping warmup.[/yellow]")
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
        for result in results:
            if result["ok"]:
                status = "[bold green]OK[/bold green]"
                note = ""
            else:
                status = "[bold red]FAIL[/bold red]"
                note = result["error"] or "unknown error"
                all_ok = False

            table.add_row(
                result["name"],
                status,
                f"{result['latency_ms']:.0f} ms",
                note,
            )

        console.print(table)

        if all_ok:
            console.print("[green]All providers reachable. Proceeding to benchmark.[/green]")
        else:
            console.print(
                "[red]One or more providers failed the warmup check.[/red] "
                "Review the errors above before running a full benchmark."
            )

        return all_ok
