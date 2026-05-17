.PHONY: install test lint

install:
	uv pip install -e .[dev]

test:
	pytest -q

lint:
	ruff check src tests
