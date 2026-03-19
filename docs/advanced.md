# Advanced usage

This page collects power-user workflows: custom payloads, batch experiments, and CI integration.

---

## Custom prompts

### Multiple prompts

The YAML schema supports a list of prompts:

```yaml
prompts:
  - "Write a haiku about the ocean."
  - "Explain KV cache in one paragraph."
```

Current behavior:

- The benchmark uses **the first prompt** (`prompts[0]`).

If you need “run all prompts”, you can run multiple times (see Batch runs below), or contribute a feature.

---

## Benchmark an OpenAI-compatible gateway

### CLI

```bash
lgb run --provider custom --model my-model \
  --base-url https://my-gateway.example/v1 \
  --prompt "Say hello." \
  --requests 50 --concurrency 10
```

### YAML

```yaml
providers:
  - name: custom
    model: my-model
    base_url: https://my-gateway.example/v1
    api_key: ${MY_GATEWAY_API_KEY}
```

---

## Batch experiments

### Matrix run (models × concurrency)

In Bash:

```bash
for c in 1 3 10; do
  for m in gpt-4.1-mini gpt-4.1; do
    lgb run --provider openai --model "$m" --concurrency "$c" --requests 30 \
      --output "reports/openai_${m}_c${c}.md"
  done
done
```

In PowerShell:

```powershell
$models = @('gpt-4.1-mini','gpt-4.1')
$concurrency = @(1,3,10)

foreach ($c in $concurrency) {
  foreach ($m in $models) {
    lgb run --provider openai --model $m --concurrency $c --requests 30 `
      --output ("reports/openai_{0}_c{1}.md" -f $m,$c)
  }
}
```

---

## Making results comparable

To reduce noise:

- Keep **prompt text** stable
- Fix **requests** and **concurrency**
- Run from the same region/network
- Repeat runs and compare medians / p95

---

## CI integration (GitHub Actions)

You can run a small benchmark suite on a schedule, or on every release.

> ⚠️ Be careful with cost: benchmarking sends real requests.

Example workflow (`.github/workflows/bench.yml`):

```yaml
name: Bench

on:
  workflow_dispatch:
  schedule:
    - cron: "0 3 * * *"  # daily

jobs:
  bench:
    runs-on: ubuntu-latest
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install
        run: |
          python -m pip install -U pip
          python -m pip install llm-gateway-bench

      - name: Run suite
        run: |
          lgb compare example-bench.yaml --output bench-report.md

      - name: Upload report artifact
        uses: actions/upload-artifact@v4
        with:
          name: bench-report
          path: bench-report.md
```

---

## CI integration (pull requests)

For PRs, consider a **smoke benchmark** with low request count:

- `requests: 3`
- `concurrency: 1`

This catches obvious failures without burning budget.

---

## Custom provider fields

Provider entries allow extra fields in YAML (future-proofing). For example:

```yaml
providers:
  - name: openrouter
    model: meta-llama/llama-3.3-70b-instruct
    api_key: ${OPENROUTER_API_KEY}
    # extra fields (ignored by the current runner)
    headers:
      HTTP-Referer: https://example.com
      X-Title: llm-gateway-bench
```

Note: currently `name`, `model`, `base_url`, and `api_key` are used by the runner. Extra fields are preserved in config validation but ignored during execution.
