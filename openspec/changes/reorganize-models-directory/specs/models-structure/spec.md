# Specification: Models Directory Reorganization

## Capability Declaration

This specification governs the reorganization of AI model files from `agent/models/` to a dedicated top-level `models/` directory. It establishes requirements for:

- ✅ Directory structure and organization
- ✅ Model file organization by type
- ✅ Configuration path updates
- ✅ Backward compatibility maintenance
- ✅ Testing requirements
- ✅ Documentation standards

---

## Governance Keywords

This specification uses OpenSpec governance language:

- **MUST**: Mandatory requirement
- **SHOULD**: Strong recommendation
- **MAY**: Optional enhancement
- **REQUIREMENT**: Implementation requirement
- **CAPABILITY GOVERNS**: Scope declaration

---

## Directory Structure Specification

### Root-Level Models Directory (MUST)

A dedicated `models/` directory MUST exist at workspace root:

```
workspace/
└── models/                       # Models root (MUST)
    ├── README.md                 # Documentation
    ├── models-manifest.json      # Model registry
    ├── gpt4all/                  # LLM models
    ├── embeddings/               # Embedding models
    ├── vosk/                      # Vosk STT models
    ├── whisper/                   # Whisper STT models
    └── scripts/                   # Management scripts
```

**Requirements**:
- MUST be at workspace root level
- MUST contain organized subdirectories by model type
- MUST include comprehensive documentation
- MUST be version-controllable (with appropriate .gitignore)

### Subdirectory Organization (MUST)

Each model type MUST have dedicated subdirectory:

```
models/
├── gpt4all/
│   ├── models-config.json        # Model registry
│   ├── checksums.json            # Integrity verification
│   └── (model files)
├── embeddings/
│   ├── sentence-transformers/
│   │   ├── all-MiniLM-L6-v2/     # Specific model
│   │   └── metadata.json
│   └── manifests/
├── vosk/
│   ├── vosk-model-small-en-us-0.15/
│   └── metadata.json
├── whisper/
│   ├── model-configs/
│   └── metadata.json
└── scripts/
```

**Requirements**:
- MUST separate models by type (gpt4all, embeddings, etc.)
- MUST use provider names as subdirectories (sentence-transformers)
- MUST include metadata for each model type
- MUST have management scripts in dedicated directory

### Models Manifest (MUST)

Central registry file `models/models-manifest.json` MUST exist:

```json
{
  "manifest_version": "1.0",
  "created": "ISO8601_timestamp",
  "models": {
    "gpt4all": {
      "type": "language_model",
      "provider": "GPT4All",
      "status": "optional",
      "models": []
    },
    "embeddings": {
      "type": "embedding",
      "provider": "sentence-transformers",
      "default": "all-MiniLM-L6-v2",
      "models": {}
    },
    "voice": {
      "vosk": {
        "type": "stt",
        "provider": "Vosk",
        "status": "optional"
      },
      "whisper": {
        "type": "stt",
        "provider": "OpenAI Whisper",
        "status": "optional"
      }
    }
  }
}
```

**Requirements**:
- MUST be valid JSON
- MUST track all model types
- MUST be parseable by agent code
- MUST be user-readable and editable

---

## Configuration Path Specification

### Configuration Updates (MUST)

All configuration MUST use new paths:

```yaml
# Old (INVALID after migration)
models_dir: ./agent/models
embed_model: ./agent/models/embeddings/all-MiniLM-L6-v2

# New (REQUIRED)
models_dir: ./models
embed_model: ./models/embeddings/sentence-transformers/all-MiniLM-L6-v2
vosk_model_path: ./models/vosk/vosk-model-small-en-us-0.15
```

**Requirements**:
- MUST use relative path from workspace root
- MUST point to correct model types
- MUST be consistent across all config files
- MUST support environment variable overrides

### Environment Variables (MUST)

Environment variable support MUST be maintained:

```bash
# Must support these env vars
export MODELS_DIR="./models"
export EMBED_MODEL="./models/embeddings/sentence-transformers/all-MiniLM-L6-v2"
export VOSK_MODEL_PATH="./models/vosk/vosk-model-small-en-us-0.15"
```

**Requirements**:
- MUST support path overrides via env vars
- MUST fall back to config defaults
- MUST validate paths exist
- MUST provide clear error messages

---

## Code Path Updates (MUST)

### Python Code Changes

All Python code MUST use new paths:

```python
# Before (INVALID)
model_path = "agent/models/gpt4all/..."
embed_model = get_setting("embed_model", "agent/models/...")

# After (REQUIRED)
model_path = "models/gpt4all/..."
embed_model = get_setting("embed_model", "models/embeddings/...")
```

**Requirements**:
- MUST update all hardcoded paths
- MUST use config-based paths
- MUST handle relative paths correctly
- MUST validate paths on startup

### Search & Replace Patterns (MUST)

These patterns MUST be replaced:

| Pattern | Replacement | Priority |
|---------|-------------|----------|
| `agent/models/` | `models/` | HIGH |
| `agent\.models` | `.models` config | MEDIUM |
| `modelmanager.py` references | Update logic | HIGH |
| `config.*models_dir` | Update defaults | MEDIUM |

**Requirements**:
- MUST find all occurrences
- MUST verify replacements correct
- MUST test after each replacement
- MUST handle context-specific cases

---

## Backward Compatibility (MUST)

### API Compatibility (MUST)

All agent APIs MUST work identically after migration:

```python
# All of these MUST work the same:
model = get_model("gpt4all")  # Load model
embeddings = embed_text("text")  # Generate embeddings
transcribe = transcribe_audio(audio)  # Voice transcription
```

**Requirements**:
- ✅ All model loading APIs unchanged
- ✅ All model performance identical
- ✅ All model caching working
- ✅ All model fallbacks working
- ✅ All model configuration compatible

### Path Adapter Pattern (MAY)

Legacy paths MAY be supported via adapter:

```python
def get_legacy_path(legacy: str) -> str:
    """Convert legacy agent/models/ path to new path."""
    if legacy.startswith("agent/models/"):
        return legacy.replace("agent/models/", "models/")
    return legacy
```

---

## File Organization (MUST)

### Model File Structure

Each model type MUST organize files clearly:

```
models/gpt4all/
├── models-config.json           # Registry
├── checksums.json               # Verification
├── model-name-1.gguf
├── model-name-2.gguf
└── README.md

models/embeddings/sentence-transformers/
├── all-MiniLM-L6-v2/           # Specific model
│   ├── config.json
│   ├── pytorch_model.bin
│   ├── tokenizer.json
│   └── vocab.txt
└── metadata.json
```

**Requirements**:
- MUST organize by model type
- MUST store model files with correct extensions
- MUST maintain metadata files
- MUST include checksums for integrity

### Documentation Files (MUST)

Required documentation:

1. **models/README.md** (MUST)
   - Directory structure explanation
   - Model download instructions
   - Model verification procedures
   - Setup steps
   - Troubleshooting guide

2. **models/models-manifest.json** (MUST)
   - Central registry
   - Model metadata
   - Version tracking
   - Status indicators

3. **models/gpt4all/models-config.json** (MUST)
   - GPT4All model registry
   - Available models
   - Model properties

---

## Testing Requirements (MUST)

### Path Reference Tests (MUST)

```python
def test_models_directory_exists():
    """Models directory must exist."""
    assert Path("models").exists()

def test_configuration_uses_new_paths():
    """Configuration must use new model paths."""
    config = get_config()
    assert config.models_dir == "./models"
    assert "models/embeddings" in config.embed_model

def test_no_agent_models_references():
    """No code should reference agent/models/."""
    # Search all files for "agent/models/"
    # Assert count == 0
    pass
```

**Coverage**:
- ✅ Directory structure tests
- ✅ Configuration path tests
- ✅ Model loading tests
- ✅ Reference cleanup tests

### Model Loading Tests (MUST)

```python
def test_gpt4all_model_loads():
    """GPT4All models load from new location."""
    model = get_model("gpt4all")
    assert model is not None

def test_embeddings_model_loads():
    """Embedding models load from new location."""
    embeddings = EmbeddingService()
    assert embeddings.get_dimension() > 0

def test_vosk_model_loads():
    """Vosk STT model loads from new location."""
    voice = VoiceService()
    assert await voice.validate()
```

**Requirements**:
- ✅ All model types tested
- ✅ Model loading verified
- ✅ Performance validated
- ✅ Caching functional

### Integration Tests (MUST)

```python
def test_agent_startup_with_new_paths():
    """Agent must start successfully."""
    agent = start_agent(config)
    assert agent.is_ready

def test_search_with_embeddings():
    """Search must work with embeddings from new path."""
    results = search("query")
    assert len(results) > 0

def test_voice_transcription():
    """Voice transcription must work."""
    text = transcribe(audio)
    assert len(text) > 0
```

---

## Performance Requirements (MUST)

### Model Load Time (MUST)

Model loading performance MUST NOT degrade:

- **Requirement**: <5% variance in load time vs old paths
- **Validation**: Benchmark before and after
- **Target**: Same speed or faster

### Startup Time (MUST)

Agent startup MUST NOT be significantly delayed:

- **Requirement**: <10% increase in startup time
- **Validation**: Measure pre/post migration
- **Target**: Same or faster

---

## Script Requirements (MUST)

### Download Script (MUST)

`models/scripts/download-models.ps1` and `.sh` MUST:
- Download models to correct subdirectories
- Verify checksums after download
- Handle network errors gracefully
- Provide progress updates

### Verification Script (MUST)

Verification scripts MUST:
- Check all model files exist
- Verify file checksums
- Report missing models
- Provide fixing instructions

### Cleanup Script (MUST)

Cleanup scripts MUST:
- Remove unused models safely
- Preserve essential models
- Report cleanup results
- Ask for confirmation

---

## Success Criteria

### Functional Success (MUST)
- ✅ `models/` directory exists with proper structure
- ✅ All model files accessible from new location
- ✅ All paths updated throughout project
- ✅ `agent/models/` directory removed
- ✅ All scripts working correctly

### Quality Success (MUST)
- ✅ All tests passing (100%)
- ✅ No broken path references
- ✅ Model loading works for all types
- ✅ Performance unchanged
- ✅ Zero regressions

### Documentation Success (MUST)
- ✅ README comprehensive
- ✅ Manifest accurate
- ✅ Setup guide clear
- ✅ Migration guide complete

---

**Specification Status**: Active  
**Version**: 1.0  
**Last Updated**: October 21, 2025
