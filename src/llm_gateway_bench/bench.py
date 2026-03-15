"""Core benchmarking logic."""

import time
import asyncio
import statistics
from dataclasses import dataclass, field
from typing import Optional, List
from openai import AsyncOpenAI
import anthropic
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class BenchResult:
    provider: str
    model: str
    ttft_ms: float = 0.0
    total_ms: float = 0.0
    tokens_per_sec: float = 0.0
    success_rate: float = 0.0
    p95_ms: float = 0.0
    p50_ms: float = 0.0
    errors: int = 0
    total_tokens: int = 0
    raw_latencies: List[float] = field(default_factory=list)


PROVIDER_DEFAULTS = {
    "openai": {"base_url": "https://api.openai.com/v1", "env_key": "OPENAI_API_KEY"},
    "deepseek": {"base_url": "https://api.deepseek.com/v1", "env_key": "DEEPSEEK_API_KEY"},
    "siliconflow": {"base_url": "https://api.siliconflow.cn/v1", "env_key": "SILICONFLOW_API_KEY"},
    "dashscope": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "env_key": "DASHSCOPE_API_KEY"},
    "gemini": {"base_url": "https://generativelanguage.googleapis.com/v1beta/openai/", "env_key": "GEMINI_API_KEY"},
}


async def _single_request_openai(
    client: AsyncOpenAI,
    model: str,
    prompt: str,
    timeout: int,
) -> dict:
    """Run a single streaming request and measure TTFT + total latency."""
    t_start = time.perf_counter()
    ttft = None
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
                if ttft is None and chunk.choices and chunk.choices[0].delta.content:
                    ttft = (time.perf_counter() - t_start) * 1000
                if chunk.usage:
                    total_tokens = chunk.usage.completion_tokens or 0

        total_ms = (time.perf_counter() - t_start) * 1000
        return {"ttft": ttft or total_ms, "total": total_ms, "tokens": total_tokens, "error": None}
    except Exception as e:
        return {"ttft": 0, "total": 0, "tokens": 0, "error": str(e)}


async def _run_concurrent(
    client: AsyncOpenAI,
    model: str,
    prompt: str,
    n_requests: int,
    concurrency: int,
    timeout: int,
) -> List[dict]:
    """Run n_requests with controlled concurrency."""
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_request():
        async with semaphore:
            return await _single_request_openai(client, model, prompt, timeout)

    tasks = [bounded_request() for _ in range(n_requests)]
    return await asyncio.gather(*tasks)


def run_benchmark(
    provider: str,
    model: str,
    prompt: str,
    n_requests: int = 20,
    concurrency: int = 3,
    base_url: Optional[str] = None,
    timeout: int = 30,
) -> BenchResult:
    """Run benchmark for a single provider/model."""
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    effective_base_url = base_url or defaults.get("base_url", "https://api.openai.com/v1")
    env_key = defaults.get("env_key", "OPENAI_API_KEY")
    api_key = os.getenv(env_key, "dummy")

    client = AsyncOpenAI(base_url=effective_base_url, api_key=api_key)

    raw = asyncio.run(_run_concurrent(client, model, prompt, n_requests, concurrency, timeout))

    successes = [r for r in raw if r["error"] is None]
    errors = len(raw) - len(successes)

    if not successes:
        return BenchResult(provider=provider, model=model, errors=errors, success_rate=0.0)

    latencies = [r["total"] for r in successes]
    ttfts = [r["ttft"] for r in successes]
    total_tokens = sum(r["tokens"] for r in successes)
    avg_total = statistics.mean(latencies)
    avg_ttft = statistics.mean(ttfts)
    p95 = sorted(latencies)[int(len(latencies) * 0.95) - 1] if len(latencies) >= 20 else max(latencies)
    p50 = statistics.median(latencies)
    tokens_per_sec = (total_tokens / sum(latencies) * 1000) if sum(latencies) > 0 else 0

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


def compare_providers(cfg: dict) -> List[BenchResult]:
    """Run benchmarks for all providers in config."""
    results = []
    prompts = cfg.get("prompts", ["Say hello."])
    prompt = prompts[0] if prompts else "Say hello."
    settings = cfg.get("settings", {})

    for p in cfg.get("providers", []):
        result = run_benchmark(
            provider=p["name"],
            model=p["model"],
            prompt=prompt,
            n_requests=settings.get("requests", 20),
            concurrency=settings.get("concurrency", 3),
            base_url=p.get("base_url"),
            timeout=settings.get("timeout", 30),
        )
        results.append(result)

    return results
