PYTHON ?= /opt/homebrew/anaconda3/envs/mlx/bin/python
UVX ?= uvx
PORT ?= 8080

.DEFAULT_GOAL := help

.PHONY: help format lint test check demo

help: ## Show available project commands.
	@awk 'BEGIN {FS = ":.*##"}; /^[a-zA-Z_-]+:.*##/ {printf "%-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

format: ## Apply the project formatter and safe import ordering.
	$(UVX) ruff format .
	$(UVX) ruff check . --fix

lint: ## Check style, imports, and formatting without modifying files.
	$(UVX) ruff check .
	$(UVX) ruff format --check .

test: ## Run fast, local tests.
	$(UVX) pytest

check: lint test ## Run all local quality checks.

demo: ## Serve browser demos at http://127.0.0.1:$(PORT).
	$(PYTHON) -m http.server $(PORT) --directory demos/web
