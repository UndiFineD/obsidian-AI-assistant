# AI Models Directory

This directory contains AI models and model metadata for the Obsidian AI Agent project.

## Overview

Models are organized into logical categories by type and provider. Each model can be downloaded on-demand or during initial setup. Models are optional unless marked as "recommended".

## Directory Structure

```
models/
├── gpt4all/                           # LLM models (GPT4All backend)
│   └── *.gguf                         # Model files
├── embeddings/
│   └── sentence-transformers/        # Embedding models
│       └── all-MiniLM-L6-v2/        # Default embedding model
├── vosk/                              # Speech recognition models
│   └── vosk-model-small-en-us-0.15/
├── whisper/                           # Speech transcription models
│   └── *.pt                           # Whisper model files
├── scripts/                           # Model management scripts
│   ├── download-models.ps1           # PowerShell: Download all models
│   ├── download-models.sh            # Bash: Download all models
│   ├── verify-models.ps1             # PowerShell: Verify models
│   ├── verify-models.sh              # Bash: Verify models
│   ├── cleanup-models.ps1            # PowerShell: Cleanup old models
│   └── cleanup-models.sh             # Bash: Cleanup old models
├── models-manifest.json               # Model registry and metadata
└── README.md                          # This file
```

## Model Types

### Language Models (LLM)
- **Provider**: GPT4All
- **Directory**: `gpt4all/`
- **Default**: Mistral-7B
- **Optional**: Yes
- **Purpose**: Question answering, text generation

### Embedding Models
- **Provider**: Sentence Transformers
- **Directory**: `embeddings/sentence-transformers/`
- **Default**: all-MiniLM-L6-v2
- **Optional**: No (required for semantic search)
- **Purpose**: Converting text to vector embeddings for search

### Voice Recognition
- **Provider**: Vosk
- **Directory**: `vosk/`
- **Default**: en-US small model
- **Optional**: Yes
- **Purpose**: Real-time speech recognition

### Transcription
- **Provider**: OpenAI Whisper
- **Directory**: `whisper/`
- **Optional**: Yes
- **Purpose**: Accurate speech-to-text conversion

## Quick Start

### Download Models

#### Windows (PowerShell)
```powershell
cd models/scripts
.\download-models.ps1
```

#### Linux/macOS (Bash)
```bash
cd models/scripts
./download-models.sh
```

### Verify Models

#### Windows (PowerShell)
```powershell
cd models/scripts
.\verify-models.ps1
```

#### Linux/macOS (Bash)
```bash
cd models/scripts
./verify-models.sh
```

## Model Registry

All models are registered in `models-manifest.json`. This file includes:
- Model names and locations
- File sizes and formats
- Provider information
- Status (recommended, optional, required)
- Download and verification instructions

## Storage Requirements

| Model Type | Size | Required | Status |
|-----------|------|----------|--------|
| Embeddings (all-MiniLM-L6-v2) | ~90 MB | Yes | Recommended |
| LLM (Mistral-7B) | ~4 GB | No | Optional |
| Voice (Vosk) | ~45 MB | No | Optional |
| Transcription (Whisper) | ~140 MB | No | Optional |
| **Total (all models)** | **~4.3 GB** | - | - |

## Configuration

### Default Paths

Models are configured in `agent/config.yaml`:

```yaml
models:
  models_dir: ./models              # Root models directory
  gpt4all_dir: ./models/gpt4all    # LLM models
  embed_model: all-MiniLM-L6-v2    # Default embedding model
  embed_model_dir: ./models/embeddings/sentence-transformers
  vosk_model_path: ./models/vosk/vosk-model-small-en-us-0.15
  whisper_model: base              # Whisper model variant
```

### Environment Variables

Optional environment variables for custom model paths:

```bash
MODELS_DIR=./models
GPTALL_MODELS_DIR=./models/gpt4all
EMBEDDING_MODEL_DIR=./models/embeddings/sentence-transformers
VOSK_MODEL_PATH=./models/vosk/vosk-model-small-en-us-0.15
```

## Troubleshooting

### Models Not Found

1. **Check directory exists**: `ls -la models/` (Linux/Mac) or `dir models/` (Windows)
2. **Verify paths**: Check `agent/config.yaml` for correct model paths
3. **Download models**: Run `./models/scripts/download-models.*`
4. **Check permissions**: Ensure read permissions on model files

### Model Loading Errors

1. **Check model file integrity**: Run `./models/scripts/verify-models.*`
2. **Check disk space**: Ensure sufficient disk space for models
3. **Check Python version**: Requires Python 3.11+
4. **Check dependencies**: Run `pip install -r requirements.txt`

### Performance Issues

1. **Model loading slow**: First load caches model, subsequent loads are faster
2. **High memory usage**: Some models require 4+ GB RAM
3. **GPU support**: Install CUDA for GPU-accelerated inference (optional)

## Contributing

### Adding New Models

1. Create subdirectory in appropriate category: `models/<category>/<model_name>/`
2. Add model files to subdirectory
3. Update `models-manifest.json` with model metadata
4. Update this README with model details
5. Create/update download script for model

### Model Guidelines

- Keep models organized by type and provider
- Document model purpose and requirements in manifest
- Provide download scripts for reproducibility
- Include verification checksums where possible
- Document any special setup requirements

## Support

For model-related issues:

1. Check troubleshooting section above
2. Review `models-manifest.json` for available models
3. Check configuration in `agent/config.yaml`
4. Consult project documentation in `docs/`
5. Open GitHub issue with detailed error information

---

**Last Updated**: October 21, 2025  
**Model Structure Version**: 1.0  
**Compatible With**: Agent v0.1.32+
