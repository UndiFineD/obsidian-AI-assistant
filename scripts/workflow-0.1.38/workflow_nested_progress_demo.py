#!/usr/bin/env python3
"""
Demo: Nested Workflow Progress Integration

Shows how the nested progress system would work when running
multiple workflow steps sequentially.
"""

import sys
import time
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from progress_indicators import StatusTracker, progress_bar, spinner, workflow_progress


def demo_workflow_execution():
    """Simulate running multiple workflow steps with nested progress."""

    print("=" * 70)
    print("Nested Workflow Progress Demo")
    print("=" * 70)
    print()
    print("Simulating workflow with 5 steps, each with its own progress...")
    print()

    # Define workflow steps
    steps = [
        ("Validation", "Validating proposal and spec documents"),
        ("Spec Generation", "Generating capability specification"),
        ("Task Generation", "Extracting tasks from documents"),
        ("Test Generation", "Creating test plan"),
        ("Script Generation", "Generating test and implementation scripts"),
    ]

    with workflow_progress(len(steps), "OpenSpec Workflow") as wp:
        for step_num, (step_name, step_desc) in enumerate(steps, 1):
            wp.start_step(step_num, step_name)
            time.sleep(0.3)

            # Simulate different types of work in each step
            if step_num == 1:
                # Step 1: Validation - use spinner
                wp.update_step_progress("Checking documents...")
                time.sleep(1)
                wp.update_step_progress("Validating structure...")
                time.sleep(1)
                wp.update_step_progress("Complete")

            elif step_num == 2:
                # Step 2: Spec generation - simulate sections
                sections = ["Overview", "Requirements", "Implementation", "Testing"]
                for i, section in enumerate(sections, 1):
                    wp.update_step_progress(
                        f"Generating {section} ({i}/{len(sections)})"
                    )
                    time.sleep(0.5)

            elif step_num == 3:
                # Step 3: Task extraction
                wp.update_step_progress("Parsing spec.md...")
                time.sleep(0.7)
                wp.update_step_progress("Parsing proposal.md...")
                time.sleep(0.7)
                wp.update_step_progress("Organizing tasks...")
                time.sleep(0.6)

            elif step_num == 4:
                # Step 4: Test generation
                wp.update_step_progress("Analyzing requirements...")
                time.sleep(0.8)
                wp.update_step_progress("Creating test cases...")
                time.sleep(1.2)

            elif step_num == 5:
                # Step 5: Script generation
                wp.update_step_progress("Generating test.py...")
                time.sleep(1)
                wp.update_step_progress("Generating implement.py...")
                time.sleep(1)

            wp.complete_step()
            time.sleep(0.2)

    print()
    print("=" * 70)
    print()


def demo_nested_with_sub_progress():
    """Show nested progress with sub-progress indicators."""

    print("=" * 70)
    print("Nested Progress with Sub-Indicators")
    print("=" * 70)
    print()
    print("Shows overall workflow + step progress + sub-operation progress")
    print()

    with workflow_progress(3, "Build & Deploy") as wp:
        # Step 1: Build with file processing
        wp.start_step(1, "Build")
        wp.update_step_progress("Compiling sources...")
        time.sleep(0.5)

        # Show file-level progress (this would be visible below workflow progress)
        print()  # Give space for file progress
        files = ["main.py", "utils.py", "config.py", "models.py"]
        for i, file in enumerate(files, 1):
            progress_pct = (i / len(files)) * 100
            wp.update_step_progress(f"Compiling {file} ({i}/{len(files)})")
            time.sleep(0.4)

        wp.update_step_progress("Build complete")
        wp.complete_step()
        time.sleep(0.3)

        # Step 2: Test with test suite progress
        wp.start_step(2, "Test")
        wp.update_step_progress("Running test suite...")
        time.sleep(0.5)

        print()  # Give space for test progress
        tests = [
            "test_auth",
            "test_api",
            "test_models",
            "test_utils",
            "test_integration",
        ]
        for i, test in enumerate(tests, 1):
            wp.update_step_progress(f"Running {test} ({i}/{len(tests)})")
            time.sleep(0.5)

        wp.update_step_progress("All tests passed")
        wp.complete_step()
        time.sleep(0.3)

        # Step 3: Deploy with status tracking
        wp.start_step(3, "Deploy")
        wp.update_step_progress("Uploading artifacts...")
        time.sleep(1)
        wp.update_step_progress("Configuring services...")
        time.sleep(1)
        wp.update_step_progress("Deployment complete")
        wp.complete_step()

    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    # Run both demos
    demo_workflow_execution()
    time.sleep(1)
    demo_nested_with_sub_progress()

    print(
        "✓ Demo complete - This shows how nested progress would work in the workflow!"
    )
