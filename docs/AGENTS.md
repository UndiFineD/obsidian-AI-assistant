<!-- OPENSPEC:START -->

# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:

- Mentions planning or proposals (words like proposal, spec, change, plan)

- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work

- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:

- How to create and apply change proposals

- Spec format and conventions

- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# AGENTS.md

## OpenSpec Agent Documentation

This file describes the OpenSpec agent governance and documentation requirements for the Obsidian AI Assistant project.

- All agent-related changes are tracked via change proposals in `openspec/changes/`

- Each change directory must include:

- `proposal.md`: Change proposal and rationale

- `tasks.md`: Implementation checklist (≥3 items)

- `specs/project-documentation/spec.md`: Capability documentation

See `README.md` and `.github/copilot-instructions.md` for further details on governance and compliance.
