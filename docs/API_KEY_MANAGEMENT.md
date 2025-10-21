# API Key Management & Rotation

## Overview
API keys are used to authenticate and authorize access to sensitive endpoints. This system supports secure API key
generation, validation, deactivation, and rotation via REST endpoints.

## Key Features
- **Key Generation**: Secure random API keys (token_urlsafe, 32 bytes)
- **Key Rotation**: Deactivate old key, issue new key atomically
- **Validation**: SHA-256 hashed keys, active/inactive status
- **Deactivation**: Keys can be revoked/deactivated
- **Endpoint**: `/api/auth/api_key/rotate` for rotation

## API Endpoints
### Rotate API Key
- **POST** `/api/auth/api_key/rotate`
- **Request Body**:
  ```json
  { "old_key": "<current_api_key>" }
  ```
- **Response**:
  ```json
  { "new_key": "<new_api_key>", "rotated": true }
  ```
- **Errors**:
  - `401 Unauthorized`: Invalid or inactive API key
  - `500 Internal Server Error`: Unexpected failure

## Security Notes
- Keys are stored as SHA-256 hashes (never plain text)
- Old keys are deactivated on rotation
- Always use HTTPS in production
- Replace in-memory store with persistent DB for production

## Example Usage
1. **Generate API key** (admin tool or endpoint)
2. **Rotate key** via `/api/auth/api_key/rotate`
3. **Use new key for subsequent requests
4. **Deactivated keys are rejected

## Implementation Reference
- See `agent/api_key_management.py` for logic
- See `tests/agent/test_api_key_rotation.py` for tests
- Endpoint defined in `agent/backend.py`

## TODO
- Add persistent storage for keys
- Add admin endpoints for key listing/revocation
- Integrate with user/role management
