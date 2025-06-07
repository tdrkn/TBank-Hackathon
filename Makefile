.PHONY: dev lint test run

dev:
	poetry install

lint:
	ruff src tests
	mypy src tests

test:

	poetry run pytest -s


run:
	poetry run python -m src.main
