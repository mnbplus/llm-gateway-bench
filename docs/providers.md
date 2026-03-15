# Providers

`llm-gateway-bench` targets **OpenAI-compatible chat completion streaming** endpoints using the OpenAI Python SDK.

This page documents:

- which providers are supported out of the box
- the default `base_url`
- which environment variable to set for API keys
- provider-specific gotchas

---

## How provider selection works

When you run:

```bash
lgb run --provider openai --model gpt-4.1-mini
```

The runner looks up defaults in `src/llm_gateway_bench/bench.py`:

- `base_url`: if you didn't pass `--base-url`
- `env_key`: which environment variable to read

You can always override the endpoint:

```bash
lgb run --provider custom --model my-model --base-url https://my-gateway.example/v1
```

---

## Built-in provider defaults

| Provider name | Default base URL | API key env var |
| --- | --- | --- |
| `openai` | `https://api.openai.com/v1` | `OPENAI_API_KEY` |
| `anthropic` | `https://api.anthropic.com/v1` *(OpenAI-compat assumed)* | `ANTHROPIC_API_KEY` |
| `gemini` | `https://generativelanguage.googleapis.com/v1beta/openai/` | `GEMINI_API_KEY` |
| `deepseek` | `https://api.deepseek.com/v1` | `DEEPSEEK_API_KEY` |
| `dashscope` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `DASHSCOPE_API_KEY` |
| `siliconflow` | `https://api.siliconflow.cn/v1` | `SILICONFLOW_API_KEY` |
| `zhipu` | `https://open.bigmodel.cn/api/paas/v4` | `ZHIPU_API_KEY` |
| `moonshot` | `https://api.moonshot.cn/v1` | `MOONSHOT_API_KEY` |
| `baidu` | `https://qianfan.baidubce.com/v2` | `BAIDU_API_KEY` |
| `01ai` | `https://api.lingyiwanwu.com/v1` | `YI_API_KEY` |
| `minimax` | `https://api.minimax.chat/v1` | `MINIMAX_API_KEY` |
| `groq` | `https://api.groq.com/openai/v1` | `GROQ_API_KEY` |
| `together` | `https://api.together.xyz/v1` | `TOGETHER_API_KEY` |
| `fireworks` | `https://api.fireworks.ai/inference/v1` | `FIREWORKS_API_KEY` |
| `openrouter` | `https://openrouter.ai/api/v1` | `OPENROUTER_API_KEY` |
| `mistral` | `https://api.mistral.ai/v1` | `MISTRAL_API_KEY` |
| `cohere` | `https://api.cohere.com/compatibility/v1` | `COHERE_API_KEY` |
| `perplexity` | `https://api.perplexity.ai` | `PERPLEXITY_API_KEY` |
| `ollama` | `http://localhost:11434/v1` | *(none)* |
| `vllm` | `http://localhost:8000/v1` | *(none)* |
| `lmstudio` | `http://localhost:1234/v1` | *(none)* |

> Tip: Run `lgb providers` to see a curated list and model examples.

---

## Getting API keys (quick links)

This project does not manage keys. You obtain keys from each provider.

- OpenAI: <https://platform.openai.com/api-keys>
- Anthropic: <https://console.anthropic.com/settings/keys>
- Google Gemini: <https://aistudio.google.com/app/apikey>
- DeepSeek: <https://platform.deepseek.com/>
- Alibaba DashScope (Qwen): <https://dashscope.console.aliyun.com/>
- SiliconFlow: <https://siliconflow.cn/>
- Groq: <https://console.groq.com/keys>
- Mistral: <https://console.mistral.ai/api-keys/>
- OpenRouter: <https://openrouter.ai/keys>

For other providers, follow their official console/docs.

---

## Usage patterns

### 1) Use defaults

```bash
export OPENAI_API_KEY="..."
lgb run --provider openai --model gpt-4.1-mini
```

### 2) Override base URL (OpenAI-compatible gateways)

```bash
export MY_GATEWAY_API_KEY="..."
lgb run --provider custom --model my-model --base-url https://my-gateway.example/v1
```

### 3) YAML config

```yaml
providers:
  - name: openai
    model: gpt-4.1-mini
    api_key: ${OPENAI_API_KEY}

  - name: vllm
    model: meta-llama/Llama-3.1-8B-Instruct
    base_url: http://10.0.0.12:8000/v1
```

---

## Provider notes & gotchas

### OpenAI-compatible streaming

The runner uses:

- `chat.completions.create(stream=True)`
- `stream_options={"include_usage": True}`

If a provider claims compatibility but fails:

- try removing/ignoring `stream_options` (would require a code change)
- verify the provider supports streaming for the chosen model
- verify the correct base URL and path includes `/v1`

### Anthropic

The default `base_url` for `anthropic` is set, but note that Anthropic's official API is not fully OpenAI-compatible. If your request fails, you may need:

- an OpenAI-compat gateway for Anthropic, or
- a future native Anthropic implementation

### Local providers (Ollama / LM Studio / vLLM)

- Ensure the server is running and exposing an OpenAI-compatible endpoint.
- Some servers accept any API key; the OpenAI SDK still expects a string, but it can be a dummy.

---

## Troubleshooting

- 401/403: check you set the right env var for the provider.
- Connection errors: verify `base_url` and network reachability.
- Immediate failures on stream: provider may not support OpenAI streaming.

See also: [FAQ](faq.md)
