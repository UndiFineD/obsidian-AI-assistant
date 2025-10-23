#!/usr/bin/env python3
"""Test script to validate test_plan.md generation in step 6"""

import sys
import importlib.util
from pathlib import Path

# Load the module properly
spec = importlib.util.spec_from_file_location("workflow_step06", "scripts/workflow-step06.py")
module = importlib.util.module_from_spec(spec)
sys.modules["workflow_step06"] = module
spec.loader.exec_module(module)

# Call invoke_step6
test_dir = Path("openspec/changes/test-step6")
print(f"Running invoke_step6 with test directory: {test_dir}")
print(f"Existing files before: {list(test_dir.glob('*.md'))}")

result = module.invoke_step6(test_dir, dry_run=False)

print(f"\nResult: {result}")
print(f"Files after: {list(test_dir.glob('*.md'))}")

# Check test_plan.md
test_plan_path = test_dir / "test_plan.md"
if test_plan_path.exists():
    size = test_plan_path.stat().st_size
    print(f"\n✅ SUCCESS: test_plan.md created ({size:,} bytes)")

    # Show first 1000 chars
    with open(test_plan_path, "r", encoding="utf-8") as f:
        content = f.read(1000)
        print("\n--- First 1000 chars ---")
        print(content)
        print("...")
else:
    print(f"\n❌ ERROR: test_plan.md not created")
    print(f"Dir contents: {list(test_dir.glob('*'))}")
    sys.exit(1)
