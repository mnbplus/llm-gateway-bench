PYTHON ?= python

.PHONY: test lint format docs clean

test:
	$(PYTHON) -m pytest -v

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .
	$(PYTHON) -m mypy src

format:
	$(PYTHON) -m ruff check --fix .
	$(PYTHON) -m ruff format .

docs:
	$(PYTHON) -m mkdocs build --strict --site-dir site

clean:
	@powershell -Command "Get-ChildItem -Path . -Recurse -Force -Include __pycache__,*.pyc,.pytest_cache,.mypy_cache,.ruff_cache,coverage.xml,htmlcov,site | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
