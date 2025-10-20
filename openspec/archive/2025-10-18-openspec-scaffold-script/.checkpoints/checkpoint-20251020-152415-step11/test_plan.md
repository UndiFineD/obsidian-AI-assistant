# Test Plan: OpenSpec Scaffold Script

## Unit Tests
- Slugify behavior for titles with punctuation and spaces
- Default change-id generation format `YYYY-MM-DD-<slug>`
- Directory and files created under temporary path
- Placeholder replacement in `todo.md`
- Idempotency: without `--force`, existing directory is not overwritten

## Integration Test (optional)
- Run the CLI against a temp repo layout and verify outputs
