#!/usr/bin/env python3
"""Restore files from .bak backups and validate them."""

import shutil
import sys
from pathlib import Path


def restore_from_backup(dry_run=True):
    """Restore all .py files from their .bak backups."""
    root = Path(__file__).parent.parent
    bak_files = list(root.glob("**/*.py.bak"))

    if not bak_files:
        print("No .bak files found.")
        return 0

    print(f"Found {len(bak_files)} backup files.\n")

    restored_count = 0
    for bak_file in bak_files:
        original_file = bak_file.with_suffix("")  # Remove .bak extension

        if original_file.exists():
            if dry_run:
                print(f"Would restore: {original_file.relative_to(root)}")
            else:
                try:
                    shutil.copy2(bak_file, original_file)
                    print(f"[OK] Restored: {original_file.relative_to(root)}")
                    restored_count += 1
                except Exception as e:
                    print(f"[ERR] Failed to restore {original_file}: {e}")
        else:
            print(f"  Skip (no original): {original_file.relative_to(root)}")

    if dry_run:
        print(f"\n{len(bak_files)} file(s) would be restored.")
        print("Run with --apply to actually restore files.")
    else:
        print(f"\n{restored_count} file(s) restored.")

    return 0


def main():
    """Main entry point."""
    dry_run = "--apply" not in sys.argv
    return restore_from_backup(dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
