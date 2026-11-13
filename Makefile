.PHONY: install lint format types test check clean

install:
	python -m pip install -e ".[dev]"

lint:
	ruff check .
	ruff format --check .

format:
	ruff format .
	ruff check . --fix

types:
	python -m mypy
	python -m mypy tests --ignore-missing-imports

test:
	python -m pytest --cov=poster_kreator --cov-report=term-missing --cov-fail-under=90

check: lint types test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist *.egg-info
