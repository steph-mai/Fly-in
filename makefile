PYTHON = uv run python
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: all install run debug clean lint lint-strict test

all: install

install:
	@uv sync

run:
	@$(PYTHON) -m src

debug:
	@$(PYTHON) -m pdb -m src

clean:
	@echo "Remove temporary files or cache."
	@rm -rf .mypy_cache
	@rm -rf .uv_cache
	@rm -rf .pytest_cache
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.py[co]" -delete
	@echo "Cleaning complete."

lint:
	@echo "Running flake8."
	@uv run flake8 . --exclude .venv
	@echo "Running mypy."
	@uv run mypy . $(MYPY_FLAGS)

lint-strict:
	@echo "Running flake8."
	@uv run flake8 . --exclude .venv
	@echo "Running mypy --strict."
	@uv run mypy . --strict

test:
	@echo "Launching the suite of tests."
	@uv run pytest -v



