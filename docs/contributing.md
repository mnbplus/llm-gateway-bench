# Contributing

Thanks for contributing to **llm-gateway-bench**.

This guide focuses on:

- setting up a development environment
- running tests and linters
- contributing docs

> If you are looking for the repository-level contributing doc, also see `CONTRIBUTING.md` at the repo root.

---

## Development setup

### Prerequisites

- Python **3.9+**
- Git

Optional but recommended:

- `uv` (fast Python env management)

### Clone

```bash
git clone https://github.com/YOUR_USERNAME/llm-gateway-bench
cd llm-gateway-bench
```

### Create an environment

Using `venv`:

```bash
python -m venv .venv

# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

Install editable + dev deps:

```bash
python -m pip install -U pip
python -m pip install -e ".[dev]"
```

---

## Run tests

```bash
pytest
```

With coverage:

```bash
pytest --cov
```

---

## Linting & formatting

- Format: `black`
- Lint: `ruff`
- Types: `mypy`

Suggested commands:

```bash
ruff check .
black .
mypy src
```

---

## Working on documentation

### Build docs locally

```bash
python -m pip install -e ".[dev]"
mkdocs serve
```

Open <http://127.0.0.1:8000>.

### Documentation style

- Prefer short sections and runnable snippets
- Use stable relative links between pages
- Avoid provider marketing claims; document steps + gotchas

---

## Adding or improving providers

Provider defaults live in `src/llm_gateway_bench/bench.py` (`PROVIDER_DEFAULTS`).

Before adding a provider:

1. Verify the endpoint is OpenAI-compatible
2. Confirm the correct base URL
3. Identify the environment variable name for API key
4. Add notes to [Providers](providers.md)

---

## PR checklist

- [ ] Tests pass (`pytest`)
- [ ] Lint passes (`ruff check .`)
- [ ] Formatting applied (`black .`)
- [ ] Updated docs for user-facing changes
- [ ] Changelog entry if behavior changes

---

## Commit messages

Use conventional, readable messages. Examples:

- `docs: improve provider setup examples`
- `feat: add report json output`
- `fix: handle streaming usage missing`

---

## Security and secrets

- Never commit real API keys
- Use `.env` locally and GitHub Secrets in CI

---

## Getting help

Open an issue with:

- provider name + base URL
- model id
- a minimal command that reproduces the bug
- sanitized error output
