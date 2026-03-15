# llm-gateway-bench

*A CLI benchmarking tool for LLM API gateways — measure latency, TTFT, and throughput across providers.*

`llm-gateway-bench` (CLI: `lgb`) helps you answer practical questions:

- Which provider/model has the best **TTFT** (Time To First Token) for my prompts?
- How does performance degrade under **concurrency**?
- Can I **reproduce** latency changes across time/regions/releases?

---

## Quick navigation

- **Install**: [Installation](installation.md)
- **5-minute tutorial**: [Quickstart](quickstart.md)
- **Configure YAML benchmarks**: [Configuration](configuration.md)
- **Provider setup & API keys**: [Providers](providers.md)
- **Power user workflows**: [Advanced usage](advanced.md)
- **Troubleshooting**: [FAQ](faq.md)
- **Contribute**: [Contributing](contributing.md)

---

## Why this tool

Pricing pages rarely tell you:

- **Real-world latency** (average + tail)
- **TTFT** (the “first token feels slow” problem)
- **Throughput** (tokens/sec)
- Behavior under **burst & concurrency**

This project runs repeatable, streaming-based benchmarks against **OpenAI-compatible chat completion endpoints**.

---

## Features

- Streaming benchmark runner (OpenAI SDK) for OpenAI-compatible endpoints
- Metrics: **TTFT**, **total latency**, **p50/p95**, **tokens/sec**, **success rate**
- Run a single provider (`lgb run`) or compare many (`lgb compare bench.yaml`)
- YAML-driven runs with environment-variable secrets (`${OPENAI_API_KEY}`)
- Report generation to Markdown/JSON/CSV

---

## Installation

```bash
pip install llm-gateway-bench
```

More options (pipx/uv/conda/source): see [Installation](installation.md).

---

## Fast start

### 1) Set an API key

```bash
# macOS/Linux
export OPENAI_API_KEY="..."

# Windows PowerShell
$Env:OPENAI_API_KEY = "..."
```

### 2) Run a quick benchmark

```bash
lgb run --provider openai --model gpt-4.1-mini --requests 20 --concurrency 3 \
  --prompt "Say hello in one sentence."
```

### 3) Compare multiple providers with a YAML config

```bash
lgb compare example-bench.yaml --output report.md
```

---

## Common use cases

### Provider evaluation

Benchmark 3–5 providers on the *same prompt* with the same concurrency to get a comparable baseline.

### Gateway regression testing

Run the same YAML config daily (or on every gateway release) and detect:

- TTFT regressions
- tail latency spikes (p95)
- throughput drops

### Region / network experiments

Run the same config from multiple environments (e.g. CI + local + cloud VM) to measure network impact.

### Self-hosted endpoints

Use `--base-url` (or YAML `base_url`) to benchmark OpenAI-compatible gateways (vLLM, LM Studio, custom gateways).

---

## Project scope

- This project currently targets **OpenAI-compatible streaming** via `chat.completions.create(stream=True)`.
- If your provider does not support OpenAI-compatible streaming, you may need a provider-native implementation.

---

## Next steps

- Read the 5-minute tutorial: [Quickstart](quickstart.md)
- Configure your benchmark suite: [Configuration](configuration.md)
- Set up each provider: [Providers](providers.md)
