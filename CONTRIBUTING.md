# Contributing to llm-gateway-bench

Thank you for your interest! Contributions are welcome.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/llm-gateway-bench
cd llm-gateway-bench
pip install -e ".[dev]"
```

## Adding a new provider

1. Add provider defaults to `PROVIDER_DEFAULTS` in `bench.py`
2. Add an entry to the `providers()` command in `cli.py`
3. Add a row to the provider table in `README.md`
4. Submit a PR!

## Running tests

```bash
pytest tests/
```

## Code style

We use `ruff` for linting and `black` for formatting.
