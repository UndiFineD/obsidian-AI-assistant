# Security Hardening Design

## Backend (Python)

- Use Pydantic for all request/response validation
- Enforce authentication and RBAC for enterprise/admin endpoints
- Store secrets in environment variables, not code/config files
- Add rate limiting middleware (e.g., slowapi)
- Validate file uploads (PDFs, audio) for type, size, and path
- Use generic error messages for clients; log details server-side
- Enforce HTTPS and strict CORS policies
- Ensure tenant data isolation in multi-tenant mode

## Plugin (JavaScript)

- Always use HTTPS for backend communication
- Sanitize all user input before processing or display
- Hide enterprise/admin features for unauthorized users
- Use try-catch for all async operations
- Avoid storing sensitive data in localStorage
- Audit and update dependencies regularly
- Escape all dynamic content in UI to prevent XSS

## CI/CD & Dependency Management

- Integrate Bandit, Safety, and npm audit in CI/CD
- Pin dependency versions and update regularly
- Document security controls and threat models

## Reference

- See AGENTS.md for OpenSpec conventions
- See project.md for integration points
