# Project Context

## Purpose
This project is an Obsidian AI assistant that provides local LLM capabilities, semantic search, voice input, and comprehensive task management. The project is designed to be offline-first and privacy-focused.

## Tech Stack
- Python (FastAPI, pytest)
- JavaScript/TypeScript (Obsidian plugin)
- Node.js (for plugin development)
- Shell scripts (for setup and testing)
- Makefile

## Project Conventions

### Code Style
- Python: The project uses `black` for formatting, `isort` for import sorting, `flake8` for linting, and `ruff` for additional checks.
- JavaScript/TypeScript: The project uses `prettier` for formatting and `eslint` for linting.

### Architecture Patterns
- The project is structured as a monorepo with a Python backend and a JavaScript/TypeScript frontend (Obsidian plugin).
- The backend is a FastAPI application.
- The plugin interacts with the backend through a REST API.

### Testing Strategy
- The project uses `pytest` for Python testing.
- The project has a `tests` directory which contains unit, integration, and e2e tests.
- The project has a comprehensive testing strategy, with a high level of test coverage.

### Git Workflow
- The project uses a standard Git workflow with feature branches.
- Commit messages should be clear and concise.

## Domain Context
- The project is an Obsidian plugin, so it is important to understand the Obsidian API and plugin development.
- The project uses local LLMs, so it is important to understand how to work with and manage these models.

## Important Constraints
- The project is designed to be offline-first, so all functionality should work without an internet connection.
- The project is privacy-focused, so no user data should be sent to external services.

## External Dependencies
- The project uses Hugging Face for downloading and managing LLMs.
- The project uses `pypdf` for reading PDF files.