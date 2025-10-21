# Dependency Management for Obsidian AI Agent

This document explains the dependency structure, installation procedures, and automated
management system for the Obsidian AI Agent project.

## Overview

Our dependency management system provides multiple layers of protection and automation:

1. **Automated Updates**: Dependabot configuration with intelligent grouping
2. **Security Scanning**: Multi-tool security vulnerability detection
3. **Conflict Detection**: Dependency version conflict resolution  
4. **Compliance Tracking**: License and supply chain risk assessment
5. **Local Validation**: Quick development-time dependency checks

---

## Dependency Files

### `requirements.txt`

Core production dependencies that are required for basic operation:

- FastAPI and web server components

- Basic data processing (numpy, pandas)

- HTTP clients and async operations

- Security and authentication

- Configuration management

- File processing utilities

### `requirements-dev.txt`

Development and testing dependencies:

- pytest and testing frameworks

- Code quality tools (black, ruff, mypy)

- Documentation tools

- Security scanning

- Load testing tools

### `requirements-ml.txt` (NEW)

Machine learning and AI-specific dependencies that may require special installation:

- PyTorch (with CUDA/CPU variants)

- Advanced ML libraries

- Computer vision and audio processing

- NLP libraries

## Installation Instructions

### Basic Installation (Core Features)

```bash
pip install -r requirements.txt
```

### Development Setup

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Full ML Setup

```bash

# Install core dependencies first

pip install -r requirements.txt

# Install PyTorch with appropriate backend

# For CPU only:

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# For CUDA 11.8:

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install additional ML dependencies

pip install -r requirements-ml.txt
```

## Dependency Verification

After installation, verify that all dependencies are compatible:

```bash
python -m pip check
```

## Platform-Specific Notes

### Windows

- Some packages may require Microsoft Visual C++ Build Tools

- GPU support requires NVIDIA CUDA toolkit for CUDA-enabled PyTorch

### Linux

- GPU support requires appropriate NVIDIA drivers and CUDA toolkit

- Some audio processing libraries may require system packages (libsndfile, etc.)

### macOS

- Metal Performance Shaders (MPS) support available in PyTorch 1.12+

- Some packages may require Xcode command line tools

## Common Issues

### PyTorch Installation

If you encounter issues with PyTorch installation, try:

1. Uninstall existing PyTorch: `pip uninstall torch torchvision torchaudio`

1. Clear pip cache: `pip cache purge`

1. Reinstall with specific index URL as shown above

### Memory Issues

For systems with limited RAM:

- Install CPU-only versions of ML libraries

- Consider using quantized models

- Reduce model cache sizes in configuration

### GPU Support

To verify GPU support is working:

```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA devices: {torch.cuda.device_count()}")
```

## Updates and Maintenance

To update dependencies:

```bash
pip install --upgrade -r requirements.txt
pip install --upgrade -r requirements-dev.txt
pip install --upgrade -r requirements-ml.txt
```

To generate updated requirements from current environment:

```bash
pip freeze > requirements-current.txt
```

---

## Automated Dependency Management System

### 1. Dependabot Configuration (`.github/dependabot.yml`)

Enhanced Dependabot setup with sophisticated dependency grouping:

#### Dependency Groups

- **FastAPI Group**: Core web framework dependencies
    - `fastapi*`, `uvicorn*`, `starlette*`, `pydantic*`
    - Updates: minor and patch versions

- **ML/AI Group**: Machine learning and AI dependencies  
    - `torch*`, `transformers*`, `sentence-transformers*`, `chromadb*`, `numpy*`
    - Updates: patch and security only (conservative approach)

- **Security Group**: Security-critical dependencies
    - `cryptography*`, `pyjwt*`, `requests*`, `urllib3*`, `certifi*`
    - Updates: security, patch, and minor versions

- **Testing Group**: Development and testing tools
    - `pytest*`, `coverage*`, `black*`, `mypy*`, `bandit*`, `safety*`
    - Updates: minor and patch versions

- **Database Group**: Database and storage dependencies
    - `sqlalchemy*`, `alembic*`, `redis*`, `psycopg*`
    - Updates: minor and patch versions

- **Utilities Group**: General utilities and libraries
    - `click*`, `pyyaml*`, `jinja2*`, `pillow*`, `aiofiles*`
    - Updates: minor and patch versions

#### Update Schedule

- **Python Dependencies**: Weekly (Mondays, 6:00 AM UTC)
- **Node.js Dependencies**: Weekly (Tuesdays, 10:00 AM UTC)  
- **GitHub Actions**: Monthly (First Monday, 11:00 AM UTC)
- **Docker Images**: Monthly (Second Monday, 12:00 PM UTC)

#### Safety Rules

- **Major Version Blocks**: Critical dependencies blocked from major updates
    - `torch`, `transformers`, `chromadb`, `numpy`, `fastapi`

- **Known Bad Versions**: Explicit version exclusions
    - `pillow` versions 9.0.0-9.0.1 (security issues)
    - `urllib3` version 2.0.0 (breaking changes)

### 2. Security Scanning Tools

#### Primary Security Scanner (`scripts/security_scanner.py`)

Comprehensive security analysis tool featuring:

- **Safety Integration**: CVE vulnerability scanning
- **Bandit Analysis**: Python code security issues  
- **GitHub Advisories**: Security advisory checking
- **Supply Chain Risk**: Package maintainer and activity analysis
- **Outdated Package Detection**: Security-focused update recommendations

**Usage:**
```bash
# Full security scan
python scripts/security_scanner.py

# JSON output for automation
python scripts/security_scanner.py --format json --output security-report.json
```

#### Dependency Manager (`scripts/dependency_manager.py`)

Full-featured dependency analysis tool providing:

- **Requirements Parsing**: Multi-file requirements analysis
- **Conflict Detection**: Version constraint conflict identification
- **Compatibility Checking**: Installed vs. required version validation
- **License Analysis**: License compliance categorization
- **Update Recommendations**: Intelligent update suggestions
- **Dependency Tree**: Visual dependency relationship mapping

**Usage:**
```bash
# Comprehensive analysis
python scripts/dependency_manager.py

# Generate detailed report
python scripts/dependency_manager.py --format json --output dependency-report.json

# Focus on security vulnerabilities
python scripts/dependency_manager.py --check-security

# Check for available updates
python scripts/dependency_manager.py --check-updates
```

#### Quick Validation (`scripts/validate_dependencies.py`)

Lightweight tool for development workflow:

- **Syntax Validation**: Requirements file format checking
- **Quick Security Check**: Fast vulnerability scanning
- **Conflict Detection**: Basic dependency conflict identification
- **Critical Package Status**: Status of security-sensitive packages

**Usage:**
```bash
# Quick development check
python scripts/validate_dependencies.py

# Perfect for pre-commit hooks
git config core.hooksPath .githooks
```

### 3. GitHub Actions Integration

#### Dependency Security Workflow (`.github/workflows/dependency-security.yml`)

Automated security scanning pipeline:

**Triggers:**

- Weekly schedule (Mondays, 8:00 AM UTC)
- Push to main/develop branches (requirements changes)
- Pull requests (requirements changes)  
- Manual workflow dispatch

**Scan Components:**
1. **Safety Scan**: Python package vulnerability detection
2. **Bandit Scan**: Source code security analysis
3. **pip-audit**: Alternative vulnerability scanning
4. **Outdated Check**: Security-sensitive package updates
5. **SBOM Generation**: Software Bill of Materials creation

**Automated Actions:**
- **PR Comments**: Security scan results in pull request reviews
- **Issue Creation**: Automatic issue creation for critical vulnerabilities
- **SARIF Upload**: Security findings uploaded to GitHub Security tab
- **Report Artifacts**: Detailed reports saved as workflow artifacts

**Fail Conditions:**
- Critical vulnerabilities detected (job fails to prevent deployment)
- Major security issues in production dependencies

### 4. Local Development Integration

#### Pre-commit Hook Setup

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Manual hook run
pre-commit run --all-files
```

#### IDE Integration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.banditEnabled": true,
  "python.linting.mypyEnabled": true,
  "python.linting.pylintEnabled": false,
  "python.formatting.provider": "black"
}
```

#### Development Workflow

1. **Daily Development**:
    ```bash
    # Quick dependency check
    python scripts/validate_dependencies.py
    ```

2. **Before Commits**:
    ```bash
    # Full dependency analysis
    python scripts/dependency_manager.py
    
    # Security-focused scan
    python scripts/security_scanner.py
    ```

3. **Weekly Maintenance**:
    ```bash
    # Check for updates
    pip list --outdated
    
    # Review Dependabot PRs
    # Review security scan results
    ```

---

## Security Best Practices

### 1. Dependency Selection

- **Prefer Well-Maintained Packages**: Active development and community
- **Check License Compatibility**: Ensure license compliance
- **Minimize Dependencies**: Reduce attack surface area
- **Pin Critical Versions**: Lock security-sensitive dependencies

### 2. Update Management

- **Security Updates**: Apply immediately
- **Patch Updates**: Apply regularly (weekly)
- **Minor Updates**: Apply with testing (monthly)
- **Major Updates**: Plan and test thoroughly (quarterly)

### 3. Vulnerability Response

1. **Detection**: Automated scanning identifies vulnerabilities
2. **Assessment**: Evaluate severity and impact
3. **Remediation**: Update packages or apply workarounds
4. **Verification**: Confirm fix effectiveness
5. **Documentation**: Record response actions

### 4. Supply Chain Security

- **Package Verification**: Check package integrity
- **Maintainer Reputation**: Verify package maintainer credibility
- **Source Code Review**: Review critical dependency source code
- **Alternative Assessment**: Identify alternative packages for critical dependencies

---

## Monitoring and Reporting

### 1. Dashboard Metrics

Track key dependency health metrics:

- **Total Dependencies**: Production vs. development
- **Security Vulnerabilities**: By severity level
- **Outdated Packages**: Age and update availability
- **License Compliance**: License type distribution
- **Update Success Rate**: Successful vs. failed updates

### 2. Alerting

Automated alerts for:

- **Critical Vulnerabilities**: Immediate notification
- **High-Severity Issues**: Daily digest
- **Update Failures**: PR merge failures
- **Compliance Violations**: License incompatibilities

### 3. Reporting

Regular reports generated:

- **Weekly**: Dependency health summary
- **Monthly**: Comprehensive security assessment
- **Quarterly**: Supply chain risk analysis
- **Annual**: License compliance audit

---

## Troubleshooting

### Common Issues

#### 1. Dependency Conflicts

**Symptoms**: Installation failures, version incompatibilities

**Solutions**:
```bash
# Identify conflicts
python scripts/dependency_manager.py

# Check specific package versions
pip show package-name

# Create clean environment
pip freeze > old-requirements.txt
pip uninstall -r old-requirements.txt -y
pip install -r requirements.txt
```

#### 2. Security Vulnerabilities

**Symptoms**: Security scan failures, vulnerability alerts

**Solutions**:
```bash
# Identify vulnerabilities
python scripts/security_scanner.py

# Update specific packages
pip install --upgrade package-name

# Check fix effectiveness
safety check
```

#### 3. Outdated Dependencies

**Symptoms**: Performance issues, missing features

**Solutions**:
```bash
# Check outdated packages
pip list --outdated

# Safe update approach
pip install --upgrade package-name==specific-version

# Test thoroughly after updates
python -m pytest tests/
```

#### 4. Build Failures

**Symptoms**: Installation errors, compilation failures

**Solutions**:
```bash
# Clean pip cache
pip cache purge

# Install build dependencies
pip install setuptools wheel

# Use pre-compiled wheels
pip install --only-binary=all package-name
```

### Emergency Procedures

#### 1. Critical Vulnerability Response

1. **Immediate Actions**:
    - Disable affected functionality if possible
    - Apply temporary workarounds
    - Update vulnerable packages

2. **Assessment**:
    - Evaluate impact scope
    - Check for active exploits
    - Review dependent systems

3. **Remediation**:
    - Apply security updates
    - Test functionality
    - Monitor for issues

4. **Communication**:
    - Notify stakeholders
    - Document response actions
    - Update security procedures

#### 2. Dependency System Failure

1. **Immediate Actions**:
    - Switch to manual dependency management
    - Disable automated updates
    - Use known-good dependency snapshots

2. **Diagnosis**:
    - Check system logs
    - Verify tool availability
    - Test individual components

3. **Recovery**:
    - Restore from backups if needed
    - Gradually re-enable automation
    - Verify system functionality

---

## Integration with Development Workflow

### 1. Git Hooks

```bash
#!/bin/sh
# .git/hooks/pre-commit
python scripts/validate_dependencies.py
```

### 2. CI/CD Pipeline

```yaml
# Example integration
- name: Validate Dependencies
  run: python scripts/validate_dependencies.py
  
- name: Security Scan
  run: python scripts/security_scanner.py --format json
```

### 3. Code Review Process

1. **Dependency Changes**: Require security team review
2. **Version Updates**: Test in staging environment
3. **New Dependencies**: Evaluate necessity and security
4. **License Changes**: Legal team approval required

---

## Future Enhancements

### Planned Improvements

1. **Machine Learning Integration**:
   - Predictive vulnerability analysis
   - Automated dependency optimization
   - Risk scoring algorithms

2. **Enhanced Automation**:
   - Intelligent update scheduling
   - Automated testing integration
   - Performance impact analysis

3. **Extended Platform Support**:
   - Additional package ecosystems
   - Container dependency scanning
   - Infrastructure as Code dependencies

4. **Advanced Reporting**:
   - Interactive dashboards
   - Trend analysis
   - Comparative assessments

### Experimental Features

- **Dependency Graph Visualization**: Interactive dependency relationship mapping
- **Performance Impact Analysis**: Update performance impact prediction
- **Alternative Package Suggestions**: AI-powered dependency recommendations
- **Compliance Automation**: Automated license compliance checking

---

## Conclusion

This comprehensive dependency management system provides multiple layers of protection and automation to ensure
the security, stability, and maintainability of the Obsidian AI Agent project. Regular monitoring,
automated scanning, and proactive maintenance help minimize security risks while maintaining development velocity.

For questions or issues with the dependency management system, please:

1. Check this documentation first
2. Run the diagnostic tools provided
3. Review the automated reports and logs
4. Create an issue with detailed information if problems persist

The system is designed to be both comprehensive and maintainable, providing the security assurance needed for
production deployment while supporting efficient development workflows.

