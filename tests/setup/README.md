# Setup Script Tests

This directory contains comprehensive test suites for the PowerShell (`setup.ps1`) and Bash (`setup.sh`) setup scripts.

## Test Files

- `test_setup_ps1.ps1` - Pester tests for PowerShell setup script
- `test_setup_sh.bats` - BATS tests for Bash setup script

## Prerequisites

### For PowerShell Tests (Windows)

Install Pester testing framework:

```powershell
Install-Module -Name Pester -Force -SkipPublisherCheck
```

### For Bash Tests (Linux/macOS/WSL)

Install BATS (Bash Automated Testing System):

**Using npm:**
```bash
npm install -g bats
```

**Using package manager:**

Ubuntu/Debian:
```bash
sudo apt-get install bats
```

macOS (Homebrew):
```bash
brew install bats-core
```

## Running the Tests

### PowerShell Tests

```powershell
# Navigate to the setup tests directory
cd tests/setup

# Run all Pester tests
Invoke-Pester test_setup_ps1.ps1 -Verbose

# Run with detailed output
Invoke-Pester test_setup_ps1.ps1 -Output Detailed

# Generate coverage report (if available)
Invoke-Pester test_setup_ps1.ps1 -CodeCoverage
```

### Bash Tests

```bash
# Navigate to the setup tests directory
cd tests/setup

# Run all BATS tests
bats test_setup_sh.bats

# Run with verbose output
bats -t test_setup_sh.bats

# Run specific test
bats -f "virtual environment" test_setup_sh.bats
```

## Test Coverage

### PowerShell Setup Script Tests (`test_setup_ps1.ps1`)

The tests cover:

1. **Configuration Validation**
   - Python executable configuration
   - Node.js download URL validation
   - Virtual environment settings
   - Requirements file configuration

2. **Python Environment Setup**
   - Python installation detection
   - Virtual environment creation
   - Activation script validation
   - Missing dependencies handling

3. **Requirements Installation**
   - Requirements.txt validation
   - Fallback dependencies
   - Error handling for missing files

4. **Hugging Face Integration**
   - Token prompting and validation
   - Empty token handling
   - Login error management

5. **Node.js Installation**
   - Existing installation detection
   - TLS configuration for downloads
   - Download and extraction process
   - PATH configuration
   - Error handling

6. **Error Handling**
   - Exit codes and error messages
   - Try-catch block validation
   - Graceful failure scenarios

7. **Security and Best Practices**
   - Secure download methods
   - Temporary file cleanup
   - Input validation
   - Path handling

### Bash Setup Script Tests (`test_setup_sh.bats`)

The tests cover:

1. **Script Structure**
   - Shebang validation
   - Error handling with `set -e`
   - Executable permissions

2. **Virtual Environment Management**
   - Environment creation with Python3
   - Activation process
   - Directory structure validation

3. **Dependency Installation**
   - Pip upgrade process
   - Required package installation
   - ML and web scraping dependencies

4. **GPU/CPU Detection**
   - CUDA availability checking
   - Torch GPU detection logic

5. **Hugging Face Token Management**
   - Token prompting
   - .env file creation and management
   - Empty token handling

6. **Model Downloads**
   - Models directory creation
   - LLaMA and GPT4All model downloads
   - Existing model checks
   - Download URL validation

7. **Obsidian Plugin Building**
   - Plugin directory validation
   - npm install and build process
   - Missing directory handling

8. **Security Validation**
   - Safe variable quoting
   - HTTPS URL validation
   - Dangerous command detection
   - File operation safety

## Test Isolation

Both test suites use isolated test environments:

- **PowerShell tests**: Create temporary workspace in `$env:TEMP`
- **Bash tests**: Create temporary workspace in `/tmp`

This ensures:
- No interference with actual project files
- Safe testing of file operations
- Reproducible test results
- Easy cleanup after test completion

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

### GitHub Actions Example

```yaml
# .github/workflows/setup-tests.yml
name: Setup Script Tests

on: [push, pull_request]

jobs:
  test-powershell:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Pester
        run: Install-Module -Name Pester -Force -SkipPublisherCheck
      - name: Run PowerShell Tests
        run: Invoke-Pester tests/setup/test_setup_ps1.ps1 -Verbose

  test-bash:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install BATS
        run: sudo apt-get install bats
      - name: Run Bash Tests
        run: bats tests/setup/test_setup_sh.bats
```

## Troubleshooting

### Common Issues

1. **Pester Not Found (Windows)**
   ```powershell
   # Update PowerShell execution policy if needed
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   
   # Install Pester with correct parameters
   Install-Module -Name Pester -Force -SkipPublisherCheck -Scope CurrentUser
   ```

2. **BATS Not Found (Linux/macOS)**
   ```bash
   # Ensure BATS is in PATH
   which bats
   
   # Install using package manager or npm
   npm install -g bats
   ```

3. **Permission Denied (Linux/macOS)**
   ```bash
   # Make test files executable
   chmod +x tests/setup/test_setup_sh.bats
   ```

4. **Test Workspace Cleanup**
   If tests fail to clean up temporary directories:
   ```bash
   # Manual cleanup
   rm -rf /tmp/obsidian-ai-test-*
   ```

### Debugging Tests

To debug failing tests:

1. **PowerShell**: Add `-Verbose` flag to see detailed output
2. **BATS**: Use `-t` flag for verbose output and `--verbose-run` for command tracing

## Contributing

When modifying setup scripts:

1. Update corresponding tests to reflect changes
2. Run tests locally before committing
3. Add new test cases for new functionality
4. Maintain test isolation and cleanup
5. Document any new test requirements