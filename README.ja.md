# llm-gateway-bench 🚀

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

> LLM API ゲートウェイ向けの CLI ベンチマークツール — レイテンシ、TTFT（最初のトークンまでの時間）、スループットを測定します。

<p align="center">
  <a href="https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml">
    <img src="https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://pypi.org/project/llm-gateway-bench/">
    <img src="https://img.shields.io/pypi/v/llm-gateway-bench" alt="PyPI">
  </a>
  <a href="https://codecov.io/gh/mnbplus/llm-gateway-bench">
    <img src="https://img.shields.io/codecov/c/github/mnbplus/llm-gateway-bench" alt="Coverage">
  </a>
  <a href="https://pypi.org/project/llm-gateway-bench/">
    <img src="https://img.shields.io/pypi/pyversions/llm-gateway-bench" alt="Python Versions">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  </a>
</p>

---

**ドキュメント**：`docs/` → `docs/configuration.md` • `docs/providers.md`

**ソースコード**：https://github.com/mnbplus/llm-gateway-bench

---

## なぜ必要？

LLM API の提供元を選ぶのは簡単ではありません。価格表だけでは実測レイテンシや TTFT、高負荷時の劣化は見えません。`llm-gateway-bench` は **客観的かつ再現可能なベンチマーク** を提供し、判断材料を増やします。

## 特徴

- ⚡ **TTFT**（Time To First Token）の測定
- 📊 **スループット**（tokens/sec）計測
- 🔄 **同時リクエスト** シミュレーション
- 🌐 **マルチ Provider** 対応：OpenAI、Anthropic、Google Gemini、DeepSeek、Qwen、SiliconFlow、および OpenAI 互換 API
- 📈 **レポート生成**（Markdown / JSON / CSV）
- 🔧 **YAML 設定** によるカスタマイズ
- 🏃 **CLI ファースト** 設計

## クイックスタート

```bash
pip install llm-gateway-bench

# すぐに計測
lgb run --provider openai --model gpt-5-mini --requests 20

# 複数 Provider の比較
lgb compare bench.yaml --output report.md
```

## インストール

```bash
# PyPI から
pip install llm-gateway-bench

# ソースから
git clone https://github.com/mnbplus/llm-gateway-bench
cd llm-gateway-bench
pip install -e .
```

## 使い方

### 単一 Provider のベンチマーク

```bash
lgb run \
  --provider openai \
  --model gpt-5.4 \
  --requests 50 \
  --concurrency 5 \
  --prompt "量子計算を一文で説明してください。"
```

### 複数 Provider の比較

```yaml
# bench.yaml
prompts:
  - "海について俳句を書いてください。"
  - "2+2 は？数字だけで答えてください。"

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

### 出力例

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

## 対応 Provider

| Provider | 状態 | 備考 |
|----------|------|------|
| OpenAI | ✅ | gpt-5.4, gpt-5-mini, o3, o4-mini |
| Anthropic | ✅ | claude-opus-4, claude-sonnet-4-5, claude-haiku-4 |
| Google Gemini | ✅ | gemini-2.5-pro, gemini-2.5-flash |
| DeepSeek | ✅ | deepseek-v3, deepseek-r2 |
| Qwen (Alibaba) | ✅ | qwen3-max, qwen3-plus |
| SiliconFlow | ✅ | deepseek-v3, deepseek-r2 |
| Any OpenAI-compat | ✅ | base_url でカスタム対応 |

## 設定

環境変数または `.env` で API キーを指定できます：

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export DEEPSEEK_API_KEY=sk-...
```

## コントリビュート

PR 大歓迎！ [CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## ライセンス

MIT — [LICENSE](LICENSE)

---

## リンク

- ドキュメント：`docs/`（`docs/configuration.md` から）
- Provider 説明：`docs/providers.md`
- 変更履歴：`CHANGELOG.md`
