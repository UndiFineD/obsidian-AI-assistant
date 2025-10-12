# Makefile for Obsidian AI Assistant
# Prov	@echo "BATS not installed. Install with package manager or from github.com/bats-core/bats-core";des convenient commands for development, testing, and maintenance

.PHONY: help install install-dev test test-backend test-setup test-coverage lint format clean setup-models run-backend build-plugin

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development and testing dependencies"
	@echo "  test         - Run all tests"
	@echo "  test-backend - Run backend Python tests only"
	@echo "  test-setup   - Run setup script tests"
	@echo "  test-coverage- Run tests with coverage reporting"
	@echo "  lint         - Run code quality checks"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean up temporary files and caches"
	@echo "  setup-models - Download required models"
	@echo "  run-backend  - Start the backend server"
	@echo "  build-plugin - Build the Obsidian plugin"

# Installation targets
install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

install-dev: install
	pip install -r requirements-dev.txt

# Testing targets
test: test-backend test-setup

test-backend:
	@echo "Running backend Python tests..."
	pytest tests/backend/ -v

test-setup:
	@echo "Running setup script tests..."
	@echo "PowerShell tests (Windows):"
	@powershell -Command "if (Get-Module -ListAvailable -Name Pester) { Invoke-Pester tests/setup/test_setup_ps1.ps1 -Verbose } else { Write-Host 'Pester not installed. Run: Install-Module -Name Pester -Force' }"
	@echo "Bash tests (Linux/macOS/WSL):"
	@if command -v bats >/dev/null 2>&1; then \
		bats tests/setup/test_setup_sh.bats; \
	else \
		echo "BATS not installed. Install with: npm install -g bats"; \
	fi

test-coverage:
	@echo "Running tests with coverage..."
	pytest tests/backend/ --cov=backend --cov-report=html --cov-report=term-missing --cov-report=xml

test-unit:
	@echo "Running unit tests only..."
	pytest tests/backend/ -m "unit" -v

test-integration:
	@echo "Running integration tests only..."
	pytest tests/backend/ -m "integration" -v

test-fast:
	@echo "Running fast tests only (excluding slow tests)..."
	pytest tests/backend/ -m "not slow" -v

# Code quality targets
lint:
	@echo "Running flake8..."
	flake8 backend/ tests/ --max-line-length=88 --extend-ignore=E203,W503
	@echo "Running mypy..."
	mypy backend/ --ignore-missing-imports

format:
	@echo "Formatting code with black..."
	black backend/ tests/ --line-length=88
	@echo "Sorting imports with isort..."
	isort backend/ tests/ --profile black

# Cleanup targets
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.log" -delete
	find . -type f -name "temp_*" -delete
	find . -type f -name "*.tmp" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

clean-models:
	@echo "Cleaning model files (keeping directories)..."
	find models/ -name "*.bin" -delete 2>/dev/null || true
	find models/ -name "*.ggml" -delete 2>/dev/null || true

clean-cache:
	@echo "Cleaning cache directories..."
	rm -rf cache/*
	rm -rf vector_db/*

clean-all: clean clean-models clean-cache

# Setup and run targets
setup-models:
	@echo "Creating models directory..."
	mkdir -p models/
	@echo "Models directory created. Download models manually or run setup scripts."

run-backend:
	@echo "Starting backend server..."
	@if [ -f ".venv/bin/activate" ]; then \
		. .venv/bin/activate && python backend/backend.py; \
	elif [ -f ".venv/Scripts/activate" ]; then \
		. .venv/Scripts/activate && python backend/backend.py; \
	else \
		echo "Virtual environment not found. Run setup script first."; \
		exit 1; \
	fi

build-plugin:
	@echo "Building Obsidian plugin..."
	@if [ -d "plugin" ]; then \
		echo "Plugin directory found. JavaScript files are ready for use."; \
	else \
		echo "Plugin directory not found."; \
		exit 1; \
	fi

# Development workflow targets
dev-setup: install-dev setup-models
	@echo "Development environment setup complete!"

dev-test: format lint test-coverage
	@echo "Development testing workflow complete!"

# CI/CD targets
ci-test: install-dev lint test-coverage
	@echo "CI testing complete!"

# Quick development cycle
quick: format test-fast
	@echo "Quick development cycle complete!"

# Documentation targets
docs:
	@echo "Generating documentation..."
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/html; \
	else \
		echo "Sphinx not installed. Install with: pip install sphinx sphinx-rtd-theme"; \
	fi

# Docker targets (if Docker is used in the future)
docker-build:
	docker build -t obsidian-ai-assistant .

docker-run:
	docker run -p 8000:8000 obsidian-ai-assistant

# Backup and restore
backup:
	@echo "Creating backup..."
	tar -czf "backup-$(shell date +%Y%m%d-%H%M%S).tar.gz" \
		--exclude=venv \

		--exclude=models \
		--exclude=cache \
		--exclude=vector_db \
		--exclude=__pycache__ \
		--exclude=.git \
		.

# Information targets
info:
	@echo "=== Obsidian AI Assistant Development Info ==="
	@echo "Python version: $(shell python --version 2>&1)"
	@echo "Pip version: $(shell pip --version)"
	@echo "Virtual environment: $(shell echo $$VIRTUAL_ENV)"
	@echo "Node.js: Removed (project uses Python only)"
	@echo "Pytest version: $(shell pytest --version 2>/dev/null | head -1 || echo 'Not installed')"
	@echo "BATS version: $(shell bats --version 2>/dev/null || echo 'Not installed')"
	@echo "Git branch: $(shell git branch --show-current 2>/dev/null || echo 'Not a git repo')"
	@echo "Project directory: $(shell pwd)"

status:
	@echo "=== Project Status ==="
	@echo "Backend tests: $(shell find tests/backend -name "test_*.py" | wc -l) files"
	@echo "Setup tests: $(shell find tests/setup -name "test_*" | wc -l) files"  
	@echo "Python files: $(shell find backend -name "*.py" | wc -l) files"
	@echo "Cache size: $(shell du -sh cache 2>/dev/null || echo '0B')"
	@echo "Models size: $(shell du -sh models 2>/dev/null || echo '0B')"