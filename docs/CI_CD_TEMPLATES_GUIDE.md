# CI/CD Templates Guide for v0.1.44

## Overview

This guide provides comprehensive documentation for the GitHub Actions CI/CD templates used in the v0.1.44 enhancement cycle. Templates are organized by lane (docs/standard/heavy) to ensure appropriate validation and deployment strategies for different types of changes.

**Key Templates:**
- `pull_request.yml` - Automatic lane detection and PR validation
- `deployment.yml` - Lane-aware deployment orchestration
- Custom lane-specific validation jobs

## Architecture

### Template Hierarchy

```
GitHub Actions Workflows
├── Pull Request Workflow (pull_request.yml)
│   ├── Lane Detection Job
│   ├── Docs Quality Gates
│   ├── Standard Quality Gates
│   └── Heavy Quality Gates
│
├── Deployment Workflow (deployment.yml)
│   ├── Pre-Deployment Validation
│   ├── Lane-Specific Testing
│   │   ├── Docs Tests
│   │   ├── Standard Tests
│   │   └── Heavy Tests
│   └── Environment-Specific Deployment
│       ├── Staging Deployment
│       └── Production Deployment
│
└── Integration Workflows (optional)
    ├── Nightly Testing
    ├── Performance Benchmarking
    └── Security Scanning
```

## Pull Request Workflow

### Overview

The PR workflow automatically detects the lane for incoming pull requests and applies appropriate quality gates.

**Triggering Events:**
- PR opened/reopened
- Synchronize (new commits)
- Draft status changed to ready

**Lane Detection Algorithm:**

```
IF (only .md/.docs files changed) AND (no .py/.js/.ts changed):
  LANE = "docs"
ELIF (total_files ≤ 5) AND (code_files ≤ 2):
  LANE = "standard"
ELSE:
  LANE = "heavy"
```

### Docs Lane Workflow

**Triggers:** Documentation-only changes

**Quality Gates:**
1. Markdown syntax validation
2. Documentation structure checks
3. Completeness verification
4. Link validation

**Example PRs:**
- Update API documentation
- Add new guides
- Fix typos in README
- Add architectural diagrams

**Execution Time:** ~2-3 minutes

```
quality-docs job:
├── Checkout code
├── Setup Python 3.11
├── Check Markdown syntax
└── Validate documentation structure
```

### Standard Lane Workflow

**Triggers:** Small-to-medium changes with tests

**Quality Gates:**
1. Python linting (Ruff)
2. Type checking (mypy)
3. Security scanning (Bandit)
4. Unit tests execution

**Example PRs:**
- Add new test cases
- Fix validation logic
- Small feature implementation
- Bug fixes with tests

**Execution Time:** ~8-12 minutes

```
quality-standard job:
├── Checkout code
├── Setup Python 3.11
├── Install dependencies
├── Linting (Ruff)
├── Type checking (mypy)
├── Security scan (Bandit)
├── Run unit tests
└── Upload test results
```

### Heavy Lane Workflow

**Triggers:** Large changes, refactoring, multiple modules

**Quality Gates:**
1. Full linting suite
2. Type checking
3. Security scanning
4. Comprehensive test suite
5. Performance regression tests
6. Integration tests
7. Code coverage analysis

**Example PRs:**
- Major refactoring
- New module architecture
- Large feature development
- Core system changes

**Execution Time:** ~20-40 minutes

```
quality-heavy job:
├── Checkout code (with full history)
├── Setup Python 3.11
├── Install dependencies
├── Linting and quality checks
├── Comprehensive test suite
├── Performance regression tests
├── Integration tests
├── Generate coverage report
└── Upload test artifacts
```

## Deployment Workflow

### Overview

Manual deployment workflow triggered on-demand with lane-specific validation.

**Triggering Method:**
```
GitHub Actions → Workflows → Deployment Workflow → Run workflow

Required Inputs:
- Lane: docs/standard/heavy
- Environment: staging/production
- Version: Git tag (e.g., v0.1.44)
- Skip Tests: true/false (not recommended)
```

### Pre-Deployment Validation

**Steps:**
1. Verify version tag exists
2. Validate input parameters
3. Check deployment prerequisites
4. Lane-specific pre-deployment tests

**Validation Output:**
```
✓ Version tag found: v0.1.44
✓ Lane selected: standard
✓ Environment target: production
✓ Pre-deployment checks passed
```

### Lane-Specific Testing

#### Docs Lane Deployment Tests

```
test-docs job:
├── Checkout v0.1.44
├── Setup Python
├── Test documentation build
├── Generate documentation artifacts
└── Upload docs-v0.1.44.tar.gz
```

**Validations:**
- Documentation builds without errors
- All links are valid
- API documentation complete
- Schema validation

**Time:** ~3-5 minutes

#### Standard Lane Deployment Tests

```
test-standard job:
├── Checkout v0.1.44
├── Setup Python
├── Install dependencies
├── Run standard test suite
├── Validate API health
└── Package artifacts
```

**Validations:**
- All unit tests pass
- API health endpoints responsive
- Backend service starts correctly
- Configuration valid

**Time:** ~10-15 minutes

#### Heavy Lane Deployment Tests

```
test-heavy job:
├── Checkout v0.1.44
├── Setup Python
├── Install dependencies (full)
├── Comprehensive test suite
├── Performance validation
├── Integration tests
├── Generate test report
└── Upload detailed artifacts
```

**Validations:**
- Full test suite (85%+ coverage required)
- Performance benchmarks meet SLA
- Integration with external services
- Database migrations tested
- Backward compatibility verified

**Time:** ~30-60 minutes

### Environment-Specific Deployment

#### Staging Deployment

**Prerequisites:**
- Pre-deployment validation passed
- All tests successful
- Deployment window approved

**Steps:**
1. Download deployment artifacts
2. Extract application files
3. Execute deployment scripts
4. Run smoke tests
5. Create deployment tracking issue

**Execution:**
```bash
./scripts/deploy.sh \
  --environment staging \
  --version v0.1.44 \
  --lane standard
```

**Post-Deployment:**
- Smoke tests verify core functionality
- API health checks pass
- Logging configured correctly
- Monitoring active

**Rollback:** Automatic on failure, manual if needed

#### Production Deployment

**Prerequisites:**
- Staging deployment successful
- Manual approval obtained
- Change window approved
- Backup verification complete

**Steps:**
1. Create pre-deployment backup
2. Download deployment artifacts
3. Execute deployment scripts
4. Run health checks
5. Run smoke tests
6. Create GitHub release
7. Create deployment tracking issue

**Execution:**
```bash
./scripts/deploy.sh \
  --environment production \
  --version v0.1.44 \
  --lane standard
```

**Safeguards:**
- Pre-deployment backup created
- Health checks mandatory
- Smoke tests required
- Automated rollback on critical failure

## Using the Templates

### Manual PR Workflow Trigger

PRs automatically trigger when:
1. Opened against main/develop/release-* branches
2. New commits pushed (synchronize)
3. Changed from draft to ready for review

**No manual action required - workflow triggers automatically**

### Manual Deployment Trigger

```
1. Go to GitHub → Actions
2. Select "Deployment Workflow"
3. Click "Run workflow"
4. Fill in inputs:
   - Lane: select from dropdown
   - Environment: staging or production
   - Version: enter tag (e.g., v0.1.44)
   - Skip Tests: usually false
5. Click "Run workflow"
```

### Deployment Flow Example

**Scenario:** Deploy v0.1.44 to production using standard lane

```
1. Pre-Deployment Validation Job
   ├─ Check version tag exists
   └─ Validate inputs
   
2. Test Standard Deployment Job (parallel)
   ├─ Run full test suite
   ├─ Validate API health
   └─ Package artifacts
   
3. Deploy to Production Job (sequential)
   ├─ Create backup
   ├─ Download artifacts
   ├─ Execute deployment
   ├─ Run health checks
   ├─ Run smoke tests
   └─ Create release
   
4. Post-Deployment Validation Job
   ├─ Validate functionality
   ├─ Collect metrics
   └─ Generate report
```

## Environment Configuration

### Required Secrets (GitHub Secrets)

```
DEPLOY_SSH_KEY          # SSH key for deployment servers
DEPLOY_KNOWN_HOSTS      # Known hosts for SSH
SLACK_WEBHOOK_URL       # Slack notifications
GITHUB_TOKEN            # For issue creation (auto-provided)
```

### Environment Secrets

**Staging Environment:**
```
STAGING_HOST = staging.obsidian-ai.local
STAGING_PORT = 8000
STAGING_HEALTH_CHECK_URL = http://staging.obsidian-ai.local:8000/health
```

**Production Environment:**
```
PRODUCTION_HOST = obsidian-ai.local
PRODUCTION_PORT = 8000
PRODUCTION_HEALTH_CHECK_URL = https://obsidian-ai.local:8000/health
```

### Environment Approval Rules (Optional)

```yaml
# .github/environments.yml
production:
  deployment_branch_policy: main|release-*
  reviewers:
    - @maintainers
  timeout_minutes: 30

staging:
  deployment_branch_policy: develop|release-*
  reviewers:
    - @developers
  timeout_minutes: 15
```

## Monitoring & Debugging

### Workflow Status

Check workflow execution:
1. GitHub → Actions → Workflow name
2. Click on specific run
3. View job logs and status

### Common Issues

#### Lane Detection Wrong

**Symptom:** PR in standard lane should be heavy

**Solution:**
1. Check changed files
2. Verify file patterns (test, code, doc)
3. Manual lane override in comments (if supported)

#### Tests Failing

**Symptom:** Quality gates fail, PR blocked

**Solution:**
1. Check detailed error logs
2. Run locally: `pytest tests/backend/ -v`
3. Fix issues and push new commit

#### Deployment Failed

**Symptom:** Deployment job fails

**Solution:**
1. Check deployment logs in Actions
2. Verify version tag exists
3. Check target environment health
4. May need manual rollback

### Viewing Artifacts

1. GitHub → Actions → Workflow run
2. Scroll to "Artifacts" section
3. Download deployment-v0.1.44.tar.gz (example)
4. Extract locally for inspection

## Customization

### Adding Custom Quality Gates

Example: Add custom validation for heavy lane

```yaml
# In .github/workflows/pull_request.yml
quality-heavy:
  steps:
    # ... existing steps ...
    
    - name: Custom validation
      run: |
        python scripts/custom_validation.py \
          --lane heavy \
          --strict
```

### Modifying Deployment Steps

Example: Add Slack notification

```yaml
# In .github/workflows/deployment.yml
deploy-to-production:
  steps:
    # ... existing steps ...
    
    - name: Notify Slack
      uses: slackapi/slack-github-action@v1
      with:
        webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
        payload: |
          {
            "text": "Production deployment: v0.1.44",
            "lane": "${{ github.event.inputs.lane }}"
          }
```

### Adding New Lane

If adding a 4th lane (e.g., "enterprise"):

1. Update lane detection in detect-lane job
2. Create `quality-enterprise` job
3. Add `enterprise` input option to deployment workflow
4. Update documentation

## Best Practices

### For Contributors

1. **Understand Your Lane**
   - Small docs changes? → docs lane
   - Adding tests? → standard lane
   - Refactoring? → heavy lane

2. **Provide Context**
   - Clear PR descriptions
   - Link related issues
   - Explain changes

3. **Fix CI Failures**
   - Don't ignore failing tests
   - Check detailed error logs
   - Run tests locally first

### For Maintainers

1. **Monitor Workflow Performance**
   - Track average execution times
   - Identify bottlenecks
   - Optimize long-running jobs

2. **Keep Templates Updated**
   - Update dependencies regularly
   - Add new validation tools
   - Document changes

3. **Audit Deployments**
   - Review deployment logs
   - Monitor post-deployment health
   - Establish rollback procedures

## Integration with External Tools

### Slack Integration

```yaml
- name: Notify Slack
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "CI/CD Update",
        "status": "success"
      }
```

### Code Coverage (Codecov)

```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

### Status Badges

Add to README.md:
```markdown
[![Pull Request Workflow](https://github.com/UndiFineD/obsidian-AI-assistant/actions/workflows/pull_request.yml/badge.svg)](https://github.com/UndiFineD/obsidian-AI-assistant/actions/workflows/pull_request.yml)
```

## Troubleshooting Guide

### "Version tag not found"

**Cause:** Tag doesn't exist or wrong format
**Fix:** Ensure tag exists: `git tag -l v0.1.44`

### "Tests skipped in deployment"

**Cause:** skip_tests set to true
**Fix:** Re-run with skip_tests: false

### "Environment approval timeout"

**Cause:** Approval not provided within timeout
**Fix:** Request reviewer approval or adjust timeout

### "Rollback needed"

**Procedure:**
1. Stop new deployment
2. Restore from backup: `./scripts/restore.sh --version previous`
3. Run smoke tests
4. Verify system health

## Performance Optimization

### Caching Dependencies

```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### Parallel Job Execution

Jobs run in parallel when possible:
- test-docs, test-standard, test-heavy run independently
- Quality gates only block on lane-specific job

### Artifact Retention

```yaml
- name: Upload artifacts
  uses: actions/upload-artifact@v3
  with:
    retention-days: 30
```

## Summary

The CI/CD templates provide:
- ✅ Automatic lane detection
- ✅ Lane-specific validation
- ✅ Staged deployment with safeguards
- ✅ Comprehensive testing
- ✅ Post-deployment monitoring
- ✅ Audit trails and tracking

For more information, refer to specific template files in `.github/workflows/`
