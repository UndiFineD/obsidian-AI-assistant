# Proposal: Update backend agent specification for AI orchestration and research

## Rationale
The backend is not just a REST API server, but a modular AI agent capable of:
- Answering questions using local compute AI models (offline/private)
- Indexing, searching, and analyzing Obsidian notes
- Using web hooks and internet access (if enabled) for external research
- Routing requests to other AI agents/models for multi-agent workflows
- Integrating enterprise features and extensible orchestration

This proposal updates the OpenSpec documentation to reflect the backend's role as an AI agent, its API capabilities, and its extensibility for research and orchestration.

## Scope
- Update AGENTS.md and project-documentation/spec.md to clarify backend agent architecture and capabilities
- Add requirements and scenarios for multi-agent orchestration, local/remote model routing, and web research
- Ensure documentation covers both offline and connected modes

## Impact
- Improves clarity for contributors and integrators
- Enables future expansion for agent-to-agent workflows and external model access
- Aligns documentation with actual backend capabilities

## Related files
- openspec/AGENTS.md
- openspec/specs/project-documentation/spec.md
