#!/usr/bin/env python3
"""
Generate clean text-based diffs comparing restored_* with workflow-step* files.
"""

import difflib
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent


def generate_diff(restored_file, workflow_file, output_file):
    """Generate a clean diff between two files."""
    try:
        with open(restored_file, "r", encoding="utf-8") as f:
            restored_lines = f.readlines()
        with open(workflow_file, "r", encoding="utf-8") as f:
            workflow_lines = f.readlines()

        if restored_lines == workflow_lines:
            return "IDENTICAL"

        # Generate unified diff
        diff = list(
            difflib.unified_diff(
                restored_lines,
                workflow_lines,
                fromfile=f"RESTORED: {restored_file.name}",
                tofile=f"WORKFLOW: {workflow_file.name}",
                lineterm="",
            )
        )

        # Write to file
        with open(output_file, "w", encoding="utf-8") as f:
            for line in diff:
                f.write(line + "\n")

        return f"DIFFERENT ({len(diff)} lines)"

    except Exception as e:
        return f"ERROR: {str(e)}"


def main():
    """Compare all restored_workflow-step files with workflow-step files."""

    print("=" * 80)
    print("GENERATING TEXT-BASED DIFFS: restored_* vs workflow-step*")
    print("=" * 80 + "\n")

    restored_files = sorted(SCRIPTS_DIR.glob("restored_workflow-step*.py"))
    workflow_files = sorted(SCRIPTS_DIR.glob("workflow-step*.py"))

    if len(restored_files) != len(workflow_files):
        print("ERROR: Mismatch in file counts!")
        print(f"  Restored files: {len(restored_files)}")
        print(f"  Workflow files: {len(workflow_files)}")
        return

    total_diffs = 0
    total_size = 0

    for restored_file, workflow_file in zip(restored_files, workflow_files):
        output_file = (
            SCRIPTS_DIR / f"RESTORED_VS_WORKFLOW_{restored_file.stem[9:]}.diff"
        )

        result = generate_diff(restored_file, workflow_file, output_file)

        if "IDENTICAL" in result:
            status = "✅"
        elif "DIFFERENT" in result:
            status = "❌"
            total_diffs += 1
            total_size += output_file.stat().st_size
        else:
            status = "⚠️"

        print(f"{status} {restored_file.name}")
        print(f"   vs {workflow_file.name}")
        print(f"   → {output_file.name}")
        print(f"   {result}\n")

    print("=" * 80)
    print(f"SUMMARY: {total_diffs} files different")
    print(f"Total diff size: {total_size:,} bytes ({total_size/1024:.2f} KB)")
    print("=" * 80)


if __name__ == "__main__":
    main()
