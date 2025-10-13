# HTTPS/SSL Enforcement for Backend

## Overview
All backend API traffic must use HTTPS. HTTP requests are automatically redirected to HTTPS. SSL certificate and key paths are configured via environment variables.

## Configuration
- `SSL_CERTFILE`: Path to SSL certificate file (PEM format)
- `SSL_KEYFILE`: Path to SSL private key file (PEM format)
- `SSL_CA_CERTS`: Path to CA bundle (optional)
- `FORCE_HTTPS`: Set to `true` to enable HTTP-to-HTTPS redirect (default: true)

## Running Backend with SSL

Example (PowerShell):
```powershell
$env:SSL_CERTFILE = "C:/path/to/cert.pem"
$env:SSL_KEYFILE = "C:/path/to/key.pem"
$env:FORCE_HTTPS = "true"
python -m uvicorn backend.backend:app --host 0.0.0.0 --port 8000 --ssl-keyfile $env:SSL_KEYFILE --ssl-certfile $env:SSL_CERTFILE
```

## Plugin Requirements
- The Obsidian plugin will reject non-HTTPS backend URLs
- Certificate validation is enforced for all connections

## Security Notes
- Use certificates signed by a trusted CA for production
- Self-signed certificates are allowed for local development
- Always keep private keys secure
