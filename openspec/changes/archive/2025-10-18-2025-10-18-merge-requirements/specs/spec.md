# Specification: Requirements File Merge

## Acceptance Criteria
- [x] All packages from requirements.txt, requirements-dev.txt, and requirements-ml.txt merged
- [x] No duplicate package entries
- [x] Packages organized by category with clear comments
- [x] All version pins preserved
- [x] Alphabetical ordering within each category
- [x] requirements-dev.txt and requirements-ml.txt removed (if they existed)

## Technical Requirements

### File Structure
```
# ====================
# Core Dependencies
# ====================
<alphabetically sorted core packages>

# ====================
# AI/ML Dependencies
# ====================
<alphabetically sorted ML packages>

# ====================
# Vector Database
# ====================
<alphabetically sorted vector DB packages>

# ====================
# Development Tools
# ====================
<alphabetically sorted dev packages>

# ====================
# Security & Validation
# ====================
<alphabetically sorted security packages>
```

### Deduplication Rules
1. If package appears in multiple files with same version: keep one
2. If package appears with different versions: keep most recent/compatible
3. If package has no version pin: add appropriate version constraint

### Categories
- **Core**: FastAPI, Pydantic, uvicorn, Python-multipart, etc.
- **AI/ML**: GPT4All, transformers, torch, sentence-transformers, etc.
- **Vector DB**: ChromaDB, hnswlib, etc.
- **Development**: pytest, coverage, black, ruff, etc.
- **Security**: bandit, safety, cryptography, etc.

## Data Models
N/A - no data model changes

## API Changes
N/A - no API changes

## Security & Privacy Notes
- Ensure all security scanning tools remain in requirements
- Verify cryptography and security packages are present
- No sensitive data involved

## Performance Impact
- Neutral - no performance changes expected
- Installation time may slightly improve with deduplicated packages

## Backward Compatibility
- Fully compatible - all existing packages retained
- Setup scripts require no changes
- CI/CD pipelines unaffected
