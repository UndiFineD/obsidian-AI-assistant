# JWT Secret Management

## Overview
JWT (JSON Web Token) secrets are used to sign and verify authentication tokens. Proper management of these secrets is critical for security.

## Best Practices
- **Never hardcode secrets in code**: Always load secrets from environment variables or secure configuration files.
- **Use strong, random secrets**: Minimum 32 bytes, generated with a cryptographically secure random generator.
- **Rotate secrets periodically**: Change secrets regularly and after any suspected compromise.
- **Restrict access**: Only the backend service should have access to the JWT secret.
- **Redact secrets in logs and APIs**: Never expose secrets in logs, error messages, or API responses.

## Implementation in This Project
- The main backend loads the JWT secret from the environment variable `JWT_SECRET_KEY`:
  ```python
  JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-secret-key-change-in-production")
  ```
- The `Settings` class also supports `jwt_secret_key` from environment/config.
- Enterprise modules accept a `secret_key` parameter for SSO/JWT operations.
- Secrets are redacted in config APIs and never returned to clients.
- Default secrets in code are for development only. **Always override in production!**

## How to Set the JWT Secret
- **Development**: Set `JWT_SECRET_KEY` in your `.env` file or environment.
- **Production**: Set `JWT_SECRET_KEY` as a secure environment variable (do not use the default!).
- **Kubernetes/Cloud**: Use secrets management (e.g., Kubernetes Secrets, Azure Key Vault, AWS Secrets Manager).

## Example (Linux/macOS)
```bash
export JWT_SECRET_KEY="$(openssl rand -base64 48)"
```

## Example (Windows PowerShell)
```powershell
$env:JWT_SECRET_KEY = [Convert]::ToBase64String((1..48 | ForEach-Object {Get-Random -Maximum 256}))
```

## References
- [OWASP JWT Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/advanced/security/)

## TODO
- Add automated secret rotation support
- Enforce minimum secret length at startup
- Add secret audit logging
