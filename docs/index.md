# llm-gateway-bench

*Benchmark real-world latency, TTFT, and throughput for LLM providers and OpenAI-compatible gateways.*

`llm-gateway-bench` is a CLI-first tool for answering practical questions about model and gateway behavior:

- Which provider has the best TTFT for my prompt shape?
- How does throughput change under concurrency?
- Did a deploy, model switch, or region change regress performance?
- Is my relay layer slower than the upstream API?

---

## Quick navigation

- **Install**: [Installation](installation.md)
- **Get running in minutes**: [Quickstart](quickstart.md)
- **Build reproducible YAML suites**: [Configuration](configuration.md)
- **See provider defaults and gotchas**: [Providers](providers.md)
- **Advanced workflows and CI**: [Advanced usage](advanced.md)
- **Questions and troubleshooting**: [FAQ](faq.md)
- **Contribute**: [Contributing](contributing.md)

---

## What it measures

| Area | Metrics |
| --- | --- |
| Latency | TTFT, total latency, p50, p95 |
| Throughput | Completion tokens per second |
| Reliability | Success rate and error count |
| Comparison | Provider, region, gateway, release, self-hosted target |

---

## Typical workflow

1. Check built-in defaults with `lgb providers`.
2. Verify reachability with `lgb warmup bench.yaml`.
3. Tune a single target with `lgb run`.
4. Compare multiple targets with `lgb compare`.
5. Save runs and compare later with `lgb history --compare`.

---

## Fast start

```bash
pip install llm-gateway-bench

lgb providers

lgb run --provider openai --model gpt-5-mini --requests 20 --concurrency 3 \
  --prompt "Say hello in one sentence."

lgb compare example-bench.yaml --output report.md
```

---

## Supported targets

`llm-gateway-bench` ships with defaults for:

- OpenAI, Anthropic, Google Gemini
- DeepSeek, Groq, Together, Fireworks, OpenRouter, Mistral, Cohere, Perplexity
- DashScope, SiliconFlow, Zhipu, Moonshot, Baidu, 01AI, MiniMax
- Ollama, vLLM, LM Studio
- Any OpenAI-compatible endpoint via `base_url`

See the full matrix in [Providers](providers.md).

---

## Project scope

- Targets OpenAI-compatible streaming chat completion APIs
- Optimized for benchmarking, not API proxying or model routing
- Best fit for provider evaluation, gateway validation, and regression tracking

---

## Continue

- Start with [Quickstart](quickstart.md)
- Build a reproducible suite in [Configuration](configuration.md)
- Wire it into CI via [Advanced usage](advanced.md)
