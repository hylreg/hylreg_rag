PYTHON ?= python3

.PHONY: setup test lint typecheck check api cli demo

setup:
	uv venv
	. .venv/bin/activate && uv pip sync requirements.txt
	. .venv/bin/activate && uv pip install -e ".[dev]"

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m black --check .
	$(PYTHON) -m flake8 src tests

typecheck:
	$(PYTHON) -m mypy src

check: lint typecheck test

api:
	$(PYTHON) run.py api

cli:
	$(PYTHON) run.py cli

demo:
	$(PYTHON) run.py demo
