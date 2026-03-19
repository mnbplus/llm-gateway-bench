# llm-gateway-bench

> どの LLM プロバイダー、ゲートウェイ、デプロイ構成を採用するか決める前に、実トラフィックで性能を測るためのツールです。

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

## 何のためのツールか

価格表やモデル紹介ページでは、実運用前に知りたいことは分かりません。

- 同じ prompt 形状で最も TTFT が良いプロバイダーはどれか
- 並列度を上げたときにスループットや tail latency がどう変わるか
- 自前ゲートウェイは upstream API より速いのか遅いのか
- モデル切替、リージョン変更、リリース後に性能が劣化していないか

`llm-gateway-bench` は、こうした問いに答えるための再現可能な CLI ベンチマークを提供します。

## できること

| 測定 | 比較 | 出力 |
| --- | --- | --- |
| TTFT、総レイテンシ、p50/p95、スループット、成功率 | プロバイダー、ゲートウェイ、リージョン、リリース、自前ホスト | Markdown、JSON、CSV、ローカル履歴 |

| 用途 | 対象例 |
| --- | --- |
| プロバイダー選定 | OpenAI、Anthropic、Gemini、Groq、DeepSeek、OpenRouter |
| ゲートウェイ検証 | OpenAI-compatible relay / API gateway |
| インフラ回帰検出 | リージョン変更、LB、モデル更新、自前推論基盤 |

## 最短ルート

```bash
pip install llm-gateway-bench

# 内蔵プロバイダー定義を確認
lgb providers

# 単一 provider / model をすばやく計測
lgb run --provider openai --model gpt-5-mini --requests 20 --concurrency 3 \
  --prompt "Say hello in one sentence."

# YAML で複数 provider を比較
lgb compare example-bench.yaml --output report.md
```

## コマンド構成

| コマンド | 目的 |
| --- | --- |
| `lgb run` | CLI 引数で単一 provider / model を計測 |
| `lgb compare` | `bench.yaml` から複数 target を比較 |
| `lgb warmup` | 本番計測前の疎通確認 |
| `lgb history` | 保存済みランの一覧と比較 |
| `lgb providers` | デフォルトの base URL と環境変数名を表示 |

## 設定例

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

## よくあるワークフロー

1. まず `lgb providers` で既定値と環境変数名を確認する
2. 疎通だけ見たいなら `lgb warmup bench.yaml` を実行する
3. 単一 target の調整には `lgb run` を使う
4. 再現可能な横比較には `lgb compare` を使う
5. 回帰を見るなら `lgb history --compare <id1> <id2>` を使う

## ベンチマーク可能な対象

- 主要 API: OpenAI、Anthropic、Google Gemini
- コスト/性能系: DeepSeek、Groq、Together、Fireworks、OpenRouter、Mistral、Cohere、Perplexity
- 中国系・地域系: DashScope、SiliconFlow、Zhipu、Moonshot、Baidu、01AI、MiniMax
- ローカル/自前ホスト: Ollama、vLLM、LM Studio
- 任意の OpenAI-compatible endpoint: `--base-url` または YAML `base_url`

詳細は [docs/providers.md](docs/providers.md) を参照してください。

## 出力例

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

## スコープ

- 現在は OpenAI-compatible `chat.completions.create(stream=True)` に絞っています
- provider 固有 API の専用ベンチマークは対象外です
- 互換を謳う endpoint でも挙動差がある場合は、まず `warmup` で確認してください

<p align="center">
  <img src="docs/images/architecture.png" alt="llm-gateway-bench architecture" width="640" />
</p>

## 次に読むもの

- [Quickstart](docs/quickstart.md)
- [Configuration](docs/configuration.md)
- [Providers](docs/providers.md)
- [Advanced usage](docs/advanced.md)

## コントリビュート

PR は歓迎です。[CONTRIBUTING.md](CONTRIBUTING.md) と [docs/contributing.md](docs/contributing.md) を参照してください。

## ライセンス

MIT。詳細は [LICENSE](LICENSE) を参照してください。
