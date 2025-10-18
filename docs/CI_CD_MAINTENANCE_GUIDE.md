# CI/CD Next Steps & Maintenance Guide

## ✅ Current State (October 18, 2025)

### Deployment Status
- **Status**: ✅ PRODUCTION READY
- **Test Success Rate**: 99.8% (1021/1042 passing)
- **Coverage**: 88%+ backend (target: 85%+)
- **PR Feedback Time**: 5-10 minutes (was 15-25 minutes)
- **OpenSpec Compliance**: 56/56 passing

### Active Workflows
1. **test-backend.yml** - PR-fast (2-3 min) / Push-full (3-5 min)
2. **ci.yml** - Comprehensive pipeline (5-10 min PR / 15-25 min push)
3. **nightly-comprehensive.yml** - Scheduled at 2 AM UTC
4. **openspec-validate.yml** - OpenSpec governance checks
5. **openspec-pr-validate.yml** - PR-specific OpenSpec validation

## 🎯 Immediate Monitoring Tasks

### Week 1: Baseline Collection
- [ ] Monitor first nightly comprehensive run (2 AM UTC tonight)
- [ ] Check cache hit rates in workflow logs
- [ ] Validate PR feedback times are consistently <10 minutes
- [ ] Ensure no false positives in automated issue creation
- [ ] Review GitHub Actions usage/billing impact

### Week 2: Optimization Validation
- [ ] Analyze cache effectiveness across workflows
- [ ] Identify any flaky tests that need attention
- [ ] Review nightly comprehensive reports for patterns
- [ ] Assess if matrix can be further optimized
- [ ] Check for any performance regressions

### Continuous Monitoring
```bash
# Check recent workflow runs
gh run list --limit 20

# View specific workflow status
gh run view <run-id>

# Watch cache performance
# Look for "Cache restored from key:" in logs
```

## 🔧 Recommended Enhancements

### Priority 1: Path Filtering (High Value, Low Effort)
**Goal**: Skip unnecessary workflow runs when only docs change

**Implementation**:
```yaml
# Add to workflows that don't need to run for docs changes
on:
  push:
    branches: [main]
    paths-ignore:
      - 'docs/**'
      - '*.md'
      - 'LICENSE'
      - '.gitignore'
```

**Impact**: 20-30% reduction in unnecessary workflow runs

---

### Priority 2: Workflow Templates (Medium Value, Medium Effort)
**Goal**: Reduce duplication across workflows

**Implementation**:
```yaml
# .github/workflows/reusable-test.yml
name: Reusable Test Workflow
on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string
      test-subset:
        required: false
        type: string
        default: "tests/"

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      # ... rest of shared steps
```

**Usage**:
```yaml
jobs:
  test-python-311:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: '3.11'
      test-subset: 'tests/backend'
```

**Impact**: Easier maintenance, reduced duplication

---

### Priority 3: Matrix Reduction for PRs (High Value, Low Effort)
**Goal**: Run full cross-platform matrix only on push, not PRs

**Current**: PRs run ubuntu + windows + macOS
**Proposed**: PRs run ubuntu only, push runs full matrix

**Implementation** (in test-backend.yml):
```yaml
strategy:
  matrix:
    python-version: ['3.11']
    os: ${{ github.event_name == 'pull_request' && fromJSON('["ubuntu-latest"]') || fromJSON('["ubuntu-latest", "windows-latest", "macos-latest"]') }}
```

**Impact**: 66% faster PR checks (3 OS → 1 OS)

---

### Priority 4: Coverage Trending (Medium Value, Medium Effort)
**Goal**: Track coverage over time, alert on drops

**Implementation**:
1. Sign up for Codecov (free for open source)
2. Add to workflow:
```yaml
- name: Upload to Codecov
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage.xml
    flags: backend
    fail_ci_if_error: true
```

**Impact**: Visual coverage trends, historical tracking

---

### Priority 5: Benchmark Baseline Storage (Low Value, High Effort)
**Goal**: Detect performance regressions automatically

**Implementation**:
1. Store benchmark results as artifacts
2. Compare against main branch baseline
3. Alert on >10% degradation

**Tools**:
- pytest-benchmark with `--benchmark-compare`
- GitHub Actions artifact storage
- Custom comparison script

**Impact**: Automated performance regression detection

---

### Priority 6: Flaky Test Detection (High Value, Medium Effort)
**Goal**: Identify and fix unreliable tests

**Implementation**:
```bash
# Run tests multiple times to detect flakes
pytest tests/ --count=10 --ignore-flaky
```

**Integration**:
- Weekly scheduled job
- Report to GitHub Issues
- Tag tests with `@pytest.mark.flaky`

**Impact**: Improved test reliability

## 📊 Monitoring & Alerts

### Key Metrics to Track

#### CI Performance
```
Metric                    | Target     | Alert Threshold
--------------------------|------------|----------------
PR feedback time          | <10 min    | >15 min
Push validation time      | <25 min    | >30 min
Cache hit rate            | >70%       | <50%
Test success rate         | >99%       | <98%
Coverage                  | >85%       | <85%
```

#### Resource Usage
```
Metric                    | Current    | Concern Threshold
--------------------------|------------|------------------
Monthly Actions minutes   | TBD        | >80% of limit
Storage (artifacts)       | TBD        | >80% of limit
Concurrent jobs           | 3-5        | >10
```

### Automated Alerts
The nightly comprehensive workflow will automatically create GitHub issues for:
- Test failures
- Coverage drops
- Security vulnerabilities
- Performance regressions

**Issue labels**: `ci`, `nightly-failure`, `automated`

### Manual Review Schedule
- **Daily**: Check for PR workflow failures
- **Weekly**: Review nightly comprehensive reports
- **Monthly**: Analyze cache effectiveness and resource usage
- **Quarterly**: Reassess CI strategy and optimization opportunities

## 🚨 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Slow PR Feedback
**Symptoms**: PR checks taking >10 minutes

**Diagnosis**:
```bash
# Check workflow duration
gh run list --workflow=test-backend.yml --limit 5

# View specific run
gh run view <run-id> --log
```

**Solutions**:
- Check cache hit rate (should be >70%)
- Look for tests that suddenly became slow
- Verify PR-fast exclusions are working
- Consider further test categorization

#### 2. Flaky Tests
**Symptoms**: Tests pass locally but fail in CI intermittently

**Diagnosis**:
```bash
# Run test multiple times locally
pytest tests/backend/test_name.py --count=10
```

**Solutions**:
- Add `@pytest.mark.flaky` and re-run
- Check for timing dependencies
- Verify async/await patterns
- Add explicit waits or timeouts

#### 3. Cache Misses
**Symptoms**: Dependencies reinstall on every run

**Diagnosis**: Check workflow logs for "Cache restored from key:"

**Solutions**:
- Verify requirements.txt hasn't changed
- Check cache key configuration
- Ensure cache action runs before install
- Review cache size limits (10GB/repo)

#### 4. Coverage Drops
**Symptoms**: Coverage below 85% on push

**Diagnosis**:
```bash
# Generate local coverage report
pytest --cov=backend --cov-report=html
# Open htmlcov/index.html
```

**Solutions**:
- Identify uncovered modules
- Add tests for new code
- Review coverage exclusions
- Check for dead code removal

#### 5. Nightly Failures
**Symptoms**: Automated issues created by nightly workflow

**Diagnosis**: Review the linked workflow run in the issue

**Solutions**:
- Platform-specific issues: Check OS-specific code paths
- Security issues: Review Bandit/Safety reports
- Performance issues: Check benchmark comparisons
- Voice tests: May need special dependencies

## 📋 Maintenance Checklist

### Weekly
- [ ] Review PR workflow success rate
- [ ] Check for new flaky tests
- [ ] Verify cache hit rates
- [ ] Review any automated failure issues

### Monthly
- [ ] Analyze workflow duration trends
- [ ] Review GitHub Actions usage
- [ ] Update dependencies (requirements.txt)
- [ ] Check for workflow action updates
- [ ] Review test durations for new slow tests

### Quarterly
- [ ] Reassess test categorization strategy
- [ ] Evaluate matrix optimization opportunities
- [ ] Review caching effectiveness
- [ ] Update CI/CD documentation
- [ ] Consider new GitHub Actions features

## 🎓 Best Practices

### Test Writing
```python
# DO: Mark intentionally slow tests
@pytest.mark.slow
def test_long_operation():
    # Test that takes >1s
    pass

# DO: Use time mocking for delays
def test_ttl_expiry(monkeypatch):
    monkeypatch.setattr(time, "time", lambda: 1000)
    # Test cache expiry logic

# DON'T: Use real sleeps in tests
def test_bad_example():
    time.sleep(5)  # ❌ Slows down entire suite
```

### Workflow Configuration
```yaml
# DO: Use caching for dependencies
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}

# DO: Use conditions for heavy jobs
if: github.event_name == 'push' || github.event_name == 'workflow_dispatch'

# DON'T: Run all tests on every PR
# Use test categorization and fast subsets
```

### Coverage Management
```bash
# DO: Run coverage locally before pushing
pytest --cov=backend --cov-report=term-missing

# DO: Focus on meaningful coverage
# Aim for high coverage of business logic, not boilerplate

# DON'T: Aim for 100% coverage at the cost of test quality
# 85%+ with good test quality > 100% with poor tests
```

## 🔗 Useful Commands

### Local Development
```bash
# Run PR-fast subset locally
pytest tests/backend -k "not comprehensive and not performance_regression and not voice" -m "not slow" --durations=20

# Run full suite with coverage
pytest tests/ --cov=backend --cov-report=html --cov-fail-under=85

# Check for slow tests
pytest tests/backend --durations=0

# Run tests with cache statistics
pytest tests/ -v --cache-show
```

### GitHub CLI
```bash
# View recent workflow runs
gh run list --limit 10

# View specific run
gh run view <run-id>

# Re-run failed jobs
gh run rerun <run-id> --failed

# Watch a running workflow
gh run watch <run-id>

# Download workflow artifacts
gh run download <run-id>
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/new-optimization

# Run local tests before pushing
pytest tests/backend -v

# Push and open PR
git push -u origin feature/new-optimization
gh pr create --title "feat: add optimization" --body "Description"

# Check PR status
gh pr checks
```

## 📚 Additional Resources

### Documentation
- [CI/CD Optimization Summary](./CI_CD_OPTIMIZATION_SUMMARY.md)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)

### Related Files
- `.github/workflows/*.yml` - All workflow definitions
- `pytest.ini` - pytest configuration
- `requirements.txt` - Python dependencies
- `backend/config.yaml` - Backend configuration

### Team Contacts
- CI/CD Issues: Create issue with `ci` label
- Test Failures: Create issue with `test-failure` label
- Performance: Create issue with `performance` label

## 🎯 Success Criteria

Your CI/CD pipeline is successfully optimized when:

- ✅ PR feedback consistently <10 minutes
- ✅ Test success rate >99%
- ✅ Coverage maintained at >85%
- ✅ Cache hit rate >70%
- ✅ No false positives in failure detection
- ✅ Nightly comprehensive runs complete successfully
- ✅ Security scans pass without critical issues
- ✅ Team satisfaction with CI speed and reliability

## 📞 Support

For CI/CD issues or questions:
1. Check this guide first
2. Review workflow logs in GitHub Actions
3. Search existing issues for similar problems
4. Create new issue with relevant labels and logs
5. Tag maintainers if urgent

---

**Last Updated**: October 18, 2025  
**Maintainer**: AI-assisted development team  
**Next Review**: November 18, 2025
