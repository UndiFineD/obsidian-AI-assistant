#!/usr/bin/env python3
"""
Generate clean text-based diffs comparing workflow-0.1.38 (archive) 
with current workflow files.
"""

import difflib
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
ARCHIVE_DIR = SCRIPTS_DIR / "workflow-0.1.38"

def generate_diff(archive_file, current_file, output_file):
    """Generate a clean unified diff between archive and current files."""
    try:
        with open(archive_file, 'r', encoding='utf-8', errors='replace') as f:
            archive_lines = f.readlines()
        with open(current_file, 'r', encoding='utf-8', errors='replace') as f:
            current_lines = f.readlines()
        
        if archive_lines == current_lines:
            return "IDENTICAL", 0
        
        # Generate unified diff
        diff = list(difflib.unified_diff(
            archive_lines,
            current_lines,
            fromfile=f"v0.1.38 (Archive): {archive_file.name}",
            tofile=f"Current: {current_file.name}",
            lineterm='',
            n=3
        ))
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in diff:
                f.write(line + '\n')
        
        return "DIFFERENT", len(diff)
    
    except Exception as e:
        return f"ERROR: {str(e)}", 0

def main():
    """Compare all workflow-0.1.38 archive files with current versions."""
    
    print("=" * 80)
    print("REGENERATING DIFFS: workflow-0.1.38 (Archive) vs Current Scripts")
    print("=" * 80 + "\n")
    
    # Get all files to compare
    comparisons = [
        ("workflow.py", "workflow.py"),
        ("workflow.ps1", "workflow.ps1"),
        ("workflow-helpers.py", "workflow-helpers.py"),
        ("version_manager.py", "version_manager.py"),
        ("workflow_nested_progress_demo.py", "workflow_nested_progress_demo.py"),
        ("workflow_visualizer.py", "workflow_visualizer.py"),
        ("workflow2.ps1", "workflow2.ps1"),
    ]
    
    # Add workflow steps
    for i in range(13):
        step_name = f"workflow-step{i:02d}.py"
        comparisons.append((step_name, step_name))
    
    total_diffs = 0
    total_diff_lines = 0
    identical_count = 0
    
    print(f"{'Status':<12} {'Archive File':<30} {'Current File':<30} {'Diff Lines':<12}")
    print("-" * 84)
    
    for archive_name, current_name in comparisons:
        archive_file = ARCHIVE_DIR / archive_name
        current_file = SCRIPTS_DIR / current_name
        
        # Skip if files don't exist
        if not archive_file.exists():
            print(f"{'⚠️  MISSING':<12} {archive_name:<30} {current_name:<30} {'N/A':<12}")
            continue
        
        if not current_file.exists():
            print(f"{'❌ NO CURR':<12} {archive_name:<30} {current_name:<30} {'N/A':<12}")
            continue
        
        output_name = f"ARCHIVE_VS_CURRENT_{archive_name}.diff"
        output_file = ARCHIVE_DIR / output_name
        
        result, diff_count = generate_diff(archive_file, current_file, output_file)
        
        if "IDENTICAL" in result:
            status = "✅ SAME"
            identical_count += 1
        elif "DIFFERENT" in result:
            status = "❌ DIFF"
            total_diffs += 1
            total_diff_lines += diff_count
        else:
            status = "⚠️  ERROR"
        
        print(f"{status:<12} {archive_name:<30} {current_name:<30} {diff_count:<12}")
    
    print("-" * 84)
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total files compared: {len(comparisons)}")
    print(f"Identical files: {identical_count}")
    print(f"Different files: {total_diffs}")
    print(f"Total diff lines: {total_diff_lines}")
    
    if total_diffs > 0:
        print(f"\n📍 Diff files saved to: {ARCHIVE_DIR}/ARCHIVE_VS_CURRENT_*.diff")
        print("   Use: cat ARCHIVE_VS_CURRENT_*.diff (to view)")
    
    print("\n✅ Diff generation complete!")
    print("=" * 80)

if __name__ == "__main__":
    main()
