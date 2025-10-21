# Release Automation Guide

## Overview

This guide documents the comprehensive release automation system for Obsidian AI Agent, including automated version
bumping, changelog generation, asset building, and GitHub releases.

## 🚀 Release Workflow Features

### Automated Release Triggers

1. **Manual Dispatch**: Trigger releases manually with version type selection
2. **Tag-based Releases**: Create releases by pushing version tags
3. **Auto-releases**: Create releases automatically based on commit activity

### Release Components

- **Version Management**: Automatic version bumping across all project files
- **Changelog Generation**: AI-powered changelog categorization and formatting
- **Asset Building**: Plugin, backend, and complete package distributions
- **GitHub Releases**: Automated release creation with comprehensive metadata
- **Post-Release Tasks**: Issue creation and notification system

## 🔧 Configuration Files

### 1. GitHub Actions Workflow (`.github/workflows/release.yml`)

The main release automation workflow with 7 distinct jobs:

- **prepare-release**: Version detection and validation
- **test-before-release**: Comprehensive testing before release
- **update-version**: Version file synchronization
- **generate-changelog**: Automated changelog generation
- **build-assets**: Distribution package creation
- **create-release**: GitHub release and asset publishing
- **post-release**: Follow-up tasks and notifications

### 2. Version Manager Script (`scripts/version_manager.py`)

Local version management utility for development:

```bash
# Check current version
python scripts/version_manager.py current

# Check version consistency across files
python scripts/version_manager.py check

# Bump version (patch, minor, major)
python scripts/version_manager.py bump patch

# Set specific version
python scripts/version_manager.py set 1.2.3

# Validate version format
python scripts/version_manager.py validate 1.2.3
```

## 📋 Release Types

### 1. Manual Release (Recommended)

Trigger a release manually with full control:

```yaml
# In GitHub Actions
workflow_dispatch:
  inputs:
    release_type: patch|minor|major
    prerelease: true|false
```

**Steps:**
1. Go to GitHub Actions → Release Automation
2. Click "Run workflow"
3. Select release type and prerelease option
4. Monitor workflow execution

### 2. Tag-based Release

Create a release by pushing a version tag:

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

**Features:**
- Automatic version detection from tag
- Pre-release detection (tags with `-` suffix)
- Complete release pipeline execution

### 3. Automatic Release

Releases are automatically created based on commit activity:

- **Trigger**: More than 5 commits since last release
- **Version Type**: Determined by conventional commit messages
    - `feat:` → minor version bump
    - `feat!:` or `BREAKING CHANGE:` → major version bump
    - Other commits → patch version bump

## 📦 Release Assets

Each release creates three distribution packages:

### 1. Plugin Package (`obsidian-ai-agent-plugin-vX.Y.Z.zip`)

Contains Obsidian plugin files ready for installation:
- `main.js` - Core plugin functionality
- `manifest.json` - Plugin metadata
- `styles.css` - Plugin styling
- Enterprise modules (if available)

**Installation:**
1. Download and extract to `.obsidian/plugins/obsidian-ai-agent/`
2. Enable plugin in Obsidian settings

### 2. Backend Package (`obsidian-ai-agent-backend-vX.Y.Z.tar.gz`)

Contains FastAPI backend server and dependencies:
- `agent/` - Server modules
- `requirements.txt` - Python dependencies
- Setup scripts (`setup.ps1`, `setup.sh`)
- Documentation

**Installation:**
```bash
tar -xzf obsidian-ai-agent-backend-vX.Y.Z.tar.gz
cd backend-source
./setup.ps1  # Windows
./setup.sh   # Linux/macOS
```

### 3. Complete Package (`obsidian-ai-agent-complete-vX.Y.Z.tar.gz`)

Full project distribution with both plugin and backend:
- Complete source code
- All setup scripts
- Documentation
- Test suite (development files excluded)

**Installation:**
```bash
tar -xzf obsidian-ai-agent-complete-vX.Y.Z.tar.gz
cd obsidian-ai-agent
./setup.ps1  # Complete setup
```

## 📝 Changelog Generation

### Automatic Categorization

Commits are automatically categorized using conventional commit patterns:

- **✨ Features**: `feat:`, `feature:`
- **🐛 Bug Fixes**: `fix:`, `bugfix:`
- **📚 Documentation**: `docs:`, `doc:`
- **🔧 Maintenance**: `chore:`, `refactor:`, `style:`, `test:`
- **🔒 Security**: `security:`, `sec:`
- **📊 Performance**: `perf:`, `performance:`
- **💥 Breaking Changes**: `BREAKING CHANGE:`, `feat!:`

### Changelog Structure

```markdown
## 🚀 Release vX.Y.Z - YYYY-MM-DD

### ✨ Features
- feat: Add new AI model support (abc123)

### 🐛 Bug Fixes  
- fix: Resolve memory leak in embeddings (def456)

### 📦 Installation
[Installation instructions]

### 🔧 Compatibility
- Python: 3.11+
- Obsidian: 0.15.0+
- OS: Windows 10+, macOS 10.15+, Ubuntu 18.04+

### 👥 Contributors
- @contributor1
- @contributor2
```

## 🔍 Version Management

### Version File Synchronization

The system maintains version consistency across:

1. **`package.json`** - Primary version source
2. **`.obsidian/plugins/obsidian-ai-agent/manifest.json`** - Plugin version
3. **`agent/__init__.py`** - Python package version
4. **`setup.py`** - Distribution version (if exists)

### Version Validation

All versions must follow semantic versioning (SemVer):
- Format: `MAJOR.MINOR.PATCH[-prerelease][+build]`
- Examples: `1.0.0`, `1.2.3-beta.1`, `2.0.0+20231016`

## 🧪 Pre-Release Testing

### Test Requirements

Before any release, the system runs comprehensive tests:

```yaml
# Test matrix
python-version: ['3.11']

# Test commands
pytest tests/ -v --cov=backend --cov-fail-under=70 --cov-report=xml
```

### Coverage Requirements

- **Minimum Coverage**: 70% for releases
- **Target Coverage**: 85% for production releases
- **Coverage Reports**: Uploaded as workflow artifacts

### Test Failure Handling

If tests fail during the release process:
1. Release is automatically cancelled
2. No version updates are committed
3. GitHub release is not created
4. Error notifications are sent

## 🔐 Security & Permissions

### Required Permissions

The release workflow requires:

```yaml
permissions:
  contents: write      # Create releases and update files
  pull-requests: write # Comment on PRs
  issues: write        # Create post-release issues
```

### Secret Requirements

- **`GITHUB_TOKEN`**: Automatically provided by GitHub Actions
- No additional secrets required for basic functionality

### Security Measures

- All version updates are committed with verification
- Release assets are built in isolated environments
- No sensitive information is exposed in logs
- Automated security scanning before release

## 📊 Monitoring & Notifications

### Post-Release Actions

After successful release creation:

1. **Post-Release Issue**: Automatically created with checklist
2. **Release Verification**: Links to download and test assets
3. **Documentation Updates**: Prompt for documentation updates
4. **Community Notifications**: Preparation for announcements

### Post-Release Issue Template

```markdown
## 🎉 Release vX.Y.Z Created Successfully!

### 📋 Post-Release Checklist

- [ ] Verify release assets are downloadable
- [ ] Test plugin installation in Obsidian  
- [ ] Update documentation if needed
- [ ] Announce release on social media/community
- [ ] Monitor for any critical issues
- [ ] Update any dependent projects

### 🔗 Release Links
- GitHub Release: [link]
- Plugin Download: [link]
- Backend Download: [link]
```

## 🔧 Local Development Commands

### Version Management

```bash
# Check current version
python scripts/version_manager.py current

# Check version consistency
python scripts/version_manager.py check

# Bump version locally (for testing)
python scripts/version_manager.py bump patch
```

### Manual Testing

```bash
# Test release workflow locally (dry-run)
act workflow_dispatch -W .github/workflows/release.yml

# Test version bumping
python scripts/version_manager.py set 0.1.1
python scripts/version_manager.py check
```

### Development Workflow

1. **Feature Development**: Work on feature branches
2. **Version Check**: Run `python scripts/version_manager.py check`
3. **Pre-Release Testing**: Run full test suite locally
4. **Release Creation**: Use manual dispatch for controlled releases
5. **Post-Release Verification**: Check generated assets and documentation

## 🎯 Best Practices

### Release Planning

1. **Feature Freeze**: Complete features before release
2. **Testing**: Run comprehensive tests locally
3. **Documentation**: Update docs before release
4. **Communication**: Plan release announcements
5. **Monitoring**: Prepare to monitor post-release

### Version Strategy

- **Patch**: Bug fixes, minor improvements
- **Minor**: New features, backwards compatible
- **Major**: Breaking changes, architectural updates
- **Pre-release**: Beta testing, experimental features

### Commit Messages

Use conventional commit format for automatic categorization:

```bash
feat: add new AI model support
fix: resolve memory leak in embeddings  
docs: update API documentation
chore: update dependencies
BREAKING CHANGE: restructure configuration format
```

## 🚨 Troubleshooting

### Common Issues

1. **Version Inconsistency**
   ```bash
   python scripts/version_manager.py check
   python scripts/version_manager.py set <correct_version>
   ```

1. **Test Failures**
   - Check test results in GitHub Actions
   - Run tests locally: `pytest tests/ -v`
   - Fix failing tests before retry

1. **Asset Build Failures**
   - Verify all required files exist
   - Check file permissions and paths
   - Review build logs in workflow

1. **GitHub Release Failures**
   - Check repository permissions
   - Verify GITHUB_TOKEN access
   - Review API rate limits

### Recovery Procedures

1. **Failed Release**: Delete tag and retry
   ```bash
   git tag -d vX.Y.Z
   git push origin --delete vX.Y.Z
   ```

1. **Version Rollback**: Use version manager
   ```bash
   python scripts/version_manager.py set <previous_version>
   ```

1. **Manual Cleanup**: Remove draft releases from GitHub

## 📈 Release Metrics

### Success Criteria

- ✅ All tests pass (100% test suite)
- ✅ Version consistency across all files
- ✅ All release assets generated successfully
- ✅ GitHub release created with complete metadata
- ✅ Post-release issue created
- ✅ No errors in workflow execution

### Performance Targets

- **Total Release Time**: < 15 minutes
- **Test Execution**: < 5 minutes
- **Asset Building**: < 3 minutes
- **Release Creation**: < 2 minutes

### Quality Gates

- **Code Coverage**: ≥ 70% (target: 85%)
- **Security Scan**: No high/critical vulnerabilities
- **Lint Checks**: All checks passing
- **Version Validation**: SemVer compliance

## 🎉 Success Indicators

A successful release includes:

1. **Workflow Completion**: All jobs completed successfully
2. **Asset Availability**: All three distribution packages available
3. **Version Synchronization**: Consistent versions across all files
4. **Documentation**: Updated changelog and version documentation
5. **Post-Release Tasks**: Issue created with verification checklist
6. **Quality Assurance**: All tests passed and coverage maintained

---

## 📚 Additional Resources

- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Releases Guide](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

*This documentation is automatically maintained as part of the release automation system.*

