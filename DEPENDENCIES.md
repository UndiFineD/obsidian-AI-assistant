# Dependency Management for Obsidian AI Assistant

This document explains the dependency structure and installation procedures for the Obsidian AI Assistant project.

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
2. Clear pip cache: `pip cache purge`
3. Reinstall with specific index URL as shown above

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
