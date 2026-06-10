PYTHON = uv run python
MAIN_SCRIPT = fly_in.py
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

.PHONY: all install run debug clean lint lint-strict test

all: install

install:
	@uv sync

run:
	@$(PYTHON) $(MAIN_SCRIPT)

debug:
	@$(PYTHON) -m pdb $(MAIN_SCRIPT)

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
	@uv run flake8 . --exclude .venv,tests
	@echo "Running mypy."
	@uv run mypy . $(MYPY_FLAGS) --exclude "(.venv/|tests/)"

lint-strict:
	@echo "Running flake8."
	@uv run flake8 . --exclude .venv,tests
	@echo "Running mypy --strict."
	@uv run mypy . --strict --exclude "(.venv/|tests/)"

test:
	@echo "Launching the suite of tests."
	@uv run pytest -v



