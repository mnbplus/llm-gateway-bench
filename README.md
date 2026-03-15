# llm-gateway-bench 🚀

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

> A CLI benchmarking tool for LLM API gateways — measure latency, TTFT, and throughput across providers.

[![CI](https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![PyPI version](https://img.shields.io/pypi/v/llm-gateway-bench)](https://pypi.org/project/llm-gateway-bench/)
[![Coverage](https://img.shields.io/codecov/c/github/mnbplus/llm-gateway-bench)](https://codecov.io/gh/mnbplus/llm-gateway-bench)

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
lgb run --provider openai --model gpt-5-mini --requests 20

# Compare multiple providers
lgb compare bench.yaml

# List supported providers
lgb providers
```

## Installation

```bash
# From PyPI
pip install llm-gateway-bench

# From source
git clone https://github.com/mnbplus/llm-gateway-bench
cd llm-gateway-bench
pip install -e .
```

## Usage

### Single Provider Benchmark

```bash
lgb run \
  --provider openai \
  --model gpt-5-mini \
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
    model: gpt-5-mini
    api_key: ${OPENAI_API_KEY}

  - name: anthropic
    model: claude-haiku-4
    api_key: ${ANTHROPIC_API_KEY}

  - name: deepseek
    model: deepseek-v3
    base_url: https://api.deepseek.com/v1
    api_key: ${DEEPSEEK_API_KEY}

  - name: siliconflow
    model: Pro/deepseek-ai/DeepSeek-V3
    base_url: https://api.siliconflow.cn/v1
    api_key: ${SILICONFLOW_API_KEY}

  - name: dashscope
    model: qwen3-max
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key: ${DASHSCOPE_API_KEY}

settings:
  requests: 30
  concurrency: 3
  timeout: 30
```

```bash
lgb compare bench.yaml --output report.md
```

### Sample Output

```
┌─────────────────┬──────────────────┬──────────┬────────────┬──────────────┐
│ Provider        │ Model            │ TTFT (ms)│ Total (ms) │ Tokens/sec   │
├─────────────────┼──────────────────┼──────────┼────────────┼──────────────┤
│ openai          │ gpt-5-mini       │  198     │  1240      │  94.5        │
│ anthropic       │ claude-haiku-4   │  312     │  1680      │  76.2        │
│ deepseek        │ deepseek-v3      │  720     │  2800      │  48.3        │
│ siliconflow     │ DeepSeek-V3      │  580     │  2400      │  55.1        │
│ dashscope       │ qwen3-max        │  440     │  2100      │  62.7        │
└─────────────────┴──────────────────┴──────────┴────────────┴──────────────┘
```

## Supported Providers

| Provider | Status | Latest Models | Notes |
|----------|--------|---------------|-------|
| OpenAI | ✅ | gpt-5.4, gpt-5-mini, o3, o4-mini | Requires `OPENAI_API_KEY` |
| Anthropic | ✅ | claude-opus-4, claude-sonnet-4-5, claude-haiku-4 | Requires `ANTHROPIC_API_KEY` |
| Google Gemini | ✅ | gemini-2.5-pro, gemini-2.5-flash | Requires `GEMINI_API_KEY` |
| DeepSeek | ✅ | deepseek-v3, deepseek-r2 | Via OpenAI-compatible API |
| Qwen (Alibaba) | ✅ | qwen3-max, qwen3-plus, qwen3-turbo | Via DashScope |
| SiliconFlow | ✅ | DeepSeek-V3, Qwen3, and more | Requires `SILICONFLOW_API_KEY` |
| Any OpenAI-compat | ✅ | Any model | Use `--base-url` |

## Configuration

Set API keys via environment variables or `.env` file:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export DEEPSEEK_API_KEY=sk-...
export SILICONFLOW_API_KEY=sk-...
export DASHSCOPE_API_KEY=sk-...
export GEMINI_API_KEY=...
```

## Contributing

PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE)

---

**Links:** [Docs](docs/) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/mnbplus/llm-gateway-bench/issues)
