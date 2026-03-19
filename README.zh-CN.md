# llm-gateway-bench 🚀

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

> 用于 LLM API 网关的 CLI 基准测试工具 —— 测量延迟、首 token 延迟（TTFT）与吞吐量。

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

**文档**：`docs/` → `docs/configuration.md` • `docs/providers.md`

**源码**：https://github.com/mnbplus/llm-gateway-bench

---

## 为什么需要它？

选择 LLM API 提供商并不容易。价格页面并不会告诉你真实的延迟、首 token 时间或高并发下的性能衰减。`llm-gateway-bench` 提供 **客观、可复现** 的基准数据，帮助你做出更可靠的决策。

## 功能亮点

- ⚡ **TTFT**（Time To First Token）测量
- 📊 **吞吐量**（tokens/sec）基准
- 🔄 **并发请求** 模拟
- 🌐 **多 Provider** 支持：OpenAI、Anthropic、Google Gemini、DeepSeek、Qwen、SiliconFlow，以及任意 OpenAI 兼容网关
- 📈 **报告生成**（Markdown / JSON / CSV）
- 🔧 **YAML 配置** 自定义请求
- 🏃 **CLI 优先**，无需 GUI

## 快速开始

```bash
pip install llm-gateway-bench

# 快速跑一次
lgb run --provider openai --model gpt-5-mini --requests 20

# 多 Provider 对比
lgb compare bench.yaml --output report.md
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

## 使用示例

### 单 Provider 基准

```bash
lgb run \
  --provider openai \
  --model gpt-5.4 \
  --requests 50 \
  --concurrency 5 \
  --prompt "用一句话解释量子计算。"
```

### 多 Provider 对比

```yaml
# bench.yaml
prompts:
  - "写一首关于海洋的俳句。"
  - "2+2 等于几？只回复数字。"

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

### 输出示例

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

## 支持的 Provider

| Provider | 状态 | 备注 |
|----------|------|------|
| OpenAI | ✅ | gpt-5.4, gpt-5-mini, o3, o4-mini |
| Anthropic | ✅ | claude-opus-4, claude-sonnet-4-5, claude-haiku-4 |
| Google Gemini | ✅ | gemini-2.5-pro, gemini-2.5-flash |
| DeepSeek | ✅ | deepseek-v3, deepseek-r2 |
| Qwen (Alibaba) | ✅ | qwen3-max, qwen3-plus |
| SiliconFlow | ✅ | deepseek-v3, deepseek-r2 |
| Any OpenAI-compat | ✅ | 自定义 base_url 支持 |

## 配置

可通过环境变量或 `.env` 提供密钥：

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export DEEPSEEK_API_KEY=sk-...
```

## 贡献

欢迎 PR！请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT — 见 [LICENSE](LICENSE)

---

## 项目链接

- 文档：`docs/`（从 `docs/configuration.md` 开始）
- Provider 说明：`docs/providers.md`
- 更新日志：`CHANGELOG.md`
