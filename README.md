# llm-gateway-bench 🚀

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

> A CLI benchmarking tool for LLM API gateways — measure latency, TTFT, and throughput across providers.

<p align="center">
  <a href="https://github.com/YOUR_USERNAME/llm-gateway-bench/actions/workflows/ci.yml">
    <img src="https://github.com/YOUR_USERNAME/llm-gateway-bench/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://pypi.org/project/llm-gateway-bench/">
    <img src="https://img.shields.io/pypi/v/llm-gateway-bench" alt="PyPI">
  </a>
  <a href="https://codecov.io/gh/YOUR_USERNAME/llm-gateway-bench">
    <img src="https://img.shields.io/codecov/c/github/YOUR_USERNAME/llm-gateway-bench" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/llm-gateway-bench/">
    <img src="https://img.shields.io/pypi/pyversions/llm-gateway-bench" alt="Python Versions">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  </a>
</p>

---

**Documentation**: `docs/` → `docs/configuration.md` • `docs/providers.md`

**Source Code**: https://github.com/YOUR_USERNAME/llm-gateway-bench

---

<p align="center">
  <img src="docs/images/screenshot.jpg" alt="llm-gateway-bench demo" width="720" />
</p>

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
lgb compare bench.yaml --output report.md
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
  --model gpt-5.4 \
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
    model: claude-sonnet-4-5
    api_key: ${ANTHROPIC_API_KEY}

  - name: gemini
    model: gemini-2.5-pro
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key: ${GEMINI_API_KEY}

  - name: deepseek
    model: deepseek-v3
    base_url: https://api.deepseek.com/v1
    api_key: ${DEEPSEEK_API_KEY}

  - name: siliconflow
    model: deepseek-v3
    base_url: https://api.siliconflow.cn/v1
    api_key: ${SILICONFLOW_API_KEY}

  - name: dashscope
    model: qwen3-plus
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
┌─────────────────┬──────────────────────┬──────────┬────────────┬──────────────┐
│ Provider        │ Model                │ TTFT (ms)│ Total (ms) │ Tokens/sec   │
├─────────────────┼──────────────────────┼──────────┼────────────┼──────────────┤
│ openai          │ gpt-5-mini           │  312     │  1840      │  68.2        │
│ anthropic       │ claude-sonnet-4-5    │  428     │  2100      │  54.1        │
│ deepseek        │ deepseek-v3          │  890     │  3200      │  42.3        │
│ siliconflow     │ deepseek-v3          │  654     │  2800      │  48.7        │
└─────────────────┴──────────────────────┴──────────┴────────────┴──────────────┘
```

## Supported Providers

| Provider | Status | Notes |
|----------|--------|-------|
| OpenAI | ✅ | gpt-5.4, gpt-5-mini, o3, o4-mini |
| Anthropic | ✅ | claude-opus-4, claude-sonnet-4-5, claude-haiku-4 |
| Google Gemini | ✅ | gemini-2.5-pro, gemini-2.5-flash |
| DeepSeek | ✅ | deepseek-v3, deepseek-r2 |
| Qwen (Alibaba) | ✅ | qwen3-max, qwen3-plus |
| SiliconFlow | ✅ | deepseek-v3, deepseek-r2 |
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

---

## Project links

- Documentation: `docs/` (start here: `docs/configuration.md`)
- Providers: `docs/providers.md`
- Changelog: `CHANGELOG.md`
