# Contributing to llm-gateway-bench

Thank you for your interest! Contributions are welcome.

## Setup

```bash
git clone https://github.com/mnbplus/llm-gateway-bench
cd llm-gateway-bench
pip install -e ".[dev]"
```

## Adding a new provider

1. Add provider defaults to `PROVIDER_DEFAULTS` in `src/llm_gateway_bench/providers.py`
2. Verify the provider works through `lgb run` and YAML-driven `lgb compare`
3. Update provider documentation in `README.md` and `docs/providers.md`
4. Submit a PR!

## Running tests

```bash
python -m pytest
python -m ruff check .
python -m mypy src
```

## Code style

We use `ruff` for linting and `black` for formatting.
