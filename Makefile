.DEFAULT_GOAL := help
.PHONY: run test fmt lint typecheck clean

help:
	@echo "Available targets: "
	@echo "make run 		- start the server"
	@echo "make test 		- run tests"
	@echo "make fmt			- format code"
	@echo "make lint		- check code style"
	@echo "make typecheck	- run mypy"
	@echo "make clean		- remove cache files"

run:
	poetry run uvicorn petri.main:app --reload

test:
	poetry run pytest

fmt:
	poetry run ruff format .
	poetry run ruff check --fix .

lint:
	poetry run ruff check .

typecheck:
	poetry run mypy petri/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
