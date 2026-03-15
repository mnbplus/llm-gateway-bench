# Providers

`llm-gateway-bench` targets **OpenAI-compatible chat completion streaming** endpoints.

## Built-in defaults

The benchmark includes defaults for the following providers:

| Provider name | Default base URL | API key env var |
| --- | --- | --- |
| `openai` | `https://api.openai.com/v1` | `OPENAI_API_KEY` |
| `deepseek` | `https://api.deepseek.com/v1` | `DEEPSEEK_API_KEY` |
| `siliconflow` | `https://api.siliconflow.cn/v1` | `SILICONFLOW_API_KEY` |
| `dashscope` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `DASHSCOPE_API_KEY` |
| `gemini` | `https://generativelanguage.googleapis.com/v1beta/openai/` | `GEMINI_API_KEY` |

## Custom / OpenAI-compatible endpoints

Any OpenAI-compatible gateway can be benchmarked using `--base-url`:

```bash
lgb run --provider custom --model my-model --base-url https://my-gateway.example/v1
```

In YAML config:

```yaml
providers:
  - name: custom
    model: my-model
    base_url: https://my-gateway.example/v1
    api_key: ${MY_GATEWAY_API_KEY}
```

## Notes about provider support

- The current implementation uses the OpenAI SDK (`openai.AsyncOpenAI`) and calls `chat.completions.create(stream=True)`.
- Providers that expose OpenAI-compatible streaming APIs should work.
- The project lists Anthropic as a dependency, but the current benchmark runner does not implement the native Anthropic SDK streaming path yet. Contributions welcome.

## Troubleshooting

- If you see authentication errors, confirm the correct environment variable is set.
- If the gateway does not support streaming or `stream_options`, the request may fail. Try a smaller prompt and verify the gateway supports the OpenAI streaming protocol.
