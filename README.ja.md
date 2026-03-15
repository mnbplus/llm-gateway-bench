# llm-gateway-bench 🚀

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

> LLM APIゲートウェイのCLIベンチマークツール — 複数プロバイダーのレイテンシ、TTFT、スループットを測定。

[![CI](https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/llm-gateway-bench)](https://pypi.org/project/llm-gateway-bench/)

## なぜ必要か？

LLM APIプロバイダーの選択は難しい。価格ページは実際のレイテンシや高負荷時のパフォーマンス低下を教えてくれません。`llm-gateway-bench`は**客観的で再現可能なベンチマークデータ**を提供し、情報に基づいた意思決定をサポートします。

## 機能

- ⚡ **TTFT**（Time To First Token）測定
- 📊 **スループット**（tokens/秒）ベンチマーク
- 🔄 **並列リクエスト**シミュレーション
- 🌐 **マルチプロバイダー**対応：OpenAI、Anthropic、Google Gemini、DeepSeek、Qwen、SiliconFlowなど
- 📈 Markdown、JSON、CSV形式の**レポート生成**
- 🔧 YAMLによる**カスタムペイロード**
- 🏃 **CLIファースト**設計

## クイックスタート

```bash
pip install llm-gateway-bench

# クイックベンチマーク
lgb run --provider openai --model gpt-5-mini --requests 20

# 複数プロバイダーを比較
lgb compare bench.yaml

# 対応プロバイダーを表示
lgb providers
```

## インストール

```bash
# PyPIから
pip install llm-gateway-bench

# ソースから
git clone https://github.com/mnbplus/llm-gateway-bench
cd llm-gateway-bench
pip install -e .
```

## 対応プロバイダー

| プロバイダー | 状態 | 最新モデル | 備考 |
|------------|------|-----------|------|
| OpenAI | ✅ | gpt-5.4, gpt-5-mini, o3, o4-mini | `OPENAI_API_KEY`が必要 |
| Anthropic | ✅ | claude-opus-4, claude-sonnet-4-5, claude-haiku-4 | `ANTHROPIC_API_KEY`が必要 |
| Google Gemini | ✅ | gemini-2.5-pro, gemini-2.5-flash | `GEMINI_API_KEY`が必要 |
| DeepSeek | ✅ | deepseek-v3, deepseek-r2 | OpenAI互換API |
| Qwen (Alibaba) | ✅ | qwen3-max, qwen3-plus | DashScope経由 |
| SiliconFlow | ✅ | DeepSeek-V3、Qwen3など | `SILICONFLOW_API_KEY`が必要 |
| OpenAI互換 | ✅ | 任意のモデル | `--base-url`を使用 |

## ライセンス

MIT — [LICENSE](LICENSE)を参照

---

**リンク：** [ドキュメント](docs/) · [更新履歴](CHANGELOG.md) · [Issues](https://github.com/mnbplus/llm-gateway-bench/issues)
