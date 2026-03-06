PYTHON ?= python3

.PHONY: setup test api cli demo

setup:
	uv venv
	. .venv/bin/activate && uv pip sync requirements.txt

test:
	$(PYTHON) -m pytest -q

api:
	$(PYTHON) run.py api

cli:
	$(PYTHON) run.py cli

demo:
	$(PYTHON) run.py demo

