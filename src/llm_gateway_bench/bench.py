"""Core benchmarking logic.

The current implementation targets OpenAI-compatible endpoints via the OpenAI Python SDK.
It sends **streaming** chat completion requests and derives:

- TTFT (time-to-first-token)
- Total latency
- Approximate throughput (completion tokens / wall time)

Note: this module intentionally keeps provider logic minimal. Most providers are
supported via OpenAI-compatible gateways (`base_url`).
"""

from __future__ import annotations

import asyncio
import os
import statistics
import time
from typing import Dict, List, Optional, TypedDict

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .models import BenchResult
from .providers import PROVIDER_DEFAULTS
from .validators import validate_api_key, validate_base_url, validate_provider_name

load_dotenv()


class _RequestResult(TypedDict):
    ttft: float
    total: float
    tokens: int
    error: Optional[str]


async def _single_request_openai(
    client: AsyncOpenAI,
    model: str,
    prompt: str,
    timeout: int,
) -> _RequestResult:
    """Run a single streaming request and measure TTFT + total latency."""
    t_start = time.perf_counter()
    ttft_ms: Optional[float] = None
    total_tokens = 0

    try:
        async with asyncio.timeout(timeout):
            stream = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                stream_options={"include_usage": True},
            )
            async for chunk in stream:
                if ttft_ms is None and chunk.choices and chunk.choices[0].delta.content:
                    ttft_ms = (time.perf_counter() - t_start) * 1000
                if chunk.usage:
                    total_tokens = chunk.usage.completion_tokens or 0

        total_ms = (time.perf_counter() - t_start) * 1000
        return {
            "ttft": ttft_ms or total_ms,
            "total": total_ms,
            "tokens": total_tokens,
            "error": None,
        }
    except Exception as exc:  # pragma: no cover - network errors vary
        return {"ttft": 0.0, "total": 0.0, "tokens": 0, "error": str(exc)}


async def _run_concurrent(
    client: AsyncOpenAI,
    model: str,
    prompt: str,
    n_requests: int,
    concurrency: int,
    timeout: int,
    on_progress: Optional[callable] = None,
) -> List[_RequestResult]:
    """Run ``n_requests`` requests with bounded concurrency.

    If ``on_progress`` is provided, it will be called once per request completion.
    """

    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_request() -> _RequestResult:
        async with semaphore:
            return await _single_request_openai(client, model, prompt, timeout)

    async def wrapped() -> _RequestResult:
        res = await bounded_request()
        if on_progress is not None:
            try:
                on_progress()
            except Exception:
                pass
        return res

    tasks = [wrapped() for _ in range(n_requests)]
    return await asyncio.gather(*tasks)


def run_benchmark(
    provider: str,
    model: str,
    prompt: str,
    n_requests: int = 20,
    concurrency: int = 3,
    base_url: Optional[str] = None,
    timeout: int = 30,
    on_progress: Optional[callable] = None,
) -> BenchResult:
    """Run a benchmark for a single provider/model.

    Args:
        provider: Provider name (e.g. ``openai``).
        model: Model identifier.
        prompt: Prompt text used for the run.
        n_requests: Number of requests to send.
        concurrency: Maximum concurrent requests.
        base_url: Optional base URL for OpenAI-compatible endpoints.
        timeout: Per-request timeout in seconds.
        on_progress: Optional callback invoked once per completed request.

    Returns:
        A :class:`~llm_gateway_bench.models.BenchResult` with summary statistics.
    """

    provider = validate_provider_name(provider)

    defaults = PROVIDER_DEFAULTS.get(provider, {})
    effective_base_url = validate_base_url(
        base_url or defaults.get("base_url", "https://api.openai.com/v1")
    )

    env_key = defaults.get("env_key", "OPENAI_API_KEY")
    # user may rely on env var
    api_key = validate_api_key(provider, os.getenv(env_key, None))

    client = AsyncOpenAI(base_url=effective_base_url, api_key=api_key)

    raw = asyncio.run(
        _run_concurrent(
            client,
            model,
            prompt,
            n_requests,
            concurrency,
            timeout,
            on_progress=on_progress,
        )
    )

    successes = [r for r in raw if r["error"] is None]
    errors = len(raw) - len(successes)

    if not successes:
        return BenchResult(provider=provider, model=model, errors=errors, success_rate=0.0)

    latencies = [r["total"] for r in successes]
    ttfts = [r["ttft"] for r in successes]
    total_tokens = sum(r["tokens"] for r in successes)

    avg_total = statistics.mean(latencies)
    avg_ttft = statistics.mean(ttfts)
    p95 = (
        sorted(latencies)[int(len(latencies) * 0.95) - 1]
        if len(latencies) >= 20
        else max(latencies)
    )
    p50 = statistics.median(latencies)
    tokens_per_sec = (total_tokens / sum(latencies) * 1000) if sum(latencies) > 0 else 0.0

    return BenchResult(
        provider=provider,
        model=model,
        ttft_ms=avg_ttft,
        total_ms=avg_total,
        tokens_per_sec=tokens_per_sec,
        success_rate=len(successes) / len(raw),
        p95_ms=p95,
        p50_ms=p50,
        errors=errors,
        total_tokens=total_tokens,
        raw_latencies=latencies,
    )


def compare_providers(cfg: dict, *, on_progress: Optional[callable] = None) -> List[BenchResult]:
    """Run benchmarks for all providers defined in the config.

    If ``on_progress`` is given, it will be called once per request completion across all providers.
    """

    results: List[BenchResult] = []
    prompts = cfg.get("prompts", ["Say hello."])
    prompt = prompts[0] if prompts else "Say hello."
    settings = cfg.get("settings", {})

    for provider_cfg in cfg.get("providers", []):
        results.append(
            run_benchmark(
                provider=provider_cfg["name"],
                model=provider_cfg["model"],
                prompt=prompt,
                n_requests=settings.get("requests", 20),
                concurrency=settings.get("concurrency", 3),
                base_url=provider_cfg.get("base_url"),
                timeout=settings.get("timeout", 30),
                on_progress=on_progress,
            )
        )

    return results
