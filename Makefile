VENV := .venv
PYTHON_SYS := python3
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
MAIN_SCRIPT := a_maze_ing.py
REQUIREMENTS := requirements.txt
FILE :=

help:
	@echo "Available commands:"
	@echo "  make install              - Install project dependencies"
	@echo "  make run FILE=filename    - Execute the main script"
	@echo "  make debug FILE=filename  - Run the main script in debug mode"
	@echo "  make clean                - Remove temporary files and caches"
	@echo "  make lint                 - Run flake8 and mypy with required flags"
	@echo "  make lint-strict          - Run flake8 and mypy in strict mode"

install:
	$(PYTHON_SYS) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip setuptools wheel
	$(VENV)/bin/pip install -r requirements.txt
	@echo ""
	@echo "Virtual environment created in $(VENV)/"
	@echo "To activate it, run:"
	@echo "  source $(VENV)/bin/activate"

run:
	$(PYTHON) $(MAIN_SCRIPT) $(FILE)

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(FILE)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(VENV)/bin/flake8 . --exclude=.venv
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs --exclude=.venv

lint-strict:
	flake8 .
	mypy . --strict

.DEFAULT_GOAL := help

.PHONY: help install run debug clean lint lint-strict