VENV := .venv
PYTHON_SYS := python3
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
MAIN_SCRIPT := a_maze_ing.py
REQUIREMENTS := requirements.txt
FILE :=

help:
	@echo "Available commands:"
	@echo "  make setup                - Create the virtual environment"
	@echo "  make install              - Install project dependencies in the venv"
	@echo "  make run FILE=filename    - Execute the main script"
	@echo "  make debug FILE=filename  - Run the main script in debug mode"
	@echo "  make clean                - Remove temporary files and caches"
	@echo "  make lint                 - Run flake8 and mypy with required flags"
	@echo "  make lint-strict          - Run flake8 and mypy in strict mode"

setup:
	@if [ ! -d "$(VENV)" ]; then \
		$(PYTHON_SYS) -m venv $(VENV); \
		echo "Virtual environment created in $(VENV)/"; \
		echo "To activate it, run:"; \
		echo "  source $(VENV)/bin/activate"; \
	else \
		echo "Virtual environment already exists in $(VENV)/"; \
	fi

install: setup
	$(VENV)/bin/pip install --upgrade pip setuptools wheel
	$(VENV)/bin/pip install build
	$(VENV)/bin/pip install -r $(REQUIREMENTS)
	$(VENV)/bin/python -m build --outdir .
	rm -rf mazegen.egg-info
	@echo ""
	@echo "Dependencies installed in $(VENV)/"

run:
	$(PYTHON) $(MAIN_SCRIPT) $(FILE)

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(FILE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +

lint:
	$(VENV)/bin/flake8 . --exclude=.venv
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude=.venv

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --strict --exclude=.venv

.DEFAULT_GOAL := help

.PHONY: help setup install run debug clean lint lint-strict