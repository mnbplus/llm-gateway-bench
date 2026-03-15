# Installation

`llm-gateway-bench` requires **Python 3.9+**.

---

## Install from PyPI (pip)

```bash
pip install llm-gateway-bench
```

Upgrade:

```bash
pip install -U llm-gateway-bench
```

Verify:

```bash
lgb --help
lgb providers
```

---

## Install with pipx (recommended for CLIs)

`pipx` installs `lgb` into an isolated environment.

```bash
pipx install llm-gateway-bench
pipx run llm-gateway-bench --help
```

Upgrade:

```bash
pipx upgrade llm-gateway-bench
```

---

## Install with uv

If you use [`uv`](https://github.com/astral-sh/uv):

```bash
uv tool install llm-gateway-bench
lgb --help
```

Or install into a project environment:

```bash
uv venv
uv pip install llm-gateway-bench
```

---

## Install with conda

If you prefer conda environments, install from PyPI inside conda:

```bash
conda create -n lgb python=3.11 -y
conda activate lgb
python -m pip install llm-gateway-bench
```

---

## Install from source

```bash
git clone https://github.com/YOUR_USERNAME/llm-gateway-bench
cd llm-gateway-bench

# Editable install
python -m pip install -e .

# (Optional) dev tooling
python -m pip install -e ".[dev]"
```

---

## Environment variables (.env)

This project loads `.env` automatically at runtime.

Create a `.env` file (do not commit it):

```dotenv
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
```

See [Providers](providers.md) for the full list of keys.

---

## Troubleshooting

- If `lgb` is not found after install, ensure your Python scripts directory is on `PATH`.
- On Windows, prefer `pipx` or `uv tool` to avoid PATH confusion.

See also: [FAQ](faq.md)
