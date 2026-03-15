# llm-gateway-bench 🚀

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

> LLM API 网关基准测试 CLI 工具 — 测量多个服务商的延迟、首 token 时间和吞吐量。

[![CI](https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/mnbplus/llm-gateway-bench/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/pypi/v/llm-gateway-bench)](https://pypi.org/project/llm-gateway-bench/)

## 为什么需要它？

选择 LLM API 服务商很难。定价页面无法告诉你真实世界的延迟、首 token 延迟，或者高负载下性能如何下降。`llm-gateway-bench` 给你**客观、可复现的基准测试数据**，帮助你做出明智的决策。

## 功能特性

- ⚡ **TTFT**（Time To First Token，首 token 时间）测量
- 📊 **吞吐量**（tokens/秒）基准测试
- 🔄 **并发请求**模拟
- 🌐 **多服务商**支持：OpenAI、Anthropic、Google Gemini、DeepSeek、通义千问、硅基流动等
- 📈 **报告生成**：Markdown、JSON、CSV 格式
- 🔧 通过 YAML 配置**自定义负载**
- 🏃 **CLI 优先**设计，无需 GUI

## 快速开始

```bash
pip install llm-gateway-bench

# 运行快速基准测试
lgb run --provider openai --model gpt-5-mini --requests 20

# 比较多个服务商
lgb compare bench.yaml

# 查看支持的服务商列表
lgb providers
```

## 安装

```bash
# 从 PyPI 安装
pip install llm-gateway-bench

# 从源码安装
git clone https://github.com/mnbplus/llm-gateway-bench
cd llm-gateway-bench
pip install -e .
```

## 使用方法

### 单服务商基准测试

```bash
lgb run \
  --provider dashscope \
  --model qwen3-max \
  --requests 50 \
  --concurrency 5 \
  --prompt "用一句话解释量子计算。"
```

### 多服务商对比

```yaml
# bench.yaml
prompts:
  - "用一句话解释量子计算。"
  - "2+2等于几？只回复数字。"

providers:
  - name: openai
    model: gpt-5-mini
    api_key: ${OPENAI_API_KEY}

  - name: deepseek
    model: deepseek-v3
    base_url: https://api.deepseek.com/v1
    api_key: ${DEEPSEEK_API_KEY}

  - name: dashscope
    model: qwen3-max
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key: ${DASHSCOPE_API_KEY}

  - name: siliconflow
    model: Pro/deepseek-ai/DeepSeek-V3
    base_url: https://api.siliconflow.cn/v1
    api_key: ${SILICONFLOW_API_KEY}

settings:
  requests: 30
  concurrency: 3
  timeout: 30
```

```bash
lgb compare bench.yaml --output report.md
```

## 支持的服务商

| 服务商 | 状态 | 最新模型 | 说明 |
|--------|------|----------|------|
| OpenAI | ✅ | gpt-5.4, gpt-5-mini, o3, o4-mini | 需要 `OPENAI_API_KEY` |
| Anthropic | ✅ | claude-opus-4, claude-sonnet-4-5, claude-haiku-4 | 需要 `ANTHROPIC_API_KEY` |
| Google Gemini | ✅ | gemini-2.5-pro, gemini-2.5-flash | 需要 `GEMINI_API_KEY` |
| DeepSeek | ✅ | deepseek-v3, deepseek-r2 | OpenAI 兼容 API |
| 通义千问 | ✅ | qwen3-max, qwen3-plus, qwen3-turbo | 通过 DashScope |
| 硅基流动 | ✅ | DeepSeek-V3、Qwen3 等 | 需要 `SILICONFLOW_API_KEY` |
| 任意 OpenAI 兼容 | ✅ | 任意模型 | 使用 `--base-url` |

## 配置

通过环境变量或 `.env` 文件设置 API Key：

```bash
export OPENAI_API_KEY=sk-...
export DASHSCOPE_API_KEY=sk-...
export DEEPSEEK_API_KEY=sk-...
export SILICONFLOW_API_KEY=sk-...
```

## 贡献

欢迎 PR！详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT — 详见 [LICENSE](LICENSE)

---

**链接：** [文档](docs/) · [更新日志](CHANGELOG.md) · [Issues](https://github.com/mnbplus/llm-gateway-bench/issues)
