# Configuration

`llm-gateway-bench` can be driven by a YAML file (e.g. `bench.yaml`) when using `lgb compare`.

## Example

```yaml
prompts:
  - "Write a haiku about the ocean."

providers:
  - name: openai
    model: gpt-4o-mini
    api_key: ${OPENAI_API_KEY}

  - name: deepseek
    model: deepseek-chat
    base_url: https://api.deepseek.com/v1
    api_key: ${DEEPSEEK_API_KEY}

settings:
  requests: 20
  concurrency: 3
  timeout: 30
```

## Top-level fields

### `prompts`

- Type: `list[str]`
- Default: `["Say hello."]`

The first prompt is used for the benchmark.

### `providers`

- Type: `list[provider]`

Each entry defines a provider/model to benchmark.

Required:
- `name`: provider name (e.g. `openai`, `deepseek`, `siliconflow`)
- `model`: model identifier

Optional:
- `base_url`: custom OpenAI-compatible endpoint
- `api_key`: API key value or an environment reference `${ENV_NAME}`

### `settings`

- Type: `settings`

Fields:
- `requests` (int, default 20): total requests
- `concurrency` (int, default 3): number of concurrent requests
- `timeout` (int, default 30): per-request timeout seconds

## Environment variables

You can reference environment variables for secrets:

```yaml
api_key: ${OPENAI_API_KEY}
```

At runtime, the loader expands the value from `os.environ`.

## Validation

Configuration is validated using Pydantic models. Invalid YAML or invalid types will raise a `ConfigError`.
