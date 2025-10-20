# Design Notes: Backend as Modular AI Agent

- The FastAPI backend serves as an orchestration layer that can:
  - Answer locally via GPT4All/LLaMA
  - Index/search notes via embeddings + vector DB
  - Call web hooks (if enabled) to fetch/summarize external content
  - Delegate to other agents/models for multi-agent workflows
  - Integrate enterprise features (SSO, RBAC, compliance)

- Modes:
  - Offline-first: Only local compute + local data
  - Connected: Optional web access and remote models via approved web hooks or configured providers

- Extensibility:
  - New endpoints for agent delegation
  - Pluggable model/router backends
  - Governance via OpenSpec
  - Mode toggles (offline/connected) enforced centrally in settings and respected by orchestration paths
