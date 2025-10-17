# Platform Documentation Overview

This document describes the platform context, supported environments, and integration points for the Obsidian AI Assistant project. It is governed by OpenSpec and must be updated via change proposals for material changes.

## Supported Platforms

- **Windows 10+**
- **macOS 10.15+**
- **Ubuntu 18.04+**
- **Obsidian Desktop (latest stable)**
- **Obsidian Mobile (limited support)**
- **Docker (production deployment)**
- **Kubernetes (enterprise deployment)**

## Integration Points

- **Obsidian Plugin**: JavaScript plugin, no build step, integrates with backend via REST API
- **Backend Server**: FastAPI, local AI models, vector DB, enterprise features
- **Enterprise Modules**: SSO, RBAC, multi-tenant, compliance, admin dashboard
- **Automation Scripts**: PowerShell and Bash for setup, validation, and deployment
- **CI/CD**: GitHub Actions for validation, application, and archiving

## Deployment Patterns

- **Local Development**: Windows/macOS/Linux, PowerShell/Bash scripts, hot reload
- **Production**: Docker, systemd/supervisor, multi-instance scaling
- **Enterprise**: Kubernetes, resource quotas, compliance monitoring

## Platform Requirements

- **CPU**: 2+ cores (dev), 8+ cores (prod)
- **RAM**: 4GB+ (dev), 32GB+ (enterprise)
- **Storage**: 5GB+ SSD (dev), 100GB+ NVMe (prod)
- **GPU**: Optional, recommended for large models
- **Network**: 10Mbps+ (dev), gigabit (prod)

## Governance Notes

- All platform documentation changes MUST follow OpenSpec proposal and validation workflow
- Platform requirements and supported environments SHALL be kept up to date with each release
- Integration points and deployment patterns SHALL be documented for new features and modules

## References

- [README.md](../README.md)
- [System Architecture Specification](./SYSTEM_ARCHITECTURE_SPECIFICATION.md)
- [Deployment Specification](./DEPLOYMENT_SPECIFICATION.md)
- [Enterprise Features Specification](./ENTERPRISE_FEATURES_SPECIFICATION.md)
- [Contributor Guide](./contributor-guide.md)

---

**Last Updated:** October 16, 2025
