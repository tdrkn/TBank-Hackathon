.PHONY: dev lint test run

dev:
	poetry install

lint:
	ruff src tests
	mypy src tests

test:
	pytest -s

run:
	poetry run python -m src.main
