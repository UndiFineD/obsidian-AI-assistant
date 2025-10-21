# OpenSpec Change Tasks: Modular API Structure

## Phase 1: Preparation (2-3 hours)

### 1.1 Create API Directory Structure
- **Task**: Create `agent/api/` directory with module files
- **Subtasks**:
    1. Create `agent/api/` directory
    2. Create `agent/api/__init__.py`
    3. Create `agent/api/base.py`
    4. Create placeholder files for all modules (health, config, auth, ask, search, indexing, voice, cache, logs, security, enterprise)
- **Acceptance Criteria**:
    - All directories exist
    - All module files created
    - Directory structure ready for migration

### 1.2 Design Base Router Utilities
- **Task**: Create common utilities for all API modules
- **File**: `agent/api/base.py`
- **Content**:
    1. BaseRouter class with common setup
    2. Common error handlers
    3. Common response models
    4. Dependency injection utilities
    5. Type definitions
- **Acceptance Criteria**:
    - Base utilities useful across modules
    - No duplication needed in modules
    - Easy to extend

### 1.3 Plan Endpoint Groupings
- **Task**: Document which endpoints go to which module
- **File**: `ENDPOINT_GROUPINGS.md`
- **Content**:
    1. Health: /health, /status, /api/health/*
    2. Config: /api/config, /api/config/reload
    3. Auth: /api/auth/*, authentication endpoints
    4. Ask: /ask, /api/ask
    5. Search: /api/search
    6. Indexing: /reindex, /api/scan_vault, /api/index_pdf
    7. Voice: /transcribe
    8. Cache: /api/cache/*
    9. Logs: /api/logs/*
    10. Security: /api/security/*
    11. Enterprise: /api/enterprise/*
- **Acceptance Criteria**:
    - All endpoints assigned
    - No conflicts
    - Clear grouping rationale

### 1.4 Design Module Interfaces
- **Task**: Define common interface for all API modules
- **Content**:
    1. Module structure pattern
    2. Router creation pattern
    3. Endpoint decorators pattern
    4. Response model pattern
    5. Error handling pattern
- **Acceptance Criteria**:
    - Pattern documented
    - Example provided
    - Reusable across modules

### 1.5 Plan Import Updates
- **Task**: Document all import changes needed
- **Content**:
    1. Services moved to modules
    2. Dependencies updated
    3. Utility imports
    4. Configuration imports
    5. Type imports
- **Acceptance Criteria**:
    - Complete import mapping
    - No missing dependencies
    - Ready for implementation

---

## Phase 2: Migration (4-6 hours)

### 2.1 Migrate Health Endpoints
- **Task**: Move health endpoints to `agent/api/health.py`
- **Endpoints**:
    1. GET `/health`
    2. GET `/status`
    3. GET `/api/health`
    4. GET `/api/health/detailed`
    5. GET `/api/health/metrics`
    6. GET `/api/health/alerts`
    7. POST `/api/health/alerts/{alert_id}/acknowledge`
- **Implementation**:
    1. Extract endpoint logic from backend.py
    2. Create router in health.py
    3. Add endpoints with same paths
    4. Update imports
    5. Test endpoints work
- **Acceptance Criteria**:
    - All health endpoints work
    - Same response format
    - No endpoint changes
    - Tests passing

### 2.2 Migrate Config Endpoints
- **Task**: Move config endpoints to `agent/api/config.py`
- **Endpoints**:
    1. GET `/api/config`
    2. POST `/api/config`
    3. POST `/api/config/reload`
- **Implementation**: Same as health.py
- **Acceptance Criteria**: All config endpoints working

### 2.3 Migrate Auth Endpoints
- **Task**: Move auth endpoints to `agent/api/auth.py`
- **Endpoints**:
    1. POST `/api/auth/token`
    2. GET `/api/auth/verify`
    3. POST `/api/auth/api_key/rotate`
    4. Additional auth endpoints
- **Implementation**: Same pattern
- **Acceptance Criteria**: All auth endpoints working

### 2.4 Migrate Ask Endpoints
- **Task**: Move ask endpoints to `agent/api/ask.py`
- **Endpoints**:
    1. POST `/ask`
    2. POST `/api/ask`
- **Implementation**: Same pattern
- **Acceptance Criteria**: Both endpoints work identically

### 2.5 Migrate Search Endpoints
- **Task**: Move search endpoints to `agent/api/search.py`
- **Endpoints**:
    1. POST `/api/search`
- **Implementation**: Same pattern
- **Acceptance Criteria**: Search endpoint working

### 2.6 Migrate Indexing Endpoints
- **Task**: Move indexing endpoints to `agent/api/indexing.py`
- **Endpoints**:
    1. POST `/reindex`
    2. POST `/api/scan_vault`
    3. POST `/api/index_pdf`
- **Implementation**: Same pattern
- **Acceptance Criteria**: All indexing endpoints working

### 2.7 Migrate Voice Endpoints
- **Task**: Move voice endpoints to `agent/api/voice.py`
- **Endpoints**:
    1. POST `/transcribe`
    2. POST `/api/voice_transcribe`
- **Implementation**: Same pattern
- **Acceptance Criteria**: Voice endpoints working

### 2.8 Migrate Cache Endpoints
- **Task**: Move cache endpoints to `agent/api/cache.py`
- **Endpoints**:
    1. POST `/api/cache/clear`
    2. POST `/api/cache/*` (all cache endpoints)
- **Implementation**: Same pattern
- **Acceptance Criteria**: Cache endpoints working

### 2.9 Migrate Logs Endpoints
- **Task**: Move logging endpoints to `agent/api/logs.py`
- **Endpoints**:
    1. GET `/api/logs/*`
    2. POST `/api/logs/*`
- **Implementation**: Same pattern
- **Acceptance Criteria**: Logging endpoints working

### 2.10 Migrate Security Endpoints
- **Task**: Move security endpoints to `agent/api/security.py`
- **Endpoints**:
    1. POST `/api/security/*`
    2. Security-related endpoints
- **Implementation**: Same pattern
- **Acceptance Criteria**: Security endpoints working

### 2.11 Create Enterprise Module
- **Task**: Create `agent/api/enterprise.py` for optional features
- **Endpoints**:
    1. GET `/api/enterprise/status`
    2. POST `/api/enterprise/auth/sso`
    3. GET `/api/enterprise/users`
    4. POST `/api/enterprise/tenants`
    5. GET `/api/enterprise/compliance/*`
- **Implementation**: Optional router
- **Acceptance Criteria**: Enterprise module created, optional loading

---

## Phase 3: Integration (2-3 hours)

### 3.1 Create Router Registration System
- **Task**: Implement router registration in `agent/api/__init__.py`
- **Content**:
    1. Import all routers
    2. Create register_routers() function
    3. Handle optional enterprise router
    4. Export for use in app.py
- **Acceptance Criteria**:
    - Clean registration interface
    - Easy to add/remove routers
    - Optional routers supported

### 3.2 Create Application Factory
- **Task**: Implement app factory in `agent/app.py`
- **Content**:
    1. create_app() function
    2. FastAPI configuration
    3. Router registration
    4. Middleware setup
    5. Exception handling
- **Acceptance Criteria**:
    - Clean app initialization
    - All routers registered
    - Middleware properly configured

### 3.3 Refactor Backend Main File
- **Task**: Update `agent/backend.py` to use new structure
- **Changes**:
    1. Import app from app.py
    2. Remove endpoint decorators
    3. Keep service logic
    4. Update initialization
    5. Export app instance
- **Acceptance Criteria**:
    - backend.py simplified
    - No duplicate endpoints
    - All endpoints accessible

### 3.4 Update Dependencies
- **Task**: Update all imports throughout codebase
- **Updates**:
    1. Test file imports
    2. Utility imports
    3. Service imports
    4. Configuration imports
- **Acceptance Criteria**:
    - All imports correct
    - No import errors
    - No circular imports

### 3.5 Verify Endpoint Accessibility
- **Task**: Test all endpoints accessible from main app
- **Tests**:
    1. All health endpoints work
    2. All config endpoints work
    3. All auth endpoints work
    4. All ask endpoints work
    5. All search endpoints work
    6. All indexing endpoints work
    7. All voice endpoints work
    8. All cache endpoints work
    9. All security endpoints work
    10. Enterprise endpoints conditional
- **Acceptance Criteria**:
    - All endpoints returning correct responses
    - No 404 errors
    - Status codes correct

---

## Phase 4: Verification (2-3 hours)

### 4.1 Run Full Endpoint Test Suite
- **Task**: Execute all endpoint tests
- **Scope**:
    1. Unit tests for each module
    2. Integration tests for router registration
    3. API endpoint tests
    4. Response validation tests
- **Acceptance Criteria**:
    - 100% test pass rate
    - No new failures
    - Coverage maintained

### 4.2 Verify Backward Compatibility
- **Task**: Test all original endpoint paths work
- **Tests**:
    1. Test /ask and /api/ask both work
    2. Test /health and /api/health both work
    3. Test all aliases work
    4. Test old response formats preserved
- **Acceptance Criteria**:
    - Perfect backward compatibility
    - No breaking changes
    - All tests passing

### 4.3 Test Endpoint Discovery
- **Task**: Verify endpoints appear in API documentation
- **Tests**:
    1. OpenAPI schema complete
    2. All endpoints documented
    3. Swagger UI shows all endpoints
    4. ReDoc shows all endpoints
- **Acceptance Criteria**:
    - Full API documentation available
    - All endpoints discoverable
    - Correct schemas

### 4.4 Performance Validation
- **Task**: Verify no performance degradation
- **Tests**:
    1. Benchmark endpoint response times
    2. Measure memory usage
    3. Check startup time
    4. Validate concurrent requests
- **Acceptance Criteria**:
    - <5% variance in response time
    - No memory leaks
    - Same startup performance

### 4.5 Load Testing
- **Task**: Test system under load
- **Scenarios**:
    1. 100 concurrent requests
    2. 1000 requests per second
    3. Long-running connections
    4. Mixed endpoint types
- **Acceptance Criteria**:
    - System handles load
    - No 500 errors
    - Response times acceptable

---

## Phase 5: Documentation (1-2 hours)

### 5.1 Create API Module Guide
- **Task**: Document new API structure
- **File**: `docs/API_MODULE_GUIDE.md`
- **Content**:
    1. Directory structure explanation
    2. Module responsibilities
    3. How to find endpoints
    4. How to add new endpoints
    5. Common patterns
- **Acceptance Criteria**:
    - Comprehensive guide
    - Easy to follow
    - Examples provided

### 5.2 Update Architecture Documentation
- **Task**: Update system architecture docs
- **Files to update**:
    1. `.github/copilot-instructions.md`
    2. `docs/SYSTEM_ARCHITECTURE_SPECIFICATION.md`
- **Changes**:
    1. Add API structure diagram
    2. Explain routing pattern
    3. Show module organization
    4. Update examples
- **Acceptance Criteria**:
    - Architecture docs current
    - Diagrams updated
    - Examples correct

### 5.3 Create API Contribution Guide
- **Task**: Document how to contribute to API
- **File**: `docs/API_CONTRIBUTION_GUIDE.md`
- **Content**:
    1. Adding new endpoints
    2. Module structure pattern
    3. Testing endpoints
    4. Documentation requirements
    5. Code review process
- **Acceptance Criteria**:
    - Clear contribution steps
    - Patterns documented
    - Examples provided

### 5.4 Update Developer Setup Guide
- **Task**: Update setup documentation
- **Files to update**:
    1. `README.md` - Quick start
    2. `docs/SETUP_README.md` - Full setup
    3. `.github/copilot-instructions.md` - Instructions
- **Changes**:
    1. Explain new API structure
    2. How to run API locally
    3. How to test endpoints
    4. Common development tasks
- **Acceptance Criteria**:
    - Setup guide current
    - Instructions clear
    - Examples working

### 5.5 Create Endpoint Reference
- **Task**: Create quick reference for all endpoints
- **File**: `docs/API_ENDPOINTS_REFERENCE.md`
- **Content**:
    1. All endpoints by domain
    2. Path, method, authentication
    3. Request/response examples
    4. Status codes
    5. Error handling
- **Acceptance Criteria**:
    - Complete endpoint list
    - All examples valid
    - Easy to search

---

## Cross-Phase Activities

### Continuous Testing
- **When**: After each phase
- **Scope**: Unit + integration tests
- **Coverage**: 95%+ for API modules
- **Frequency**: After each module migration

### Code Review
- **When**: After each phase
- **Focus**: Structure, patterns, completeness
- **Reviewers**: Senior developers
- **Frequency**: Weekly during migration

### Performance Monitoring
- **When**: Throughout implementation
- **Metrics**: Response time, memory, startup time
- **Target**: No degradation vs baseline
- **Frequency**: Continuous

### Documentation Updates
- **When**: As changes are made
- **Owner**: Technical writer
- **Scope**: Keep docs in sync
- **Frequency**: Ongoing

---

## Success Metrics

| Metric | Target | Validation |
|--------|--------|-----------|
| Endpoints migrated | 100% | All endpoints in modules |
| Backward compatibility | 100% | All tests pass |
| Code coverage | 95%+ | Coverage reports |
| Response time | <5% variance | Performance tests |
| Documentation | 100% complete | All guides written |

---

**Task Status**: Ready for Implementation  
**Created**: October 21, 2025  
**Version**: 1.0
