# Project Context

## Purpose

This project is an Obsidian AI assistant that provides local LLM capabilities,
semantic search, voice input, and comprehensive task management. The project is
designed to be offline-first and privacy-focused.

## Tech Stack

- Python (FastAPI, pytest)
- JavaScript/TypeScript (Obsidian plugin)
- Node.js (for plugin development)
- Shell scripts (for setup and testing)
- Makefile

## Project Conventions

### Documentation Governance

- The project uses OpenSpec for documentation governance to ensure consistency and quality
- Material changes to documentation require OpenSpec change proposals
- All documentation follows the project-documentation capability requirements

### Code Style

- Python: The project uses `ruff` for linting, with `black`-compatible formatting and import sorting
- JavaScript: The project follows PEP8-inspired JavaScript conventions (4-space indentation, PascalCase classes, camelCase functions)

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
