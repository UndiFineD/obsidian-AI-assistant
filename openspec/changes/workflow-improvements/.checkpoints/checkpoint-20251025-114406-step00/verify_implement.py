#!/usr/bin/env python3
"""Direct test of implement.py execution"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import implement

print("=" * 70)
print("IMPLEMENT.PY EXECUTION TESTS")
print("=" * 70)

print("\n[TEST 1] Lane Selection Execution")
r1 = implement.implement_lane_selection_python()
print(f"Result: {r1}")

print("\n[TEST 2] Quality Gates Execution")
r2 = implement.create_quality_gates_module()
print(f"Result: {r2}")

print("\n[TEST 3] Status JSON Execution")
r3 = implement.create_status_json_template()
print(f"Result: {r3}")

print("\n[TEST 4] File Verification")
qg_file = implement.scripts_root / "quality_gates.py"
wf_file = implement.scripts_root / "workflow.py"

print(f"quality_gates.py exists: {qg_file.exists()}")
if qg_file.exists():
    print(f"quality_gates.py size: {qg_file.stat().st_size} bytes")
    content = qg_file.read_text()
    has_class = "class QualityGates" in content
    has_methods = all(
        f"def {m}" in content
        for m in ["run_all", "run_ruff", "run_mypy", "run_pytest", "run_bandit"]
    )
    print(f"  Has QualityGates class: {has_class}")
    print(f"  Has all 5+ methods: {has_methods}")

print(f"\nworkflow.py exists: {wf_file.exists()}")
if wf_file.exists():
    try:
        content = wf_file.read_text(encoding="utf-8", errors="replace")
        has_lane = "LANE_MAPPING" in content
        print(f"  Has LANE_MAPPING: {has_lane}")
        if has_lane:
            lanes = [l for l in ["docs", "standard", "heavy"] if f'"{l}"' in content]
            print(f"  Defined lanes: {lanes}")
    except Exception as e:
        print(f"  Error reading: {e}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
all_pass = r1 and r2 and r3 and qg_file.exists() and wf_file.exists()
print(f"All phases executed: {all_pass}")
print(f"All files created: {qg_file.exists() and wf_file.exists()}")
print("=" * 70)
