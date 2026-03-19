# llm-gateway-bench

> Benchmark real LLM API behavior before you commit to a provider, gateway, or deployment.

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

<p align="center">
  <img src="docs/assets/github-hero.svg" alt="llm-gateway-bench hero banner" width="100%" />
</p>

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

<p align="center">
  <a href="https://mnbplus.github.io/llm-gateway-bench/">Docs</a> ·
  <a href="docs/quickstart.md">Quickstart</a> ·
  <a href="docs/providers.md">Providers</a> ·
  <a href="https://pypi.org/project/llm-gateway-bench/">PyPI</a> ·
  <a href="https://github.com/mnbplus/llm-gateway-bench/releases">Releases</a>
</p>

## Why this exists

Pricing pages and model cards do not answer the questions that matter in production:

- Which provider has the best TTFT for my prompt shape?
- What happens when I increase concurrency?
- Is my gateway faster than the upstream provider?
- Did latency regress after a deploy, region change, or model switch?

`llm-gateway-bench` gives you a repeatable CLI workflow for measuring those answers against real endpoints.

## What you get

| Measure | Compare | Export |
| --- | --- | --- |
| TTFT, total latency, p50/p95, throughput, success rate | Providers, gateways, regions, releases, self-hosted endpoints | Markdown, JSON, CSV, plus local run history |

| Use it for | Typical target |
| --- | --- |
| Provider evaluation | OpenAI, Anthropic, Gemini, Groq, DeepSeek, OpenRouter |
| Gateway validation | OpenAI-compatible relay layers and API gateways |
| Infra regression checks | Regional changes, load balancers, model rollouts, self-hosted serving |

## Fast path

```bash
pip install llm-gateway-bench

# See built-in provider defaults
lgb providers

# Benchmark one provider/model quickly
lgb run --provider openai --model gpt-5-mini --requests 20 --concurrency 3 \
  --prompt "Say hello in one sentence."

# Compare multiple providers from YAML
lgb compare example-bench.yaml --output report.md
```

## Command model

| Command | Purpose |
| --- | --- |
| `lgb run` | Run a single provider/model benchmark from CLI flags |
| `lgb compare` | Run a multi-provider suite from `bench.yaml` |
| `lgb warmup` | Verify provider reachability before a full run |
| `lgb history` | List and compare saved historical runs |
| `lgb providers` | Show built-in provider defaults and env var names |

## Example config

```yaml
prompts:
  - "Write a haiku about the ocean."

providers:
  - name: openai
    model: gpt-5-mini
    api_key: ${OPENAI_API_KEY}

  - name: gemini
    model: gemini-2.5-flash
    base_url: https://generativelanguage.googleapis.com/v1beta/openai/
    api_key: ${GEMINI_API_KEY}

  - name: deepseek
    model: deepseek-v3
    base_url: https://api.deepseek.com/v1
    api_key: ${DEEPSEEK_API_KEY}

settings:
  requests: 20
  concurrency: 3
  timeout: 30
```

```bash
lgb compare bench.yaml --output report.md --save
```

## Typical workflow

1. Start with `lgb providers` to confirm defaults and environment variables.
2. Run `lgb warmup bench.yaml` if you want a quick reachability check.
3. Use `lgb run` while tuning a single provider or endpoint.
4. Use `lgb compare` when you want a reproducible cross-provider report.
5. Save runs and compare them later with `lgb history --compare <id1> <id2>`.

## What you can benchmark

- Frontier APIs: OpenAI, Anthropic, Google Gemini
- Cost/performance providers: DeepSeek, Groq, Together, Fireworks, OpenRouter, Mistral, Cohere, Perplexity
- China-focused providers: DashScope, SiliconFlow, Zhipu, Moonshot, Baidu, 01AI, MiniMax
- Local and self-hosted endpoints: Ollama, vLLM, LM Studio
- Any OpenAI-compatible endpoint via `--base-url` or YAML `base_url`

The full provider matrix lives in [docs/providers.md](docs/providers.md).

## Sample output

```text
┌─────────────────┬──────────────────────┬──────────┬────────────┬──────────────┐
│ Provider        │ Model                │ TTFT (ms)│ Total (ms) │ Tokens/sec   │
├─────────────────┼──────────────────────┼──────────┼────────────┼──────────────┤
│ openai          │ gpt-5-mini           │  198     │  1240      │  94.5        │
│ anthropic       │ claude-haiku-4       │  312     │  1680      │  76.2        │
│ gemini          │ gemini-2.5-flash     │  280     │  1520      │  82.1        │
│ deepseek        │ deepseek-v3          │  720     │  2800      │  48.3        │
│ groq            │ llama-3.3-70b        │   95     │   880      │ 210.5        │
└─────────────────┴──────────────────────┴──────────┴────────────┴──────────────┘
```

## Scope

- The runner targets OpenAI-compatible `chat.completions.create(stream=True)` endpoints.
- Native provider-specific benchmarking flows are out of scope for now.
- If a provider claims compatibility but behaves differently, use `base_url` and validate with `warmup` first.

<p align="center">
  <img src="docs/images/architecture.png" alt="llm-gateway-bench architecture" width="640" />
</p>

## Next steps

- Read the [Quickstart](docs/quickstart.md)
- Configure a suite in [Configuration](docs/configuration.md)
- Check provider-specific notes in [Providers](docs/providers.md)
- Review advanced workflows in [Advanced usage](docs/advanced.md)

## Contributing

PRs are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/contributing.md](docs/contributing.md).

## License

MIT. See [LICENSE](LICENSE).
