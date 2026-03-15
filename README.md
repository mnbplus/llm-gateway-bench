# llm-gateway-bench 🚀

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

> A CLI benchmarking tool for LLM API gateways — measure latency, TTFT, and throughput across providers.

<p align="center">
  <a href="https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml">
    <img src="https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/mnbplus/llm-gateway-bench/releases">
    <img src="https://img.shields.io/github/v/release/mnbplus/llm-gateway-bench?include_prereleases" alt="Release">
  </a>
  <a href="https://github.com/mnbplus/llm-gateway-bench/stargazers">
    <img src="https://img.shields.io/github/stars/mnbplus/llm-gateway-bench" alt="Stars">
  </a>
  <a href="https://pypi.org/project/llm-gateway-bench/">
    <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  </a>
</p>

---

**Documentation**: [docs/](docs/) · [Configuration](docs/configuration.md) · [Providers](docs/providers.md) · [FAQ](docs/faq.md)

**Source Code**: <https://github.com/mnbplus/llm-gateway-bench>

---

<p align="center">
  <img src="docs/images/screenshot.jpg" alt="llm-gateway-bench terminal demo" width="720" />
</p>

<p align="center">
  <img src="docs/images/architecture.png" alt="llm-gateway-bench architecture" width="600" />
</p>

## Why?

Choosing an LLM API provider is hard. Pricing pages don't tell you about real-world latency, first-token delay, or how performance degrades under load. `llm-gateway-bench` gives you **objective, reproducible benchmark data** so you can make informed decisions.

## Features

- ⚡ **TTFT** (Time To First Token) measurement
- 📊 **Throughput** (tokens/sec) benchmarking
- 🔄 **Concurrent requests** simulation
- 🌐 **Multi-provider** support: OpenAI, Anthropic, Google Gemini, DeepSeek, Qwen, SiliconFlow, Groq, Mistral, OpenRouter, Ollama, and more
- 📈 **Report generation** in Markdown, JSON, and CSV
- 🔧 **Custom payloads** via YAML config
- 📜 **History** — save and compare past runs
- 🏃 **CLI-first** design, no GUI required

## Quick Start

```bash
pip install llm-gateway-bench

# Run a quick benchmark
lgb run --provider openai --model gpt-5-mini --requests 20

# Compare multiple providers
lgb compare bench.yaml

# List all supported providers
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

  - name: gemini
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key: ${GEMINI_API_KEY}

  - name: deepseek
    model: deepseek-v3
    base_url: https://api.deepseek.com/v1
    api_key: ${DEEPSEEK_API_KEY}

  - name: groq
    model: llama-3.3-70b-versatile
    base_url: https://api.groq.com/openai/v1
    api_key: ${GROQ_API_KEY}

settings:
  requests: 20
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
│ openai          │ gpt-5-mini           │  198     │  1240      │  94.5        │
│ anthropic       │ claude-haiku-4       │  312     │  1680      │  76.2        │
│ gemini          │ gemini-2.5-flash     │  280     │  1520      │  82.1        │
│ deepseek        │ deepseek-v3          │  720     │  2800      │  48.3        │
│ groq            │ llama-3.3-70b        │  95      │  880       │  210.5       │
└─────────────────┴──────────────────────┴──────────┴────────────┴──────────────┘
```

## Supported Providers (20+)

| Provider | Latest Models | Notes |
|----------|---------------|-------|
| OpenAI | gpt-5.4, gpt-5-mini, o3, o4-mini | `OPENAI_API_KEY` |
| Anthropic | claude-opus-4, claude-sonnet-4-5, claude-haiku-4 | `ANTHROPIC_API_KEY` |
| Google Gemini | gemini-2.5-pro, gemini-2.5-flash | `GEMINI_API_KEY` |
| DeepSeek | deepseek-v3, deepseek-r2 | `DEEPSEEK_API_KEY` |
| Qwen (Alibaba) | qwen3-max, qwen3-plus, qwen3-turbo | `DASHSCOPE_API_KEY` |
| SiliconFlow | DeepSeek-V3, Qwen3 series | `SILICONFLOW_API_KEY` |
| Groq | llama-3.3-70b, llama-3.1-8b | `GROQ_API_KEY` |
| Mistral | mistral-large, mistral-small | `MISTRAL_API_KEY` |
| OpenRouter | 100+ models | `OPENROUTER_API_KEY` |
| Ollama | llama3.2, qwen2.5, mistral... | Local, no key needed |
| vLLM / LM Studio | Any HuggingFace model | Local, no key needed |
| **Any OpenAI-compat** | Any model | Use `--base-url` |

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

**Links:** [Docs](docs/) · [Changelog](CHANGELOG.md) · [Issues](https://github.com/mnbplus/llm-gateway-bench/issues) · [Discussions](https://github.com/mnbplus/llm-gateway-bench/discussions)
