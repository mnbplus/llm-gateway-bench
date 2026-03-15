# Configuration

`llm-gateway-bench` can be driven by a YAML file (e.g. `bench.yaml`) when using `lgb compare`.

This page documents the **full schema** and practical tips for reproducible results.

---

## Example config

```yaml
prompts:
  - "Write a haiku about the ocean."

providers:
  - name: openai
    model: gpt-4.1-mini
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

Run it:

```bash
lgb compare bench.yaml --output report.md
```

---

## Schema overview

Top-level mapping:

- `prompts`: list of prompt strings
- `providers`: list of providers/models to benchmark
- `settings`: benchmark parameters (requests, concurrency, timeout)

> Validation is performed using Pydantic models. Unknown top-level fields raise a `ConfigError`.

---

## `prompts`

- Type: `list[str]`
- Default: `['Say hello.']`

Notes:

- Current runner uses the **first prompt only** (`prompts[0]`).
- Keep prompt text stable when comparing runs over time.

---

## `providers`

- Type: `list[provider]`
- Default: `[]`

Each provider entry supports these fields:

### Required

- `name` (str): provider identifier (lowercased internally)
- `model` (str): model id used by the provider

### Optional

- `base_url` (str): OpenAI-compatible API base URL (e.g. `https://.../v1`)
- `api_key` (str): secret, usually referenced as `${ENV_NAME}`

Example:

```yaml
providers:
  - name: openrouter
    model: meta-llama/llama-3.3-70b-instruct
    base_url: https://openrouter.ai/api/v1
    api_key: ${OPENROUTER_API_KEY}
```

### Extra fields

The provider model is configured with `extra="allow"`, so you may include extra fields for future extensions:

```yaml
providers:
  - name: openrouter
    model: meta-llama/llama-3.3-70b-instruct
    api_key: ${OPENROUTER_API_KEY}
    headers:
      HTTP-Referer: https://example.com
      X-Title: llm-gateway-bench
```

The **current runner** ignores these extra keys.

### Important: where the API key is read from

Even though YAML supports `api_key`, the current benchmark runner reads the actual key from **environment variables** based on provider name:

- Provider defaults mapping lives in `src/llm_gateway_bench/bench.py` (`PROVIDER_DEFAULTS`).
- The loader (`src/llm_gateway_bench/config.py`) expands `${ENV_NAME}` values, but the runner does not currently consume `provider_cfg["api_key"]`.

If you want YAML keys to be used directly, please open an issue or contribute a patch.

---

## `settings`

- Type: `settings`

Fields:

### `requests`

- Type: `int` (> 0)
- Default: `20`

How many total requests to send per provider.

### `concurrency`

- Type: `int` (> 0)
- Default: `3`

Maximum in-flight requests.

### `timeout`

- Type: `int` (> 0)
- Default: `30`

Per-request timeout in seconds.

---

## Environment variables

### `.env`

This project calls `dotenv.load_dotenv()` so a local `.env` file will be loaded automatically.

Example `.env`:

```dotenv
OPENAI_API_KEY=...
DEEPSEEK_API_KEY=...
```

### YAML env var expansion

In YAML, you can reference env vars as `${ENV_NAME}`:

```yaml
api_key: ${OPENAI_API_KEY}
```

The loader expands this at runtime.

---

## Validation rules & errors

Typical errors:

- Missing file: `Config file not found`
- Invalid YAML: `Invalid YAML: ...`
- Wrong types: Pydantic validation errors wrapped as `ConfigError`

Tips:

- Ensure `providers` is a YAML list (`- name: ...`)
- Ensure `settings` is present and is a mapping

---

## Reproducibility checklist

- Use a fixed prompt
- Keep `requests`/`concurrency`/`timeout` stable
- Record provider base URLs and model ids
- Run from the same region/network when comparing changes
- Track both central tendency (p50) and tail (p95)
