# llm-gateway-bench 🚀

> A CLI benchmarking tool for LLM API gateways — measure latency, TTFT, and throughput across providers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![PyPI version](https://badge.fury.io/py/llm-gateway-bench.svg)](https://pypi.org/project/llm-gateway-bench/)

## Why?

Choosing an LLM API provider is hard. Pricing pages don't tell you about real-world latency, first-token delay, or how performance degrades under load. `llm-gateway-bench` gives you **objective, reproducible benchmark data** so you can make informed decisions.

## Features

- ⚡ **TTFT** (Time To First Token) measurement
- 📊 **Throughput** (tokens/sec) benchmarking
- 🔄 **Concurrent requests** simulation
- 🌐 **Multi-provider** support: OpenAI, Anthropic, Google Gemini, DeepSeek, Qwen, SiliconFlow, and any OpenAI-compatible endpoint
- 📈 **Report generation** in Markdown, JSON, and CSV
- 🔧 **Custom payloads** via YAML config
- 🏃 **CLI-first** design, no GUI required

## Quick Start

```bash
pip install llm-gateway-bench

# Run a quick benchmark
lgb run --provider openai --model gpt-4o-mini --requests 20

# Compare multiple providers
lgb compare --config bench.yaml

# Generate a report
lgb report --output results.md
```

## Installation

```bash
# From PyPI
pip install llm-gateway-bench

# From source
git clone https://github.com/YOUR_USERNAME/llm-gateway-bench
cd llm-gateway-bench
pip install -e .
```

## Usage

### Single Provider Benchmark

```bash
lgb run \
  --provider openai \
  --model gpt-4o-mini \
  --requests 50 \
  --concurrency 5 \
  --prompt "Explain quantum computing in one sentence."
```

### Multi-Provider Comparison

```yaml
# bench.yaml
prompts:
  - "Write a haiku about the ocean."
  - "What is 2+2? Reply with just the number."

providers:
  - name: openai
    model: gpt-4o-mini
    api_key: ${OPENAI_API_KEY}

  - name: anthropic
    model: claude-3-haiku-20240307
    api_key: ${ANTHROPIC_API_KEY}

  - name: deepseek
    model: deepseek-chat
    base_url: https://api.deepseek.com/v1
    api_key: ${DEEPSEEK_API_KEY}

  - name: siliconflow
    model: deepseek-ai/DeepSeek-V3
    base_url: https://api.siliconflow.cn/v1
    api_key: ${SILICONFLOW_API_KEY}

settings:
  requests: 30
  concurrency: 3
  timeout: 30
```

```bash
lgb compare --config bench.yaml --output report.md
```

### Sample Output

```
┌─────────────────┬──────────────────────┬──────────┬────────────┬──────────────┐
│ Provider        │ Model                │ TTFT (ms)│ Total (ms) │ Tokens/sec   │
├─────────────────┼──────────────────────┼──────────┼────────────┼──────────────┤
│ openai          │ gpt-4o-mini          │  312     │  1840      │  68.2        │
│ anthropic       │ claude-3-haiku       │  428     │  2100      │  54.1        │
│ deepseek        │ deepseek-chat        │  890     │  3200      │  42.3        │
│ siliconflow     │ DeepSeek-V3          │  654     │  2800      │  48.7        │
└─────────────────┴──────────────────────┴──────────┴────────────┴──────────────┘
```

## Supported Providers

| Provider | Status | Notes |
|----------|--------|-------|
| OpenAI | ✅ | GPT-4o, GPT-4o-mini, o1, etc. |
| Anthropic | ✅ | Claude 3.x series |
| Google Gemini | ✅ | Gemini 1.5 Pro/Flash |
| DeepSeek | ✅ | Via OpenAI-compatible API |
| Qwen (Alibaba) | ✅ | Via DashScope |
| SiliconFlow | ✅ | Multiple open-source models |
| Any OpenAI-compat | ✅ | Custom base_url support |

## Configuration

Set API keys via environment variables or `.env` file:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export DEEPSEEK_API_KEY=sk-...
```

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE)
