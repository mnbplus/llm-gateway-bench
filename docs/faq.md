# FAQ

## What does TTFT mean?

TTFT = **Time To First Token**. It measures how long it takes from request start until the model streams the first token.

---

## What is measured exactly?

For each request, the runner measures:

- **TTFT**: first streamed content token observed
- **Total latency**: until the stream finishes
- **Tokens/sec**: completion tokens divided by wall time (approx.)

---

## Why do I see high variance between runs?

Common causes:

- Internet routing / packet loss
- Provider rate limits and queueing
- Cold starts / cache warm-up
- Prompt length variability (if you change prompts)

Try increasing `requests`, running from a stable network, and comparing **median/p95**.

---

## My provider works in curl but fails here. Why?

This tool currently uses the **OpenAI Python SDK** and calls:

- `chat.completions.create(stream=True)`
- `stream_options={"include_usage": True}`

Some “OpenAI-compatible” endpoints do not fully match the streaming protocol or do not support `stream_options`.

---

## Where do API keys come from?

From environment variables (and `.env`). The mapping is defined in code.

See [Providers](providers.md).

---

## Why is `api_key` in YAML not used?

`bench.yaml` supports `api_key: ${ENV_NAME}` and the loader expands it, but **the current benchmark runner still reads keys from environment variables** based on the provider name.

This is intentional for simplicity today, but may be improved. If you need YAML-driven keys, contributions are welcome.

---

## How do I benchmark a self-hosted vLLM/Ollama/LM Studio?

Use `--base-url` (or YAML `base_url`) pointing to your OpenAI-compatible endpoint:

- vLLM: `http://<host>:8000/v1`
- Ollama: `http://localhost:11434/v1`
- LM Studio: `http://localhost:1234/v1`

Some local servers accept any `api_key` (or require a dummy value).

---

## I get timeouts. What should I do?

- Increase `--timeout` (or `settings.timeout`)
- Reduce `--concurrency`
- Use shorter prompts
- Ensure the provider supports streaming

---

## What do p50/p95 mean?

- **p50**: median latency (typical case)
- **p95**: 95th percentile latency (tail latency)

Tail latency often matters most for user experience.

---

## Does this tool count prompt tokens?

Currently it relies on streaming `usage` metadata for **completion tokens**. Prompt tokens are not summarized in the table.

---

## The success rate is < 100%. What counts as failure?

Any request that raises an exception (network error, auth error, provider error, timeout) is counted as an error.

---

## How do I run on Windows?

Use PowerShell examples in [Quickstart](quickstart.md). If you hit PATH issues, install via `pipx`.

---

## Is the throughput number reliable?

It is an approximation:

- It uses reported completion tokens
- Divides by observed wall time

It is good for **relative comparisons** under the same setup.

---

## How can I contribute a new provider?

Most providers should work via `base_url` if they are OpenAI-compatible.

If a provider needs a native SDK, see [Contributing](contributing.md) and open an issue describing the API shape.
