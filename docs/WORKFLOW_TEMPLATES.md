# Workflow Templates Guide

## Overview

The OpenSpec workflow now supports **proposal templates** for common change scenarios. Templates provide pre-structured content that matches the type of work you're doing, reducing initial setup time and ensuring consistency.

## Available Templates

### 1. Feature Template (`--template feature`)

**Use for**: New functionality or capability additions

**Sections included**:
- Background & Current State
- Implementation Approach
- Success Metrics
- Risks & Mitigation
- Phased Rollout Plan

**Example**:
```bash
python workflow.py --change-id add-export-feature --template feature
```

### 2. Bugfix Template (`--template bugfix`)

**Use for**: Fixing incorrect behavior or defects

**Sections included**:
- Bug Description & Impact
- Reproduction Steps
- Root Cause Analysis
- Fix Approach & Alternatives
- Testing Strategy
- Rollout Plan

**Example**:
```bash
python workflow.py --change-id fix-null-pointer-error --template bugfix
```

### 3. Documentation Template (`--template docs`)

**Use for**: Documentation creation or updates

**Sections included**:
- Documentation Gap Analysis
- Target Audience
- Content Plan
- Quality Standards
- Success Metrics

**Example**:
```bash
python workflow.py --change-id update-api-docs --template docs
```

### 4. Refactor Template (`--template refactor`)

**Use for**: Code quality improvements without behavior changes

**Sections included**:
- Technical Debt Description
- Current vs. Proposed Architecture
- Migration Strategy
- Risk Assessment
- Testing Strategy
- Benefits Analysis

**Example**:
```bash
python workflow.py --change-id refactor-authentication --template refactor
```

### 5. Default Template (`--template default` or omit `--template`)

**Use for**: Generic changes or when you want a minimal starting point

**Sections included**:
- Context
- What Changes
- Goals / Non-Goals
- Stakeholders
- Timeline

**Example**:
```bash
python workflow.py --change-id my-change  # Uses default template
```

## Usage

### Starting a New Workflow with Template

```bash
# Full workflow with specific template
python workflow.py --change-id my-feature --template feature --title "Add User Export"

# Single step with template
python workflow.py --change-id my-bugfix --template bugfix --step 2
```

### Interactive Workflow

When running the full workflow, the template is automatically used in Step 2 (Proposal):

```bash
python workflow.py --change-id enhance-logging --template feature
```

Output:
```
═════════  STEP 2: Proposal ═════════
Using 'feature' template: New functionality or capability addition
⠋ Creating proposal.md from template... ✓ Proposal created from template
⠋ Validating proposal.md... ✓ Validation complete
Step 2 completed
```

### Template Selection Decision Tree

```
Are you adding new functionality?
├─ Yes → Use `--template feature`
└─ No → Is this fixing a bug?
    ├─ Yes → Use `--template bugfix`
    └─ No → Is this documentation work?
        ├─ Yes → Use `--template docs`
        └─ No → Is this refactoring existing code?
            ├─ Yes → Use `--template refactor`
            └─ No → Use `--template default` or omit flag
```

## Template Customization

### Modifying Existing Templates

Templates are stored in `openspec/templates/`:
- `proposal-feature.md` - Feature template
- `proposal-bugfix.md` - Bugfix template
- `proposal-docs.md` - Documentation template
- `proposal-refactor.md` - Refactor template

Edit these files directly to customize sections, add prompts, or modify structure.

### Placeholders

Templates support automatic placeholder substitution:
- `<date>` → Current UTC date (YYYY-MM-DD)
- `<owner>` → Converted to `[owner]` (user fills in)
- `<reviewers>` → Converted to `[reviewers]` (user fills in)
- `[Feature Name]` → Replaced with `--title` value if provided

### Adding New Templates

1. Create template file in `openspec/templates/`:
   ```bash
   # Example: proposal-experiment.md
   ```

2. Register in `scripts/workflow-helpers.py`:
   ```python
   class TemplateManager:
       TEMPLATES = {
           'feature': 'proposal-feature.md',
           'bugfix': 'proposal-bugfix.md',
           'docs': 'proposal-docs.md',
           'refactor': 'proposal-refactor.md',
           'experiment': 'proposal-experiment.md',  # New template
           'default': None
       }
   ```

3. Add description:
   ```python
   descriptions = {
       'experiment': 'Experimental features or A/B tests',
       # ...
   }
   ```

4. Update argparse choices in `scripts/workflow.py`:
   ```python
   parser.add_argument(
       '--template',
       choices=['feature', 'bugfix', 'docs', 'refactor', 'experiment', 'default'],
       # ...
   )
   ```

## Benefits

### Time Savings
- **50-70% faster** initial proposal creation
- Pre-filled sections eliminate "blank page" syndrome
- Consistent structure across all changes

### Quality Improvements
- Ensures all critical sections are considered
- Provides prompts for important information
- Reduces review cycles through completeness

### Team Alignment
- Common vocabulary across change types
- Clear expectations for proposal content
- Easier for reviewers to navigate familiar structure

## Examples

### Feature Example: Add Data Export

```bash
python workflow.py --change-id add-data-export --template feature --title "User Data Export API"
```

Generates proposal with sections like:
- **Context**: Current system limitations for data portability
- **Implementation Approach**: REST API with async job processing
- **Success Metrics**: Adoption rate, performance targets
- **Phased Rollout**: Beta users → gradual rollout

### Bugfix Example: Fix Memory Leak

```bash
python workflow.py --change-id fix-memory-leak --template bugfix --title "Fix WebSocket Connection Leak"
```

Generates proposal with sections like:
- **Bug Description**: Memory usage grows unbounded
- **Reproduction Steps**: 1-2-3 steps to reproduce
- **Root Cause**: Missing connection cleanup
- **Fix Approach**: Add cleanup in disconnect handler

## Best Practices

1. **Choose the Right Template**: Match template to change type for best results
2. **Don't Over-Customize**: Templates provide structure - add details, don't rewrite
3. **Fill Placeholders Early**: Replace `[owner]`, `[reviewers]` etc. immediately
4. **Review Validation Warnings**: Templates are starting points, ensure completeness
5. **Iterate**: Edit proposal after generation if template doesn't perfectly fit

## Template Comparison

| Template | Sections | Typical Size | Best For |
|----------|----------|--------------|----------|
| Feature | 9+ sections | 200-400 lines | New capabilities, features |
| Bugfix | 8+ sections | 150-300 lines | Bug fixes, defect resolution |
| Docs | 7+ sections | 150-250 lines | Documentation work |
| Refactor | 9+ sections | 200-350 lines | Code quality improvements |
| Default | 5 sections | 50-100 lines | Simple changes, quick starts |

## Troubleshooting

### Template Not Found
```
Template file not found: .../proposal-feature.md, using default
```

**Solution**: Ensure template file exists in `openspec/templates/`

### Wrong Template Selected
If you realize you picked the wrong template after Step 2 runs:

1. Delete `proposal.md`: `rm openspec/changes/my-change/proposal.md`
2. Re-run Step 2 with correct template:
   ```bash
   python workflow.py --change-id my-change --template bugfix --step 2
   ```

### Validation Errors After Template
Templates provide structure but may have placeholder warnings:

```
Proposal has 2 warning(s):
  ⚠ Template placeholders remain (e.g., <...>)
```

**Solution**: Fill in `[owner]`, `[reviewers]`, and other bracketed placeholders

## Advanced Usage

### Dry Run with Template
Preview template output without creating files:

```bash
python workflow.py --change-id test --template feature --step 2 --dry-run
```

### Programmatic Template Access

From Python code:

```python
from workflow_helpers import TemplateManager

# List available templates
templates = TemplateManager.get_available_templates()
# ['feature', 'bugfix', 'docs', 'refactor', 'default']

# Get template description
desc = TemplateManager.describe_template('feature')
# "New functionality or capability addition"

# Load template content
content = TemplateManager.load_template('bugfix', title="Fix Memory Leak")
```

## Next Steps

After creating a proposal from a template:

1. **Review Generated Content**: Templates are starting points
2. **Fill Placeholders**: Replace `[owner]`, `[description]`, etc.
3. **Add Details**: Expand sections with specific context
4. **Run Validation**: `python workflow.py --change-id <id> --step 2`
5. **Continue Workflow**: Move to Step 3 (Specification)

---

**Template System Version**: 1.0  
**Last Updated**: October 20, 2025  
**Feedback**: Report issues or suggest improvements via GitHub issues
