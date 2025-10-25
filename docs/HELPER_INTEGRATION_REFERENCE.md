# Helper Integration Reference

This document provides a comprehensive reference for how helpers are integrated across all 13 workflow steps. Each step follows consistent patterns for importing and using helper modules.

## Core Helper Modules

### 1. workflow-helpers.py (Always Required)
**Import Pattern:**
```python
import importlib.util
spec = importlib.util.spec_from_file_location(
    "workflow_helpers",
    SCRIPT_DIR / "workflow-helpers.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
```

**Core Functions Used in All Steps:**
- `helpers.write_step(step_num, description)` - Display step header
- `helpers.write_info(message)` - Log informational messages
- `helpers.write_success(message)` - Log success messages
- `helpers.write_warning(message)` - Log warnings
- `helpers.write_error(message)` - Log errors
- `helpers.set_content_atomic(file_path, content)` - Write files atomically
- `helpers.validate_step_artifacts(change_path, step_num)` - Validate artifacts
- `helpers.show_changes(changes_dir)` - Show git changes
- `helpers.detect_next_step(change_path)` - Detect next workflow step

### 2. progress_indicators.py (Conditionally Imported)
**Import Pattern:**
```python
try:
    import progress_indicators as progress
except ImportError:
    progress = None
```

**Usage Pattern:**
```python
if progress and hasattr(progress, 'spinner'):
    with progress.spinner("Description", "Complete message"):
        # Long-running operation
elif progress and hasattr(progress, 'ProgressBar'):
    pb = progress.ProgressBar(total_steps, "Progress message", width=40)
    pb.set(current_step)
    pb.complete()
```

**Used in Steps:** 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

### 3. status_tracker.py (Conditionally Imported)
**Import Pattern:**
```python
try:
    from status_tracker import StatusTracker, create_tracker
    STATUS_TRACKER_AVAILABLE = True
except ImportError:
    STATUS_TRACKER_AVAILABLE = False
    StatusTracker = None
    create_tracker = None
```

**Usage Pattern:**
```python
status_tracker = None
if STATUS_TRACKER_AVAILABLE:
    try:
        status_tracker = create_tracker(
            change_path.name,
            lane="standard",
            status_file=change_path / ".checkpoints" / "status.json",
        )
        status_tracker.start_stage(step_num, "Stage description")
        # ... operations ...
        status_tracker.complete_stage(step_num, success=True, metrics={...})
    except Exception as e:
        helpers.write_warning(f"Could not initialize status tracker: {e}")
```

**Used in Steps:** 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

### 4. Document Validators/Generators (Conditionally Imported from helpers)
**Import Pattern:**
```python
try:
    DocumentValidator = helpers.DocumentValidator
    DocumentGenerator = helpers.DocumentGenerator
    TemplateManager = helpers.TemplateManager
    DOCUMENT_VALIDATOR_AVAILABLE = True
    DOCUMENT_GENERATOR_AVAILABLE = True
    TEMPLATE_MANAGER_AVAILABLE = True
except AttributeError:
    DOCUMENT_VALIDATOR_AVAILABLE = False
    DOCUMENT_GENERATOR_AVAILABLE = False
    TEMPLATE_MANAGER_AVAILABLE = False
    DocumentValidator = None
    DocumentGenerator = None
    TemplateManager = None
```

**Usage Pattern:**
```python
# Document validation
if DOCUMENT_VALIDATOR_AVAILABLE and DocumentValidator:
    validator = DocumentValidator()
    if not validator.validate_file_creation(change_path, "filename.md"):
        helpers.write_error("Document validation failed")

# Document generation
if DOCUMENT_GENERATOR_AVAILABLE and DocumentGenerator:
    generator = DocumentGenerator()
    content = generator.generate_from_template(template_name, context)

# Template management
if TEMPLATE_MANAGER_AVAILABLE and TemplateManager:
    template_manager = TemplateManager()
    content = template_manager.render_template(template_path, variables)
```

**Used in Steps:** 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12

## Step-Specific Helper Integration

### Step 0: Create TODOs
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for todo generation)
- Status tracker (stage tracking)
- Document generator (todo.md generation)
- Template manager (todo template rendering)

**Key Integration Points:**
```python
# Initialize status tracker
status_tracker.start_stage(0, "Create TODOs")

# Generate todos with progress
with progress.spinner("Generating comprehensive TODO list", "TODOs generated"):
    todos_content = _generate_comprehensive_todos(change_path, title)

# Use template manager for rendering
if TEMPLATE_MANAGER_AVAILABLE and TemplateManager:
    template_manager = TemplateManager()
    content = template_manager.render_todo_template(context)
```

### Step 1: Version Bump
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for version updates)
- Status tracker (stage tracking)
- Document validator (version_snapshot.md validation)
- Template manager (version snapshot rendering)
- VersionManager (direct import for version operations)

**Key Integration Points:**
```python
# Direct import of VersionManager
from version_manager import VersionManager

# Version bump with progress
with progress.spinner("Updating version files", "Version files updated"):
    updated_files = vm.update_all_versions(new_version)

# Template rendering for snapshot
content = template_manager.render_version_snapshot(captured_time=now, ...)
```

### Step 2: Proposal Review
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for proposal generation)
- Status tracker (stage tracking)
- Document generator (proposal.md generation)
- Template manager (proposal template rendering)

**Key Integration Points:**
```python
# Generate proposal with document generator
if DOCUMENT_GENERATOR_AVAILABLE and DocumentGenerator:
    generator = DocumentGenerator()
    proposal_content = generator.generate_proposal_from_title(title, owner)
```

### Step 3: Specification Definition
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for spec generation)
- Status tracker (stage tracking)
- Document generator (spec.md generation)
- Template manager (spec template rendering)

**Key Integration Points:**
```python
# Generate spec from templates
if TEMPLATE_MANAGER_AVAILABLE and TemplateManager:
    template_manager = TemplateManager()
    content = template_manager.render_spec_template(context)
```

### Step 4: Task Breakdown
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for task breakdown)
- Status tracker (stage tracking)
- Document generator (tasks.md generation)
- Template manager (task template rendering)

**Key Integration Points:**
```python
# Generate detailed task breakdown
if DOCUMENT_GENERATOR_AVAILABLE and DocumentGenerator:
    generator = DocumentGenerator()
    tasks_content = generator.generate_task_breakdown(proposal_path, spec_path)
```

### Step 5: Implementation Checklist
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for checklist generation)
- Status tracker (stage tracking)
- Document generator (checklist generation)
- Template manager (checklist template rendering)

**Key Integration Points:**
```python
# Generate implementation checklist
if TEMPLATE_MANAGER_AVAILABLE and TemplateManager:
    template_manager = TemplateManager()
    checklist_content = template_manager.render_checklist_template(context)
```

### Step 6: Script Generation
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for script generation)
- Status tracker (stage tracking)
- Document generator (script generation)
- Template manager (script template rendering)

**Key Integration Points:**
```python
# Generate test.py and implement.py scripts
if DOCUMENT_GENERATOR_AVAILABLE and DocumentGenerator:
    generator = DocumentGenerator()
    test_script = generator.generate_test_script(change_path)
    impl_script = generator.generate_implementation_script(change_path)
```

### Step 7: Document Review
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for review generation)
- Status tracker (stage tracking)
- Document validator (comprehensive validation)
- Template manager (review template rendering)

**Key Integration Points:**
```python
# Comprehensive document validation
if DOCUMENT_VALIDATOR_AVAILABLE and DocumentValidator:
    validator = DocumentValidator()
    validation_results = validator.validate_all_documents(change_path)
```

### Step 8: Testing & Quality Gates
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for testing)
- Status tracker (stage tracking)
- QualityGates (direct import for gate execution)

**Key Integration Points:**
```python
# Direct import of quality gates
spec_qg = importlib.util.spec_from_file_location(
    "quality_gates",
    SCRIPT_DIR / "quality_gates.py",
)
quality_gates_module = importlib.util.module_from_spec(spec_qg)
spec_qg.loader.exec_module(quality_gates_module)

# Run quality gates
gates = quality_gates_module.QualityGates(lane=lane)
success = gates.run_all()
```

### Steps 9-12: Implementation Phases
**Helpers Used:**
- Core helpers (always)
- Progress indicators (spinner for implementation)
- Status tracker (stage tracking)
- Document generator (implementation notes)
- Template manager (implementation templates)

**Key Integration Points:**
```python
# Implementation tracking with status updates
status_tracker.start_stage(step_num, f"Implementation Phase {phase_num}")
# ... implementation work ...
status_tracker.complete_stage(step_num, success=True, metrics=metrics)
```

## Helper Availability Flags

All steps use consistent availability flags for conditional helper usage:

```python
# Progress indicators
PROGRESS_AVAILABLE = progress is not None

# Status tracking
STATUS_TRACKER_AVAILABLE = StatusTracker is not None

# Document operations
DOCUMENT_VALIDATOR_AVAILABLE = DocumentValidator is not None
DOCUMENT_GENERATOR_AVAILABLE = DocumentGenerator is not None
TEMPLATE_MANAGER_AVAILABLE = TemplateManager is not None
```

## Error Handling Patterns

All steps follow consistent error handling for optional helpers:

```python
# Safe helper initialization
try:
    status_tracker = create_tracker(...)
except Exception as e:
    helpers.write_warning(f"Could not initialize status tracker: {e}")
    status_tracker = None

# Graceful degradation
if status_tracker:
    status_tracker.start_stage(step_num, description)
    # ... operations ...
    status_tracker.complete_stage(step_num, success=success)
```

## Performance Considerations

- **Lazy Loading**: Helpers are imported only when needed
- **Conditional Execution**: Expensive operations only run if helpers are available
- **Fallback Behavior**: All steps work without optional helpers
- **Progress Feedback**: Visual progress indicators for long-running operations
- **Status Tracking**: Comprehensive metrics collection for monitoring

## Testing Integration

Helper integration is tested through:
- **Unit Tests**: Individual helper function testing
- **Integration Tests**: End-to-end workflow testing with helpers
- **Mocking**: Optional helpers are mocked in tests
- **Fallback Testing**: Verification that steps work without optional helpers

## Maintenance Guidelines

When adding new helpers or modifying existing ones:

1. **Follow Import Patterns**: Use the established import patterns for consistency
2. **Add Availability Flags**: Create clear availability flags for conditional usage
3. **Update Documentation**: Document new helpers in this reference
4. **Test Fallbacks**: Ensure steps work without new optional helpers
5. **Update All Steps**: Apply changes consistently across all workflow steps

This reference ensures consistent helper integration across the entire workflow system while maintaining flexibility and robustness.</content>
<parameter name="filePath">c:\Users\kdejo\DEV\obsidian-llm-assistant\obsidian-AI-assistant\docs\HELPER_INTEGRATION_REFERENCE.md