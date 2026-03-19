"""Core benchmarking logic for llm-gateway-bench."""

from __future__ import annotations

import asyncio
import os
import statistics
import time
from typing import Any, Callable, List, Optional, Sequence, TypedDict

from dotenv import load_dotenv
from openai import AsyncOpenAI

from .models import BenchConfig, BenchResult, ProviderConfig
from .providers import PROVIDER_DEFAULTS
from .validators import validate_api_key, validate_base_url, validate_provider_name

load_dotenv()


class _RequestResult(TypedDict):
    ttft: float
    total: float
    tokens: int
    error: Optional[str]


def _provider_api_key(provider: str, explicit_api_key: Optional[str]) -> str:
    """Resolve the effective API key for a provider."""

    provider = validate_provider_name(provider)
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    env_key = defaults.get("env_key", "")
    fallback = os.getenv(env_key, None) if env_key else None
    return validate_api_key(provider, explicit_api_key or fallback, env_fallback=True)


def _provider_base_url(provider: str, base_url: Optional[str]) -> Optional[str]:
    """Resolve the effective base URL for a provider."""

    provider = validate_provider_name(provider)
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    return validate_base_url(base_url or defaults.get("base_url"))


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

    async def _collect_stream() -> None:
        nonlocal ttft_ms, total_tokens
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

    try:
        await asyncio.wait_for(_collect_stream(), timeout=timeout)
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
    on_progress: Optional[Callable[[], None]] = None,
) -> List[_RequestResult]:
    """Run ``n_requests`` requests with bounded concurrency."""

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
    api_key: Optional[str] = None,
    timeout: int = 30,
    on_progress: Optional[Callable[[], None]] = None,
) -> BenchResult:
    """Run a benchmark for a single provider/model."""

    provider = validate_provider_name(provider)
    effective_base_url = _provider_base_url(provider, base_url)
    effective_api_key = _provider_api_key(provider, api_key)

    client = AsyncOpenAI(base_url=effective_base_url, api_key=effective_api_key)
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


def run_provider_config(
    provider: ProviderConfig,
    *,
    prompt: str,
    requests: int,
    concurrency: int,
    timeout: int,
    on_progress: Optional[Callable[[], None]] = None,
) -> BenchResult:
    """Run a benchmark using a provider entry from BenchConfig."""

    return run_benchmark(
        provider=provider.name,
        model=provider.model,
        prompt=prompt,
        n_requests=requests,
        concurrency=concurrency,
        base_url=provider.base_url,
        api_key=provider.api_key,
        timeout=timeout,
        on_progress=on_progress,
    )


def compare_providers(
    cfg: Any,
    *,
    on_progress: Optional[Callable[[], None]] = None,
) -> List[BenchResult]:
    """Run benchmarks for all providers defined in the config."""

    if isinstance(cfg, BenchConfig):
        prompt = cfg.first_prompt()
        providers: Sequence[ProviderConfig] = cfg.providers
        requests = cfg.settings.requests
        concurrency = cfg.settings.concurrency
        timeout = cfg.settings.timeout
    else:
        prompt = (cfg.get("prompts") or ["Say hello."])[0]
        providers = [ProviderConfig.model_validate(p) for p in cfg.get("providers", [])]
        settings = cfg.get("settings", {})
        requests = settings.get("requests", 20)
        concurrency = settings.get("concurrency", 3)
        timeout = settings.get("timeout", 30)

    results: List[BenchResult] = []
    for provider in providers:
        results.append(
            run_provider_config(
                provider,
                prompt=prompt,
                requests=requests,
                concurrency=concurrency,
                timeout=timeout,
                on_progress=on_progress,
            )
        )
    return results


class BenchmarkRunner:
    """Compatibility wrapper around the current sync benchmarking API."""

    def __init__(self, cfg: Any) -> None:
        self.cfg = cfg

    def run_all(
        self,
        *,
        on_progress: Optional[Callable[[], None]] = None,
    ) -> List[BenchResult]:
        return compare_providers(self.cfg, on_progress=on_progress)
