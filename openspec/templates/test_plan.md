# Test Plan: [Change ID]

---

## Document Overview

**Purpose**: Define comprehensive testing strategy, test cases, and validation criteria for a project or change.
**Change ID**: `[change-id]`
**Related Proposal**: [Link to proposal.md]
**Related Spec**: [Link to spec.md]
**Related Tasks**: [Link to tasks.md]
**Owner**: @[username]
**QA Lead**: @[username]
**Status**: [Draft / In Review / Approved / In Progress / Complete]

---

## Table of Contents

### Planning & Strategy (1-5)
01. [Test Strategy](#test-strategy)
02. [Test Scope](#test-scope)
03. [Test Objectives](#test-objectives)
04. [Test Automation Strategy](#test-automation-strategy)
05. [Test Types & Coverage](#test-types--coverage)

### Test Implementation (6-14)
06. [Unit Testing](#unit-testing)
07. [Integration Testing](#integration-testing)
08. [End-to-End Testing](#end-to-end-testing)
09. [Performance Testing](#performance-testing)
10. [Security Testing](#security-testing)
11. [Accessibility Testing](#accessibility-testing)
12. [Compatibility Testing](#compatibility-testing)
13. [User Acceptance Testing (UAT)](#user-acceptance-testing-uat)
14. [Regression Testing](#regression-testing)

### Test Infrastructure (15-16)
15. [Test Environment](#test-environment)
16. [Test Data Management](#test-data-management)

### Test Execution & Management (17-20)
17. [Test Execution Schedule](#test-execution-schedule)
18. [Defect Management](#defect-management)
19. [Test Metrics & Reporting](#test-metrics--reporting)
20. [Risk Assessment](#risk-assessment)

### Test Completion (21-25)
21. [Test Deliverables](#test-deliverables)
22. [Entry & Exit Criteria](#entry--exit-criteria)
23. [Validation Checklist](#validation-checklist)
24. [Test Results Summary](#test-results-summary)
25. [Document Metadata](#document-metadata)

---

## Test Strategy

**Testing Approach**: [Describe overall testing philosophy - e.g., Shift-Left, Risk-Based, Agile Testing]

**Testing Principles**:
- **Early Testing**: Testing activities begin in requirements phase
- **Continuous Testing**: Automated tests run on every commit
- **Risk-Based**: Focus testing efforts on high-risk areas
- **Defect Prevention**: Identify and fix issues early
- **Comprehensive Coverage**: All code paths, features, and scenarios tested

**Testing Pyramid**:
```
        /\
       /  \  E2E Tests (10%)
      /    \
     /------\  Integration Tests (30%)
    /        \
   /----------\  Unit Tests (60%)
  /            \
```

**Test Level Distribution**:
- **Unit Tests**: 60% - Fast, isolated, developer-owned
- **Integration Tests**: 30% - Component interactions, API contracts
- **End-to-End Tests**: 10% - Critical user workflows, high-value scenarios

**Quality Gates**:
- All unit tests must pass before code review
- Integration tests must pass before merge to main
- E2E tests must pass before deployment to staging
- Performance tests must meet targets before production

---

## Test Scope

**In Scope**:
- [Feature 1]: [Description of what will be tested]
- [Feature 2]: [Description]
- [Feature 3]: [Description]
- All new and modified code
- Regression testing of existing features
- Performance benchmarks
- Security vulnerability scanning

**Out of Scope**:
- [Feature X]: [Reason for exclusion - e.g., "Not in current release"]
- [System Y]: [Reason - e.g., "Third-party system, not our responsibility"]
- [Scenario Z]: [Reason - e.g., "Edge case deferred to future release"]

**Testing Boundaries**:
- **Start**: [When testing begins - e.g., "After feature implementation complete"]
- **End**: [When testing concludes - e.g., "After production validation"]
- **Inclusions**: [What's definitely tested]
- **Exclusions**: [What's explicitly not tested]

---

## Test Objectives

**Primary Objectives**:
1. **Functional Correctness**: Verify all features work as specified
2. **Quality Assurance**: Ensure code meets quality standards
3. **Risk Mitigation**: Identify and prevent defects before production
4. **Performance Validation**: Confirm system meets performance targets
5. **Security Assurance**: Validate security controls are effective

**Success Criteria**:
- ✅ All critical (P0) and high-priority (P1) test cases pass
- ✅ Test coverage ≥ [80%] for unit tests
- ✅ Test coverage ≥ [70%] for integration tests
- ✅ No open P0 or P1 defects
- ✅ All performance benchmarks met
- ✅ Security scan passes with no critical/high vulnerabilities
- ✅ Stakeholder acceptance obtained

---

## Test Types & Coverage

**Test Type Coverage Matrix**:

| Test Type | Coverage Target | Automation | Owner | Tools |
|-----------|----------------|------------|-------|-------|
| Unit Tests | ≥80% code coverage | 100% automated | Developers | [pytest, Jest, JUnit] |
| Integration Tests | ≥70% API coverage | 100% automated | QA + Dev | [Supertest, Postman/Newman] |
| E2E Tests | Critical paths | 80% automated | QA | [Cypress, Playwright, Selenium] |
| Performance Tests | Key endpoints | 100% automated | DevOps + QA | [JMeter, k6, Gatling] |
| Security Tests | All endpoints | 100% automated | Security + QA | [OWASP ZAP, Snyk, Bandit] |
| Accessibility | Key pages | 50% automated | QA | [axe, WAVE, Lighthouse] |
| Compatibility | Browser matrix | Manual + smoke | QA | [BrowserStack, LambdaTest] |
| UAT | Business scenarios | Manual | Product + Users | [Manual test cases] |

**Estimated Effort**:

| Test Type | Estimated Hours | Actual Hours | Variance |
|-----------|----------------|--------------|----------|
| Unit Test Creation | [X hours] | [X hours] | [+/- X hours] |
| Integration Test Creation | [X hours] | [X hours] | [+/- X hours] |
| E2E Test Creation | [X hours] | [X hours] | [+/- X hours] |
| Performance Testing | [X hours] | [X hours] | [+/- X hours] |
| Security Testing | [X hours] | [X hours] | [+/- X hours] |
| Manual Testing | [X hours] | [X hours] | [+/- X hours] |
| UAT Coordination | [X hours] | [X hours] | [+/- X hours] |
| **Total** | **[X hours]** | **[X hours]** | **[+/- X hours]** |

---

## Unit Testing

**Unit Test Strategy**: Test individual functions, methods, and classes in isolation.

**Coverage Targets**:
- **Overall Coverage**: ≥80%
- **Critical Modules**: ≥90%
- **Branch Coverage**: ≥75%

**Testing Framework**: [pytest, Jest, JUnit, NUnit, etc.]

**Test Organization**:
```
tests/
├── unit/
│   ├── backend/
│   │   ├── test_module1.py
│   │   ├── test_module2.py
│   │   └── test_utils.py
│   ├── frontend/
│   │   ├── component1.test.js
│   │   └── component2.test.js
│   └── shared/
│       └── test_helpers.py
```

**Unit Test Cases**:

### Module 1: [Module Name]

| Test ID | Test Case | Priority | Status | Owner |
|---------|-----------|----------|--------|-------|
| UT-001 | Test [function] with valid input | P0 | [not-started/in-progress/pass/fail] | @[dev] |
| UT-002 | Test [function] with invalid input | P1 | [status] | @[dev] |
| UT-003 | Test [function] with edge case | P2 | [status] | @[dev] |
| UT-004 | Test error handling in [function] | P1 | [status] | @[dev] |

**Test Case Template**:
```python
def test_[function_name]_[scenario]():
    """
    Test [function] when [condition].
    
    Given: [preconditions]
    When: [action]
    Then: [expected result]
    """
    # Arrange
    input_data = [test data]
    expected_output = [expected result]
    
    # Act
    actual_output = function_under_test(input_data)
    
    # Assert
    assert actual_output == expected_output
```

**Mocking Strategy**:
- Mock external dependencies (databases, APIs, file system)
- Use dependency injection for testability
- Mock time-dependent functions
- Tools: [unittest.mock, pytest-mock, Jest mocks]

**Test Execution**:
```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=agent --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/backend/test_module1.py -v

# Run tests matching pattern
pytest tests/unit/ -k "test_validation" -v
```

**Coverage Requirements by Module**:

| Module | Current Coverage | Target Coverage | Gap | Actions |

|--------|-----------------|-----------------|-----|---------|
| [Module 1] | [X%] | [Target%] | [Gap%] | [Actions to close gap] |
| [Module 2] | [X%] | [Target%] | [Gap%] | [Actions] |
| [Module 3] | [X%] | [Target%] | [Gap%] | [Actions] |

### Pytest Best Practices & Patterns

This section provides comprehensive pytest patterns for easy test code generation.

#### Pytest Project Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── pytest.ini               # Pytest configuration
├── unit/
│   ├── conftest.py         # Unit test fixtures
│   ├── test_module1.py
│   ├── test_module2.py
│   └── test_utils.py
├── integration/
│   ├── conftest.py         # Integration test fixtures
│   ├── test_api.py
│   ├── test_database.py
│   └── test_external_services.py
├── e2e/
│   ├── conftest.py
│   └── test_user_workflows.py
├── fixtures/
│   ├── sample_data.json
│   └── test_files/
└── helpers.py               # Custom assertions and test utilities
```

#### pytest.ini Configuration

```ini
[pytest]
# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Test paths
testpaths = tests

# Minimum Python version
minversion = 3.11

# Default options
addopts = 
    -v                          # Verbose output
    --strict-markers            # Raise error on unknown markers
    --tb=short                  # Shorter traceback format
    --cov=agent                 # Coverage for agent module
    --cov-report=term-missing   # Show missing lines
    --cov-report=html           # Generate HTML coverage
    --cov-fail-under=80         # Fail if coverage < 80%
    -p no:warnings              # Disable warnings summary

# Custom markers for test categorization
markers =
    smoke: Quick smoke tests for critical functionality
    slow: Tests that take more than 1 second
    integration: Integration tests requiring external services
    e2e: End-to-end tests
    unit: Unit tests (fast, isolated)
    security: Security-related tests
    performance: Performance benchmarks
    skip_ci: Skip in CI/CD pipeline
```

#### Root conftest.py (Shared Fixtures)

```python
"""
Shared pytest fixtures for all test types.
Location: tests/conftest.py
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================================
# SESSION-SCOPED FIXTURES (run once per test session)
# ============================================================================

@pytest.fixture(scope="session")
def test_config():
    """
    Test configuration loaded once per session.
    Use for configuration that doesn't change between tests.
    """
    return {
        "api_url": "http://localhost:8000",
        "test_db_url": "sqlite:///test.db",
        "timeout": 30,
        "debug": False
    }


@pytest.fixture(scope="session")
def test_data_dir():
    """Directory containing test data files."""
    return Path(__file__).parent / "fixtures"


# ============================================================================
# MODULE-SCOPED FIXTURES (run once per test module)
# ============================================================================

@pytest.fixture(scope="module")
def database_connection(test_config):
    """
    Database connection shared across module.
    Set up once, torn down once per test file.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(test_config["test_db_url"])
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Setup: Create tables
    from agent.models import Base
    Base.metadata.create_all(engine)
    
    yield session
    
    # Teardown: Drop tables and close connection
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


# ============================================================================
# FUNCTION-SCOPED FIXTURES (run for each test function - default)
# ============================================================================

@pytest.fixture
def clean_database(database_connection):
    """
    Clean database before each test.
    Ensures test isolation.
    """
    # Truncate all tables before test
    from agent.models import User, Post, Comment
    database_connection.query(User).delete()
    database_connection.query(Post).delete()
    database_connection.query(Comment).delete()
    database_connection.commit()
    
    yield database_connection
    
    # Rollback any uncommitted changes after test
    database_connection.rollback()


@pytest.fixture
def sample_user(clean_database):
    """Create a sample user for testing."""
    from agent.models import User
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    clean_database.add(user)
    clean_database.commit()
    clean_database.refresh(user)
    
    return user


@pytest.fixture
def mock_settings(mocker):
    """
    Mock application settings.
    Useful for testing with different configurations.
    """
    mock_config = mocker.MagicMock()
    mock_config.database_url = "sqlite:///test.db"
    mock_config.api_key = "test-api-key"
    mock_config.debug = True
    
    mocker.patch("agent.settings.get_settings", return_value=mock_config)
    return mock_config


@pytest.fixture
def mock_external_api(mocker):
    """
    Mock external API calls.
    Prevents actual HTTP requests during tests.
    """
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "success", "data": {}}
    
    mocker.patch("requests.get", return_value=mock_response)
    mocker.patch("requests.post", return_value=mock_response)
    
    return mock_response


@pytest.fixture
def temp_file(tmp_path):
    """
    Create a temporary file for testing.
    Automatically cleaned up after test.
    """
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Test content")
    return file_path


@pytest.fixture(autouse=True)
def reset_caches():
    """
    Automatically reset caches before each test.
    autouse=True means this runs for every test without explicitly requesting it.
    """
    from agent.cache import cache_manager
    cache_manager.clear()
    yield
    cache_manager.clear()


# ============================================================================
# PARAMETRIZED FIXTURES (fixtures that yield multiple values)
# ============================================================================

@pytest.fixture(params=["user", "admin", "guest"])
def user_role(request):
    """
    Parametrized fixture for testing with different user roles.
    Test function will run 3 times, once for each role.
    """
    return request.param


@pytest.fixture(params=[
    {"valid": True, "email": "user@example.com"},
    {"valid": False, "email": "invalid-email"},
    {"valid": False, "email": ""},
])
def email_test_case(request):
    """Parametrized fixture for email validation tests."""
    return request.param
```

#### Pytest Markers & Test Organization

```python
"""
Example test file: tests/unit/test_authentication.py
"""
import pytest
from agent.auth import authenticate_user, hash_password, verify_password

# ============================================================================
# SMOKE TESTS (critical functionality)
# ============================================================================

@pytest.mark.smoke
@pytest.mark.unit
def test_user_can_login_with_valid_credentials(clean_database, sample_user):
    """
    SMOKE TEST: Verify basic login functionality.
    
    Given: A user exists in the database
    When: User provides correct credentials
    Then: Authentication succeeds
    """
    result = authenticate_user(
        db=clean_database,
        username="testuser",
        password="correct_password"
    )
    
    assert result.success is True
    assert result.user.username == "testuser"


# ============================================================================
# UNIT TESTS (fast, isolated tests)
# ============================================================================

@pytest.mark.unit
class TestPasswordHashing:
    """Group related tests in a class."""
    
    def test_hash_password_returns_hashed_string(self):
        """Password hashing produces a hashed string."""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 20
        assert hashed.startswith("$2b$")  # bcrypt prefix
    
    def test_verify_password_with_correct_password(self):
        """Verify password succeeds with correct password."""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_with_wrong_password(self):
        """Verify password fails with incorrect password."""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        
        assert verify_password("WrongPassword", hashed) is False


# ============================================================================
# PARAMETRIZED TESTS (data-driven tests)
# ============================================================================

@pytest.mark.unit
@pytest.mark.parametrize("password,expected_valid", [
    ("Short1!", False),                    # Too short
    ("NoNumbers!", False),                 # No numbers
    ("nonumbers123", False),               # No special chars
    ("ValidPass123!", True),               # Valid
    ("AnotherGood1@", True),               # Valid
    ("", False),                           # Empty
])
def test_password_validation(password, expected_valid):
    """
    Test password validation with various inputs.
    
    This test runs 6 times with different parameters.
    """
    from agent.auth import validate_password
    
    result = validate_password(password)
    assert result.is_valid == expected_valid


@pytest.mark.unit
@pytest.mark.parametrize("username,email,expected_error", [
    ("user", "user@example.com", None),           # Valid
    ("", "user@example.com", "Username required"), # Missing username
    ("user", "invalid-email", "Invalid email"),   # Invalid email
    ("user", "", "Email required"),                # Missing email
    ("ab", "user@example.com", "Username too short"), # Short username
], ids=[
    "valid_user",
    "missing_username",
    "invalid_email",
    "missing_email",
    "short_username"
])
def test_user_registration_validation(username, email, expected_error):
    """
    Test user registration validation.
    
    Uses 'ids' parameter to give descriptive names to each test case.
    """
    from agent.auth import validate_registration
    
    result = validate_registration(username=username, email=email)
    
    if expected_error:
        assert result.error == expected_error
    else:
        assert result.error is None


# ============================================================================
# MOCKING EXAMPLES
# ============================================================================

@pytest.mark.unit
def test_send_welcome_email_calls_email_service(mocker, sample_user):
    """
    Test that welcome email is sent after registration.
    
    Uses mocker fixture from pytest-mock plugin.
    """
    # Mock the email service
    mock_email_service = mocker.patch("agent.email.send_email")
    
    from agent.auth import send_welcome_email
    send_welcome_email(sample_user)
    
    # Verify email service was called with correct parameters
    mock_email_service.assert_called_once_with(
        to=sample_user.email,
        subject="Welcome to Our App!",
        template="welcome"
    )


@pytest.mark.unit
def test_external_api_integration_with_mock(mocker):
    """Test external API call with mocked response."""
    # Mock requests.get
    mock_response = mocker.MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "success",
        "data": {"user_id": 123}
    }
    mocker.patch("requests.get", return_value=mock_response)
    
    from agent.external import fetch_user_data
    result = fetch_user_data(user_id=123)
    
    assert result["user_id"] == 123


# ============================================================================
# EXCEPTION TESTING
# ============================================================================

@pytest.mark.unit
def test_authenticate_raises_error_for_nonexistent_user(clean_database):
    """Test that authentication raises error for non-existent user."""
    from agent.auth import authenticate_user, UserNotFoundError
    
    with pytest.raises(UserNotFoundError) as exc_info:
        authenticate_user(
            db=clean_database,
            username="nonexistent",
            password="password"
        )
    
    assert "User not found" in str(exc_info.value)


# ============================================================================
# FIXTURES WITH CLEANUP
# ============================================================================

@pytest.fixture
def temp_user_with_posts(clean_database, sample_user):
    """
    Create user with sample posts for testing.
    Automatically cleaned up after test.
    """
    from agent.models import Post
    
    posts = []
    for i in range(3):
        post = Post(
            title=f"Test Post {i}",
            content=f"Content {i}",
            author_id=sample_user.id
        )
        clean_database.add(post)
        posts.append(post)
    
    clean_database.commit()
    
    yield sample_user, posts
    
    # Cleanup happens automatically via clean_database fixture
```

#### Custom Assertions & Test Helpers

```python
"""
Custom pytest helpers and assertions.
Location: tests/helpers.py
"""
import pytest
from typing import Any, Dict, List


def assert_response_success(response, expected_status=200):
    """
    Helper to assert successful API response.
    
    Usage:
        response = client.get('/api/users')
        assert_response_success(response)
    """
    assert response.status_code == expected_status, \
        f"Expected {expected_status}, got {response.status_code}: {response.text}"
    
    data = response.json()
    assert "error" not in data or data["error"] is None


def assert_dict_contains(actual: Dict, expected: Dict):
    """
    Assert that actual dict contains all keys/values from expected.
    
    Usage:
        assert_dict_contains(
            actual={"id": 1, "name": "John", "email": "john@example.com"},
            expected={"name": "John", "email": "john@example.com"}
        )
    """
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in {actual.keys()}"
        assert actual[key] == value, \
            f"Expected {key}={value}, got {actual[key]}"


@pytest.fixture
def assert_no_errors_logged(caplog):
    """
    Fixture that fails test if any errors were logged.
    
    Usage:
        def test_something(assert_no_errors_logged):
            # test code
            pass  # Test will fail if any errors logged
    """
    yield
    
    errors = [record for record in caplog.records if record.levelname == "ERROR"]
    assert len(errors) == 0, f"Errors logged: {[e.message for e in errors]}"
```

#### Running Pytest Tests

```bash
# ============================================================================
# BASIC TEST EXECUTION
# ============================================================================

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run tests in specific directory
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_authentication.py

# Run specific test function
pytest tests/unit/test_authentication.py::test_user_can_login

# Run specific test class
pytest tests/unit/test_authentication.py::TestPasswordHashing

# ============================================================================
# FILTERING TESTS BY MARKERS
# ============================================================================

# Run only smoke tests
pytest -m smoke

# Run only unit tests
pytest -m unit

# Run all except slow tests
pytest -m "not slow"

# Run smoke AND unit tests
pytest -m "smoke and unit"

# ============================================================================
# COVERAGE REPORTING
# ============================================================================

# Run with coverage
pytest --cov=agent

# Coverage with missing lines
pytest --cov=agent --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=agent --cov-report=html
# Open: htmlcov/index.html

# Fail if coverage below threshold
pytest --cov=agent --cov-fail-under=80

# ============================================================================
# PARALLEL EXECUTION (requires pytest-xdist)
# ============================================================================

# Run tests in parallel (auto-detect CPU count)
pytest -n auto

# Run tests on 4 workers
pytest -n 4

# ============================================================================
# OUTPUT CONTROL
# ============================================================================

# Show print statements
pytest -s

# Stop after first failure
pytest -x

# Show slowest 10 tests
pytest --durations=10

# ============================================================================
# RERUN FAILED TESTS
# ============================================================================

# Run only failed tests from last run
pytest --lf   # or --last-failed

# Run failed tests first, then others
pytest --ff   # or --failed-first

# ============================================================================
# CI/CD OPTIMIZED COMMAND
# ============================================================================

pytest \
  -v \
  --tb=short \
  --cov=agent \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-report=xml \
  --cov-fail-under=80 \
  --junitxml=junit.xml \
  -n auto \
  -m "not slow"
```

#### Pytest Plugins & Extensions

```bash
# requirements-test.txt

pytest>=7.4.0                 # Core pytest framework
pytest-cov>=4.1.0             # Coverage reporting
pytest-mock>=3.11.1           # Mocking support
pytest-xdist>=3.3.1           # Parallel test execution
pytest-timeout>=2.1.0         # Timeout for long-running tests
pytest-asyncio>=0.21.1        # Async test support
pytest-benchmark>=4.0.0       # Performance benchmarking
pytest-html>=3.2.0            # HTML test reports
pytest-json-report>=1.5.0     # JSON test reports
pytest-random-order>=1.1.0    # Randomize test order
freezegun>=1.2.2              # Mock datetime
faker>=19.6.0                 # Generate fake test data
responses>=0.23.3             # Mock HTTP responses
```

---

## Integration Testing

**Integration Test Strategy**: Test interactions between components, services, and systems.

**Integration Scope**:
- API endpoint testing
- Database operations
- Service-to-service communication
- External API integrations
- Message queue interactions

**Testing Framework**: [Supertest, pytest + requests, Postman/Newman, REST Assured]

**API Test Cases**:

### Endpoint: [Method] /api/v1/[resource]

| Test ID | Test Case | Priority | Status | Owner |

|---------|-----------|----------|--------|-------|
| IT-001 | POST valid data returns 201 | P0 | [not-started/in-progress/pass/fail] | @[qa] |
| IT-002 | POST invalid data returns 400 | P1 | [status] | @[qa] |
| IT-003 | GET with valid ID returns 200 | P0 | [status] | @[qa] |
| IT-004 | GET with invalid ID returns 404 | P1 | [status] | @[qa] |
| IT-005 | PUT updates resource returns 200 | P0 | [status] | @[qa] |
| IT-006 | DELETE removes resource returns 204 | P0 | [status] | @[qa] |
| IT-007 | Unauthorized access returns 401 | P1 | [status] | @[qa] |
| IT-008 | Rate limiting returns 429 | P2 | [status] | @[qa] |

**Test Case Example**:
```javascript
describe('POST /api/v1/users', () => {
  it('should create user with valid data', async () => {
    const userData = {
      name: 'Test User',
      email: 'test@example.com',
      password: 'SecurePass123!'
    };
    
    const response = await request(app)
      .post('/api/v1/users')
      .send(userData)
      .expect(201);
    
    expect(response.body).toHaveProperty('id');
    expect(response.body.name).toBe(userData.name);
    expect(response.body.email).toBe(userData.email);
    expect(response.body).not.toHaveProperty('password');
  });
  
  it('should return 400 for invalid email', async () => {
    const userData = {
      name: 'Test User',
      email: 'invalid-email',
      password: 'SecurePass123!'
    };
    
    const response = await request(app)
      .post('/api/v1/users')
      .send(userData)
      .expect(400);
    
    expect(response.body.error).toContain('Invalid email');
  });
});
```

**Database Integration Tests**:

| Test ID | Test Case | Priority | Status |

|---------|-----------|----------|--------|
| DB-001 | Create record and verify in database | P0 | [status] |
| DB-002 | Update record and verify changes | P0 | [status] |
| DB-003 | Delete record and verify removal | P0 | [status] |
| DB-004 | Query with filters returns correct results | P1 | [status] |
| DB-005 | Transaction rollback on error | P1 | [status] |
| DB-006 | Unique constraint violation handling | P1 | [status] |

**External Integration Tests**:

| Integration | Test Cases | Priority | Status |

|-------------|------------|----------|--------|
| [Third-party API 1] | Authentication, data fetch, error handling | P1 | [status] |
| [Payment Gateway] | Charge, refund, webhook handling | P0 | [status] |
| [Email Service] | Send email, template rendering | P2 | [status] |

**Test Execution**:
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run API tests
pytest tests/integration/test_api.py -v

# Run with test database
TEST_DATABASE=true pytest tests/integration/ -v
```

---

## End-to-End Testing

**E2E Test Strategy**: Test complete user workflows from start to finish in a production-like environment.

**Testing Framework**: [Cypress, Playwright, Selenium WebDriver, TestCafe]

**Test Environment**: [Staging environment mirroring production]

**Critical User Workflows**:

### Workflow 1: [User Registration and Login]

| Test ID | Test Step | Expected Result | Status |

|---------|-----------|----------------|--------|
| E2E-001 | Navigate to registration page | Registration form displayed | [status] |
| E2E-002 | Fill valid registration data | Form accepts input | [status] |
| E2E-003 | Submit registration | Success message, email sent | [status] |
| E2E-004 | Verify email and activate account | Account activated | [status] |
| E2E-005 | Login with credentials | Dashboard displayed | [status] |

### Workflow 2: [Core Feature Usage]

| Test ID | Test Step | Expected Result | Status |

|---------|-----------|----------------|--------|
| E2E-010 | User navigates to [feature] | Feature page loads | [status] |
| E2E-011 | User creates new [item] | Item created successfully | [status] |
| E2E-012 | User edits [item] | Changes saved | [status] |
| E2E-013 | User deletes [item] | Item removed | [status] |

**Test Case Example** (Cypress):
```javascript
describe('User Registration Flow', () => {
  it('should register new user and login', () => {
    // Visit registration page
    cy.visit('/register');
    
    // Fill registration form
    cy.get('[data-testid="name-input"]').type('John Doe');
    cy.get('[data-testid="email-input"]').type('john@example.com');
    cy.get('[data-testid="password-input"]').type('SecurePass123!');
    cy.get('[data-testid="confirm-password-input"]').type('SecurePass123!');
    
    // Submit form
    cy.get('[data-testid="register-button"]').click();
    
    // Verify success
    cy.get('[data-testid="success-message"]').should('be.visible');
    cy.url().should('include', '/verify-email');
    
    // Simulate email verification (in test environment)
    cy.task('verifyEmail', 'john@example.com');
    
    // Login
    cy.visit('/login');
    cy.get('[data-testid="email-input"]').type('john@example.com');
    cy.get('[data-testid="password-input"]').type('SecurePass123!');
    cy.get('[data-testid="login-button"]').click();
    
    // Verify dashboard
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="user-name"]').should('contain', 'John Doe');
  });
});
```

**E2E Test Scenarios**:

| Scenario | Priority | Frequency | Status |

|----------|----------|-----------|--------|
| Happy path: User completes main workflow | P0 | Every build | [status] |
| Error handling: Invalid input rejected | P1 | Daily | [status] |
| Edge case: Concurrent users | P2 | Pre-release | [status] |
| Mobile responsive: Core features on mobile | P1 | Pre-release | [status] |

**Test Execution**:
```bash
# Run all E2E tests
npx cypress run

# Run in headed mode (see browser)
npx cypress open

# Run specific test suite
npx cypress run --spec "cypress/e2e/user-registration.cy.js"

# Run on different browser
npx cypress run --browser chrome
npx cypress run --browser firefox
```

---

## Performance Testing

**Performance Test Strategy**: Validate system performance under various load conditions.

**Testing Framework**: [JMeter, k6, Gatling, Locust]

**Performance Targets**:

| Metric | Target | Measurement Point | Tools |

|--------|--------|------------------|-------|
| Response Time (P50) | < 200ms | API endpoints | [APM tool] |
| Response Time (P95) | < 500ms | API endpoints | [APM tool] |
| Response Time (P99) | < 1000ms | API endpoints | [APM tool] |
| Throughput | ≥ [X req/sec] | Load balancer | [Load testing tool] |
| Page Load Time | < 3 seconds | Frontend | Lighthouse |
| Time to Interactive | < 5 seconds | Frontend | Lighthouse |
| Concurrent Users | ≥ [X users] | Full system | [Load testing tool] |
| Database Query Time (P95) | < 100ms | Database | [DB monitoring] |
| CPU Utilization | < 70% | Application servers | [Monitoring tool] |
| Memory Usage | < 80% | Application servers | [Monitoring tool] |

**Test Scenarios**:

### Load Testing (Normal Traffic)
**Objective**: Verify system handles expected load

| Test ID | Scenario | Users | Duration | Pass Criteria |

|---------|----------|-------|----------|--------------|
| PERF-001 | Average daily traffic | [X concurrent] | 30 min | Response time targets met |
| PERF-002 | Peak hour traffic | [Y concurrent] | 15 min | Response time targets met |
| PERF-003 | Sustained load | [X concurrent] | 2 hours | No memory leaks, stable performance |

### Stress Testing (Beyond Normal)
**Objective**: Find breaking point and verify graceful degradation

| Test ID | Scenario | Users | Duration | Pass Criteria |

|---------|----------|-------|----------|--------------|
| PERF-010 | Gradual load increase | 0 → [2X] | 30 min | System remains responsive, no crashes |
| PERF-011 | Beyond capacity | [3X concurrent] | 10 min | Graceful degradation, meaningful errors |

### Spike Testing (Sudden Load Increase)
**Objective**: Verify system handles sudden traffic spikes

| Test ID | Scenario | Users | Duration | Pass Criteria |

|---------|----------|-------|----------|--------------|
| PERF-020 | Traffic spike | 0 → [2X] instantly | 5 min | System recovers, no data loss |
| PERF-021 | Flash sale simulation | [3X] for 2 min | 5 min | Key features remain available |

### Endurance Testing (Soak Testing)
**Objective**: Verify system stability over extended period

| Test ID | Scenario | Users | Duration | Pass Criteria |

|---------|----------|-------|----------|--------------|
| PERF-030 | Extended operation | [X concurrent] | 8 hours | No memory leaks, consistent performance |

**Test Script Example** (k6):
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Ramp up to 200 users
    { duration: '5m', target: 200 },  // Stay at 200 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'],  // 95% of requests under 500ms
    'http_req_failed': ['rate<0.01'],    // Error rate under 1%
  },
};

export default function () {
  // Test API endpoint
  let response = http.get('https://api.example.com/v1/users');
  
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  sleep(1);  // Wait 1 second between iterations
}
```

**Test Execution**:
```bash
# Run load test
k6 run load-test.js

# Run with custom parameters
k6 run --vus 100 --duration 30s load-test.js

# Run and send results to monitoring
k6 run --out influxdb=http://localhost:8086 load-test.js
```

**Performance Benchmarking**:

| Endpoint | Current P95 | Target P95 | Status | Notes |

|----------|------------|-----------|--------|-------|
| GET /api/v1/users | [X ms] | < 200ms | [Pass/Fail] | [Notes] |
| POST /api/v1/users | [X ms] | < 500ms | [Pass/Fail] | [Notes] |
| GET /api/v1/data | [X ms] | < 300ms | [Pass/Fail] | [Notes] |

---

## Security Testing

**Security Test Strategy**: Identify and validate security controls to protect against vulnerabilities.

**Testing Framework**: [OWASP ZAP, Burp Suite, Snyk, Bandit, npm audit]

**Security Test Categories**:

### 1. OWASP Top 10 Testing

| OWASP Risk | Test Cases | Priority | Status | Tools |

|------------|------------|----------|--------|-------|
| A01: Broken Access Control | Test unauthorized access, privilege escalation | P0 | [status] | [Manual + OWASP ZAP] |
| A02: Cryptographic Failures | Test data encryption, secure storage | P0 | [status] | [Code review + tools] |
| A03: Injection | SQL injection, command injection, XSS | P0 | [status] | [OWASP ZAP, Burp Suite] |
| A04: Insecure Design | Architecture review, threat modeling | P1 | [status] | [Manual review] |
| A05: Security Misconfiguration | Default credentials, unnecessary features | P1 | [status] | [Config scanning] |
| A06: Vulnerable Components | Dependency scanning, outdated libraries | P0 | [status] | [Snyk, npm audit] |
| A07: Authentication Failures | Weak passwords, session management | P0 | [status] | [Manual + automated] |
| A08: Software & Data Integrity | Code integrity, supply chain security | P1 | [status] | [SCA tools] |
| A09: Logging & Monitoring | Security event logging, alerting | P2 | [status] | [Manual review] |
| A10: Server-Side Request Forgery | SSRF testing | P1 | [status] | [Manual testing] |

### 2. Vulnerability Scanning

| Test ID | Test Case | Priority | Status |

|---------|-----------|----------|--------|
| SEC-001 | Scan for known CVEs in dependencies | P0 | [status] |
| SEC-002 | Static code analysis for security issues | P0 | [status] |
| SEC-003 | Dynamic application security testing (DAST) | P1 | [status] |
| SEC-004 | Secrets scanning (no hardcoded credentials) | P0 | [status] |

### 3. Authentication & Authorization Testing

| Test ID | Test Case | Expected Result | Status |

|---------|-----------|----------------|--------|
| AUTH-001 | Login with valid credentials | Access granted | [status] |
| AUTH-002 | Login with invalid credentials | Access denied | [status] |
| AUTH-003 | Access protected resource without token | 401 Unauthorized | [status] |
| AUTH-004 | Access resource with expired token | 401 Unauthorized | [status] |
| AUTH-005 | User A tries to access User B's data | 403 Forbidden | [status] |
| AUTH-006 | Regular user tries admin function | 403 Forbidden | [status] |
| AUTH-007 | SQL injection in login form | Injection blocked | [status] |
| AUTH-008 | Brute force attack (rate limiting) | 429 Too Many Requests | [status] |

### 4. Input Validation Testing

| Test ID | Test Case | Expected Result | Status |

|---------|-----------|----------------|--------|
| VAL-001 | XSS attempt in text field | Input sanitized/escaped | [status] |
| VAL-002 | SQL injection in search | Query parameterized, safe | [status] |
| VAL-003 | File upload with malicious file | File rejected/sanitized | [status] |
| VAL-004 | Oversized input (DOS attempt) | Request rejected | [status] |
| VAL-005 | Special characters in input | Properly escaped | [status] |

**Test Execution**:
```bash
# Run dependency vulnerability scan
npm audit
snyk test

# Run static analysis security scan
bandit -r agent/ -f json -o tests/bandit_report.json

# Run OWASP ZAP baseline scan
docker run -v $(pwd):/zap/wrk/:rw -t owasp/zap2docker-stable zap-baseline.py \
  -t https://staging.example.com -r zap-report.html

# Run secrets detection
trufflehog filesystem . --json
```

**Security Test Results**:

| Severity | Count | Status | Actions |

|----------|-------|--------|---------|
| Critical | [X] | [Open/Resolved] | [Action items] |
| High | [X] | [Open/Resolved] | [Action items] |
| Medium | [X] | [Open/Resolved] | [Action items] |
| Low | [X] | [Open/Resolved] | [Action items] |

**Security Acceptance Criteria**:
- [ ] Zero critical vulnerabilities
- [ ] Zero high vulnerabilities (or documented exceptions)
- [ ] All medium vulnerabilities reviewed and accepted/fixed
- [ ] Dependency scanning shows no known CVEs
- [ ] OWASP Top 10 tests all pass
- [ ] Penetration test report reviewed and issues addressed

---

## Accessibility Testing

**Accessibility Test Strategy**: Ensure application is usable by people with disabilities.

**Standards Compliance**: WCAG 2.1 Level AA

**Testing Tools**:
- **Automated**: axe DevTools, Lighthouse, WAVE, Pa11y
- **Manual**: Keyboard navigation, screen reader (NVDA, JAWS, VoiceOver)
- **Browser Extensions**: axe DevTools, WAVE

**Accessibility Test Cases**:

| Test ID | Test Case | WCAG Criteria | Priority | Status |

|---------|-----------|---------------|----------|--------|
| A11Y-001 | All images have alt text | 1.1.1 Non-text Content | P0 | [status] |
| A11Y-002 | Color contrast ratio ≥ 4.5:1 | 1.4.3 Contrast (Minimum) | P0 | [status] |
| A11Y-003 | All functionality keyboard accessible | 2.1.1 Keyboard | P0 | [status] |
| A11Y-004 | No keyboard trap | 2.1.2 No Keyboard Trap | P0 | [status] |
| A11Y-005 | Forms have labels | 3.3.2 Labels or Instructions | P0 | [status] |
| A11Y-006 | Heading hierarchy correct (h1→h2→h3) | 1.3.1 Info and Relationships | P1 | [status] |
| A11Y-007 | Links descriptive (not "click here") | 2.4.4 Link Purpose | P1 | [status] |
| A11Y-008 | Page title describes content | 2.4.2 Page Titled | P1 | [status] |
| A11Y-009 | ARIA landmarks used correctly | 1.3.1 Info and Relationships | P2 | [status] |
| A11Y-010 | Screen reader reads content correctly | Multiple | P1 | [status] |

**Keyboard Navigation Test**:
- [ ] Tab through all interactive elements in logical order
- [ ] Shift+Tab moves backward through elements
- [ ] Enter/Space activates buttons and links
- [ ] Escape closes modals and dropdowns
- [ ] Arrow keys navigate lists and menus
- [ ] Focus indicator always visible

**Screen Reader Test** (NVDA/JAWS/VoiceOver):
- [ ] Page title announced on load
- [ ] Headings announced with level (h1, h2, etc.)
- [ ] Links announced with descriptive text
- [ ] Form fields announced with labels
- [ ] Error messages announced
- [ ] Dynamic content changes announced

**Test Execution**:
```bash
# Run automated accessibility tests
npm run test:a11y

# Run Lighthouse accessibility audit
lighthouse https://staging.example.com --only-categories=accessibility

# Run Pa11y CI
pa11y-ci
```

**Accessibility Score Target**: ≥95/100 (Lighthouse)

---

## Compatibility Testing

**Compatibility Test Strategy**: Verify application works across different browsers, devices, and operating systems.

**Browser Compatibility Matrix**:

| Browser | Version | Priority | Status | Notes |

|---------|---------|----------|--------|-------|
| Chrome | Latest 2 | P0 | [status] | [Issues found] |
| Firefox | Latest 2 | P0 | [status] | [Issues found] |
| Safari | Latest 2 | P0 | [status] | [Issues found] |
| Edge | Latest 2 | P0 | [status] | [Issues found] |
| Chrome (Mobile) | Latest | P1 | [status] | [Issues found] |
| Safari (iOS) | Latest 2 | P1 | [status] | [Issues found] |

**Device Compatibility**:

| Device Type | Screen Sizes | Priority | Status |

|-------------|-------------|----------|--------|
| Desktop | 1920x1080, 1366x768 | P0 | [status] |
| Tablet | 1024x768, 768x1024 | P1 | [status] |
| Mobile | 375x667, 414x896 | P0 | [status] |

**Operating System Compatibility**:

| OS | Version | Priority | Status |

|----|---------|----------|--------|
| Windows | 10, 11 | P0 | [status] |
| macOS | 11+, 12+ | P1 | [status] |
| iOS | 14+, 15+ | P1 | [status] |
| Android | 10+, 11+ | P1 | [status] |

**Responsive Design Test**:
- [ ] Layout adapts correctly to different screen sizes
- [ ] Navigation menu works on mobile (hamburger menu)
- [ ] Touch targets minimum 44x44 pixels
- [ ] Text readable without zooming
- [ ] No horizontal scrolling on mobile
- [ ] Images scale appropriately

**Test Execution**:
```bash
# Use BrowserStack/LambdaTest for cross-browser testing
# Or use local browser testing with Playwright

# Run tests on multiple browsers (Playwright)
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

---

## User Acceptance Testing (UAT)

**UAT Strategy**: Validate that solution meets business requirements and user needs.

**UAT Participants**:

| Name | Role | Responsibilities |

|------|------|------------------|
| @[username] | Product Owner | Define acceptance criteria, final sign-off |
| @[username] | Business Analyst | Facilitate UAT, track issues |
| @[username] | End User 1 | Execute test scenarios, provide feedback |
| @[username] | End User 2 | Execute test scenarios, provide feedback |

**UAT Environment**: [Staging environment with production-like data]

**UAT Test Scenarios**:

| Scenario ID | Scenario Description | Priority | Expected Outcome | Status | Tester | Notes |

|-------------|---------------------|----------|------------------|--------|--------|-------|
| UAT-001 | [End-to-end workflow 1] | P0 | [Expected result] | [not-started/in-progress/pass/fail] | @[user] | [Comments] |
| UAT-002 | [End-to-end workflow 2] | P0 | [Expected result] | [status] | @[user] | [Comments] |
| UAT-003 | [Edge case scenario] | P1 | [Expected result] | [status] | @[user] | [Comments] |

**UAT Schedule**:
- **Preparation**: [Start date] - [End date]
- **UAT Execution**: [Start date] - [End date] ([X days])
- **Issue Resolution**: [Start date] - [End date]
- **Re-testing**: [Start date] - [End date]
- **Sign-off**: [Target date]

**UAT Acceptance Criteria**:
- [ ] ≥95% of test scenarios pass
- [ ] All P0 and P1 defects resolved
- [ ] User satisfaction score ≥ [4/5]
- [ ] Product Owner provides written sign-off

**UAT Feedback Template**:
```
Scenario: [ID and description]
Tester: [Name]
Date: [YYYY-MM-DD]
Result: [Pass/Fail]

Steps Executed:
1. [Step 1]
2. [Step 2]
3. [Step 3]

Expected Result: [What should happen]
Actual Result: [What actually happened]

Issues Found: [List any issues]
Suggestions: [Any improvement suggestions]
Overall Satisfaction: [1-5 rating]
```

---

## Regression Testing

**Regression Test Strategy**: Ensure existing functionality not broken by new changes.

**Regression Test Suite**:
- **Full Regression**: All tests across all modules (Pre-release)
- **Partial Regression**: Affected areas + critical paths (Per sprint)
- **Smoke Tests**: Critical functionality only (Daily builds)

**Regression Test Selection**:

| Module | Test Cases | Frequency | Automation | Owner |

|--------|------------|-----------|------------|-------|
| Authentication | [X tests] | Every build | 100% | @[qa] |
| Core Feature 1 | [X tests] | Every build | 100% | @[qa] |
| Core Feature 2 | [X tests] | Weekly | 80% | @[qa] |
| Admin Features | [X tests] | Pre-release | 50% | @[qa] |

**Regression Test Cases**:

| Test ID | Module | Test Case | Priority | Status |

|---------|--------|-----------|----------|--------|
| REG-001 | Auth | User can login | P0 | [pass/fail] |
| REG-002 | Auth | User can logout | P0 | [pass/fail] |
| REG-003 | [Feature] | [Critical functionality] | P0 | [pass/fail] |
| REG-004 | [Feature] | [Important functionality] | P1 | [pass/fail] |

**Test Execution**:
```bash
# Run full regression suite
pytest tests/ -m regression -v

# Run smoke tests only
pytest tests/ -m smoke -v

# Run regression for specific module
pytest tests/test_authentication.py -v
```

**Regression Metrics**:

| Sprint/Release | Tests Run | Pass | Fail | Pass Rate | Defects Found |

|----------------|-----------|------|------|-----------|---------------|
| Sprint 1 | [X] | [X] | [X] | [X%] | [X] |
| Sprint 2 | [X] | [X] | [X] | [X%] | [X] |
| Release 1.0 | [X] | [X] | [X] | [X%] | [X] |

---

## Test Environment

**Environment Configuration**:

| Environment | Purpose | URL | Database | Test Data | Access |

|-------------|---------|-----|----------|-----------|--------|
| Local Dev | Developer testing | localhost:8000 | Local SQLite | Synthetic | All devs |
| Dev | Integration testing | dev.example.com | Dev DB | Synthetic | Dev team |
| QA/Test | QA testing | test.example.com | Test DB | Sanitized prod | QA + Dev |
| Staging | UAT, pre-prod validation | staging.example.com | Staging DB | Prod-like | All teams |
| Production | Live environment | example.com | Prod DB | Real data | Ops only |

**Environment Setup**:
```bash
# Set up local test environment
./setup-test-env.sh

# Run tests against specific environment
TEST_ENV=dev pytest tests/
TEST_ENV=staging pytest tests/
```

**Infrastructure Requirements**:

| Component | Specification | Purpose |

|-----------|--------------|---------|
| Web Server | [Specs] | Host application |
| Database | [Specs] | Data storage |
| Cache | Redis 6.x | Session/query cache |
| Message Queue | RabbitMQ | Async processing |

**Test Data Requirements**:
- User accounts with different roles (admin, user, guest)
- Sample data covering all scenarios
- Edge case data (boundary values, special characters)
- Large datasets for performance testing

---

## Test Data Management

**Test Data Strategy**: Manage creation, maintenance, and cleanup of test data.

**Data Categories**:

| Category | Source | Refresh Frequency | Compliance |

|----------|--------|-------------------|------------|
| User Data | Synthetic generation | Weekly | No PII |
| Business Data | Sanitized production | Daily | Anonymized |
| Test Fixtures | Manually created | As needed | Safe for all envs |
| Performance Data | Generated scripts | Pre-test run | Ephemeral |

**Data Creation Scripts**:
```bash
# Generate test users
python scripts/generate_test_users.py --count 100

# Load sample data
python scripts/load_sample_data.py --dataset small

# Generate large dataset for performance testing
python scripts/generate_perf_data.py --records 100000
```

**Data Privacy & Compliance**:
- ✅ No production PII in test environments
- ✅ All test data anonymized/synthetic
- ✅ Data access logged and audited
- ✅ Test data deleted after use (ephemeral)

**Data Cleanup**:
```bash
# Clean up test data after test run
pytest tests/ --cleanup-after

# Reset database to known state
python scripts/reset_test_db.py
```

---

## Test Execution Schedule

**Testing Timeline**:

| Week | Testing Activities | Owner | Deliverables |

|------|-------------------|-------|--------------|
| 1 | Test planning, test case creation | QA | Test plan, test cases |
| 2-3 | Unit testing, integration testing | Dev + QA | Test results, coverage reports |
| 4 | E2E testing, performance testing | QA | E2E results, performance report |
| 5 | Security testing, accessibility testing | QA + Security | Security report, a11y report |
| 6 | UAT, regression testing | QA + Users | UAT sign-off, regression results |
| 7 | Bug fixes, re-testing | Dev + QA | Final test report |
| 8 | Production validation | QA + Ops | Go-live sign-off |

**Daily Test Execution**:
- **CI/CD Pipeline**: Automated tests run on every commit
    - Unit tests: ~5 minutes
    - Integration tests: ~15 minutes
    - Smoke tests: ~10 minutes
- **Manual Testing**: [X hours/day during sprint]
- **Exploratory Testing**: [X hours/week]

**Test Status Tracking**:

| Test Type | Total | Executed | Passed | Failed | Blocked | Pass Rate |

|-----------|-------|----------|--------|--------|---------|-----------|
| Unit | [X] | [X] | [X] | [X] | [X] | [X%] |
| Integration | [X] | [X] | [X] | [X] | [X] | [X%] |
| E2E | [X] | [X] | [X] | [X] | [X] | [X%] |
| Performance | [X] | [X] | [X] | [X] | [X] | [X%] |
| Security | [X] | [X] | [X] | [X] | [X] | [X%] |
| UAT | [X] | [X] | [X] | [X] | [X] | [X%] |
| **Total** | **[X]** | **[X]** | **[X]** | **[X]** | **[X]** | **[X%]** |

---

## Defect Management

**Defect Tracking System**: [JIRA, Azure DevOps, GitHub Issues]

**Defect Severity Levels**:

| Severity | Definition | Response Time | Resolution SLA |

|----------|------------|---------------|----------------|
| **P0 - Critical** | System down, data loss, security breach | 15 minutes | 4 hours |
| **P1 - High** | Major feature broken, workaround exists | 1 hour | 1 business day |
| **P2 - Medium** | Minor feature broken, cosmetic issues | 4 hours | 1 week |
| **P3 - Low** | Enhancement, nice-to-have | 1 business day | Backlog |

**Defect Workflow**:
```
New → Assigned → In Progress → Fixed → Ready for Retest → Verified → Closed
                                    ↓ (if still broken)
                                Reopened
```

**Defect Report Template**:
```
**Defect ID**: [DEF-XXX]
**Summary**: [One-line description]
**Severity**: [P0/P1/P2/P3]
**Status**: [New/In Progress/Fixed/Verified/Closed]
**Found in**: [Version/Build]
**Assigned to**: @[developer]
**Reporter**: @[tester]
**Date Reported**: [YYYY-MM-DD]

**Description**: [Detailed description of the issue]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**: [What should happen]
**Actual Result**: [What actually happens]

**Environment**: [Browser, OS, device]
**Test Data**: [Any specific data used]
**Screenshots/Logs**: [Attach evidence]

**Workaround** (if exists): [Describe workaround]
```

**Defect Metrics**:

| Metric | Value | Trend |

|--------|-------|-------|
| Total Defects Found | [X] | [↑/↓/→] |
| Open Defects | [X] | [↑/↓/→] |
| Critical/High Defects | [X] | [↑/↓/→] |
| Defect Resolution Rate | [X%] | [↑/↓/→] |
| Defect Leakage to Production | [X] | [↓] |
| Mean Time to Resolution | [X hours] | [↓] |

**Defect Summary**:

| Severity | New | In Progress | Fixed | Verified | Closed | Total |

|----------|-----|-------------|-------|----------|--------|-------|
| P0 | [X] | [X] | [X] | [X] | [X] | [X] |
| P1 | [X] | [X] | [X] | [X] | [X] | [X] |
| P2 | [X] | [X] | [X] | [X] | [X] | [X] |
| P3 | [X] | [X] | [X] | [X] | [X] | [X] |
| **Total** | **[X]** | **[X]** | **[X]** | **[X]** | **[X]** | **[X]** |

---

## Test Metrics & Reporting

**Key Performance Indicators (KPIs)**:

| KPI | Target | Current | Status |

|-----|--------|---------|--------|
| Test Coverage (Unit) | ≥80% | [X%] | [🟢/🟡/🔴] |
| Test Coverage (Integration) | ≥70% | [X%] | [🟢/🟡/🔴] |
| Test Execution Rate | 100% | [X%] | [🟢/🟡/🔴] |
| Test Pass Rate | ≥95% | [X%] | [🟢/🟡/🔴] |
| Defect Detection Rate | [Baseline] | [X] | [↑/↓/→] |
| Defect Resolution Time | < 2 days | [X days] | [🟢/🟡/🔴] |
| Automation Coverage | ≥80% | [X%] | [🟢/🟡/🔴] |

**Test Execution Summary**:

| Sprint/Release | Tests Executed | Pass | Fail | Blocked | Pass Rate | Coverage |

|----------------|----------------|------|------|---------|-----------|----------|
| Sprint 1 | [X] | [X] | [X] | [X] | [X%] | [X%] |
| Sprint 2 | [X] | [X] | [X] | [X] | [X%] | [X%] |
| Release 1.0 | [X] | [X] | [X] | [X] | [X%] | [X%] |

**Test Coverage Report**:

| Module | Lines of Code | Covered | Coverage % | Branches | Branch Coverage % |

|--------|--------------|---------|------------|----------|-------------------|
| Module 1 | [X] | [X] | [X%] | [X] | [X%] |
| Module 2 | [X] | [X] | [X%] | [X] | [X%] |
| Module 3 | [X] | [X] | [X%] | [X] | [X%] |
| **Total** | **[X]** | **[X]** | **[X%]** | **[X]** | **[X%]** |

**Reporting Schedule**:
- **Daily**: Test execution status (to team via standup)
- **Weekly**: Test progress report (to stakeholders via email)
- **Sprint End**: Comprehensive test summary (to all stakeholders)
- **Release**: Final test report (formal document)

**Test Report Template**:
```
# Test Report: [Sprint/Release Name]
Date: [YYYY-MM-DD]
Prepared by: @[QA Lead]

## Executive Summary
[High-level summary of testing outcomes, key findings, and go/no-go recommendation]

## Test Execution Summary
- Tests Executed: [X]
- Pass: [X] ([X%])
- Fail: [X] ([X%])
- Blocked: [X] ([X%])

## Coverage
- Unit Test Coverage: [X%]
- Integration Test Coverage: [X%]
- E2E Test Coverage: [Critical paths covered]

## Defects
- Total Defects: [X]
- Critical/High: [X] ([X] open)
- Medium/Low: [X]

## Risks & Issues
[List any risks, blockers, or concerns]

## Recommendations
[Recommendations for next steps or areas needing attention]

## Go-Live Recommendation
[Go / No-Go with justification]
```

---

## Risk Assessment

**Testing Risks**:

| Risk | Probability | Impact | Mitigation | Contingency |

|------|-------------|--------|------------|-------------|
| Insufficient test coverage | Medium | High | Focus on critical paths, automated tests | Manual exploratory testing |
| Test environment instability | Medium | Medium | Regular env health checks, quick restore | Backup environment ready |
| Delayed feature delivery | High | Medium | Continuous testing, early feedback | Adjust test scope |
| Resource constraints (testers) | Medium | Medium | Automate more tests, prioritize | Outsource testing |
| Test data unavailable | Low | High | Prepare test data early | Generate synthetic data |
| Production-like env differences | Medium | High | Mirror prod configs, regular sync | Production-like staging |

**Technical Risks**:

| Risk | Description | Mitigation |

|------|-------------|------------|
| Flaky tests | Tests fail intermittently | Identify and fix root cause, retry logic |
| Test execution time | Tests take too long | Parallelize tests, optimize slow tests |
| Test maintenance | High effort to maintain tests | Refactor brittle tests, page object pattern |

---

## Test Deliverables

**Testing Artifacts**:

| Deliverable | Description | Owner | Status | Location |

|-------------|-------------|-------|--------|----------|
| Test Plan | This document | @[QA Lead] | [Complete] | [Link] |
| Test Cases | Detailed test scenarios | @[QA] | [In Progress] | [Link] |
| Test Scripts | Automated test code | @[Dev/QA] | [In Progress] | [tests/ directory] |
| Test Data | Datasets for testing | @[QA] | [Complete] | [tests/data/] |
| Test Reports | Execution results, coverage | @[QA] | [Ongoing] | [reports/] |
| Defect Reports | Bug tracking | @[QA] | [Ongoing] | [JIRA] |
| UAT Sign-off | Stakeholder approval | @[Product Owner] | [Pending] | [Link] |

---

## Entry & Exit Criteria

**Entry Criteria** (Before testing starts):
- [ ] Requirements documented and approved
- [ ] Test plan reviewed and approved
- [ ] Test cases created and reviewed
- [ ] Test environment set up and validated
- [ ] Test data prepared
- [ ] Feature implementation complete
- [ ] Code review passed
- [ ] Build deployed to test environment
- [ ] Smoke tests passed

**Exit Criteria** (Before moving to next phase):
- [ ] All planned tests executed
- [ ] Test pass rate ≥ [95%]
- [ ] Test coverage targets met (unit ≥80%, integration ≥70%)
- [ ] No open P0 or P1 defects
- [ ] All P2 defects reviewed and accepted/deferred
- [ ] Performance targets met
- [ ] Security scan passed
- [ ] Regression tests passed
- [ ] UAT sign-off obtained (if UAT phase)
- [ ] Test reports completed and reviewed
- [ ] Known issues documented

---

## Test Automation Strategy

**Automation Philosophy**: Automate everything that can be automated reliably and cost-effectively.

**Automation Goals**:
- **Unit Tests**: 100% automated (run on every commit)
- **Integration Tests**: 100% automated (run on every commit)
- **E2E Tests**: 80% automated, 20% manual exploratory
- **Performance Tests**: 100% automated (run pre-release)
- **Security Tests**: 90% automated, 10% manual penetration testing

**Automation Framework Stack**:

| Layer | Framework | Language | Purpose | CI/CD Integration |
|-------|-----------|----------|---------|-------------------|
| Unit | **pytest** | Python | Test individual functions/classes | ✅ Every commit |
| Unit | **Jest** | JavaScript | Test frontend components | ✅ Every commit |
| Integration | **pytest + requests** | Python | Test API endpoints | ✅ Every commit |
| Integration | **Supertest** | JavaScript | Test Node.js APIs | ✅ Every commit |
| E2E | **Cypress** | JavaScript | Test user workflows | ✅ Pre-merge |
| E2E | **Playwright** | TypeScript | Cross-browser testing | ✅ Nightly |
| Performance | **k6** | JavaScript | Load/stress testing | ✅ Pre-release |
| Performance | **Locust** | Python | Performance testing | ✅ Pre-release |
| Security | **Bandit** | Python | Static security analysis | ✅ Every commit |
| Security | **OWASP ZAP** | N/A | Dynamic security testing | ✅ Nightly |
| Security | **Snyk** | N/A | Dependency scanning | ✅ Daily |

> **Note**: See [Unit Testing > Pytest Best Practices](#pytest-best-practices--patterns) for comprehensive pytest patterns including fixtures, parametrization, markers, and code examples.

**Test Automation Best Practices**:
- **Arrange-Act-Assert Pattern**: Structure tests with clear setup, execution, and verification
- **Test Independence**: Tests can run in any order without dependencies
- **Fixture Reusability**: Use pytest fixtures for common setup/teardown (session, module, function scopes)
- **Data-Driven Tests**: Use `@pytest.mark.parametrize` for testing multiple scenarios
- **Test Categorization**: Use markers (`@pytest.mark.smoke`, `@pytest.mark.slow`) for flexible test execution
- **Mock External Dependencies**: Prevent actual API/database calls during unit tests
- **Clear Naming**: Test names describe what they test (e.g., `test_user_login_fails_with_invalid_password`)
- **Fast Execution**: Optimize slow tests, use parallel execution (`pytest -n auto`)
- **CI/CD Integration**: Tests run automatically on every commit with coverage reporting

**Automation Test Organization**:
```
tests/
├── unit/
│   ├── backend/
│   ├── frontend/
│   └── fixtures/
├── integration/
│   ├── api/
│   ├── database/
│   └── fixtures/
├── e2e/
│   ├── pages/
│   ├── specs/
│   └── support/
├── performance/
│   └── load-tests/
└── security/
    └── scans/
```

**CI/CD Pipeline Integration**:
```yaml
# Example GitHub Actions workflow
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Unit Tests
        run: pytest tests/unit/ --cov=agent
      
      - name: Run Integration Tests
        run: pytest tests/integration/ -v
      
      - name: Run E2E Tests
        run: npx cypress run --headless
      
      - name: Run Security Scan
        run: bandit -r agent/
      
      - name: Upload Coverage
        run: codecov
```

---

## Validation Checklist

**Pre-Testing Validation**:
- [ ] Test plan reviewed and approved by stakeholders
- [ ] All test cases documented
- [ ] Test environment ready and validated
- [ ] Test data prepared
- [ ] Team trained on testing process

**Testing Execution Validation**:
- [ ] All planned tests executed
- [ ] Test results documented
- [ ] Defects logged and tracked
- [ ] Coverage reports generated

**Post-Testing Validation**:
- [ ] All exit criteria met
- [ ] Test summary report completed
- [ ] Stakeholder sign-off obtained
- [ ] Lessons learned documented

**OpenSpec Validation**:
- [ ] Test plan aligns with proposal and spec
- [ ] All acceptance criteria tested
- [ ] Traceability matrix complete (requirements → tests)
- [ ] `openspec validate [change-id] --strict` passes

---

## Test Results Summary

**Overall Test Results**: [PASS / FAIL / PENDING]

**Test Execution Summary**:
- **Total Tests**: [X]
- **Executed**: [X]
- **Passed**: [X] ([X%])
- **Failed**: [X] ([X%])
- **Blocked**: [X] ([X%])
- **Not Executed**: [X]

**Coverage Summary**:
- **Unit Test Coverage**: [X%] (Target: ≥80%)
- **Integration Test Coverage**: [X%] (Target: ≥70%)
- **E2E Test Coverage**: [Critical paths covered]

**Defect Summary**:
- **Total Defects**: [X]
- **Critical/High**: [X] ([X] open)
- **Medium**: [X] ([X] open)
- **Low**: [X] ([X] open)

**Performance Results**:
- **Response Time (P95)**: [X ms] (Target: <500ms)
- **Throughput**: [X req/sec] (Target: ≥[Y req/sec])
- **Concurrent Users**: [X] (Target: ≥[Y])

**Security Results**:
- **Critical Vulnerabilities**: [X] (Target: 0)
- **High Vulnerabilities**: [X] (Target: 0)
- **Medium Vulnerabilities**: [X]
- **Low Vulnerabilities**: [X]

**UAT Results**:
- **Scenarios Executed**: [X]
- **Scenarios Passed**: [X] ([X%])
- **User Satisfaction**: [X/5] (Target: ≥4/5)
- **Sign-off**: [Obtained / Pending]

**Go-Live Recommendation**: [GO / NO-GO]

**Justification**: [Brief explanation of recommendation based on test results]

**Outstanding Issues**:
- [Issue 1]: [Description and plan]
- [Issue 2]: [Description and plan]

**Test Completion Date**: [YYYY-MM-DD]

**Next Steps**:
- [Action item 1]
- [Action item 2]
- [Action item 3]

---

## Document Metadata

- **Created**: [YYYY-MM-DD]
- **Last Updated**: [YYYY-MM-DD]
- **Version**: [v1.0]
- **Authors**: @[QA Lead], @[username]
- **Reviewers**: @[Tech Lead], @[Product Owner]
- **Approved By**: @[Stakeholder]
- **Approval Date**: [YYYY-MM-DD]

---

## Template Usage Instructions

**For New Projects**:
1. Copy this template to your change directory: `openspec/changes/[change-name]/test_plan.md`
2. Replace all `[bracketed placeholders]` with actual values
3. Delete sections that don't apply to your project
4. Customize test cases based on your requirements
5. Review with QA lead and stakeholders
6. Get approval before starting test execution

**Tips**:
- Start with high-priority test types (unit, integration, E2E)
- Focus test coverage on critical paths and high-risk areas
- Automate repetitive tests early
- Document test results as you execute
- Update test plan as project evolves
- Use this as living documentation throughout testing phase

---

**Related Resources**:
- **Proposal**: [proposal.md](./proposal.md) - Business case and context
- **Specification**: [spec.md](./spec.md) - Technical requirements
- **Tasks**: [tasks.md](./tasks.md) - Implementation tasks
- **TODO**: [todo.md](./todo.md) - Task tracking
- **Changelog**: [CHANGELOG.md](../../CHANGELOG.md) - Project version history
