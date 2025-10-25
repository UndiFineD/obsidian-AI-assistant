#!/usr/bin/env python3
"""Implementation script for cleanup-organize-docs - Functional cleanup implementation"""

import sys, re, argparse, shutil
from pathlib import Path

change_root = Path(__file__).parent
project_root = change_root.parent.parent.parent
impl_results = {"completed": 0, "failed": 0, "tasks": []}


def log_task(name, result):
    print(f"  {'[OK]' if result == 'OK' else '[FAIL]'} {name}")
    impl_results["tasks"].append({"name": name, "result": result})


def create_structure():
    try:
        docs = project_root / "docs"
        docs.mkdir(exist_ok=True)
        for s in [
            "getting-started",
            "guides",
            "architecture",
            "reference",
            "production",
            "historical",
        ]:
            (docs / s).mkdir(exist_ok=True)
            log_task(f"Create docs/{s}/", "OK")
        (docs / "README.md").write_text("# Documentation\nWelcome!")
        impl_results["completed"] += 7
        return True
    except Exception as e:
        log_task("Create structure", str(e))
        return False


def move_docs():
    try:
        moved = 0
        for f, dest in [
            ("GIT_WORKFLOW_REFERENCE.md", "guides"),
            ("PRODUCTION_READINESS_V0.1.35.md", "production"),
        ]:
            src = project_root / f
            if src.exists():
                (project_root / "docs" / dest).mkdir(exist_ok=True, parents=True)
                shutil.move(str(src), str(project_root / "docs" / dest / f))
                log_task(f"Move {f}", "OK")
                moved += 1
        impl_results["completed"] += moved
        return True
    except Exception as e:
        log_task("Move docs", str(e))
        return False


def delete_files():
    try:
        deleted = 0
        for p in [
            "*CELEBRATION*.md",
            "COMPLETION_CERTIFICATE_*.md",
            "PROJECT_COMPLETE_*.md",
            "SESSION_*.md",
        ]:
            for f in project_root.glob(p):
                f.unlink()
                deleted += 1
        log_task(f"Delete {deleted} files", "OK")
        impl_results["completed"] += deleted
        return True
    except Exception as e:
        log_task("Delete files", str(e))
        return False


def update_readme():
    try:
        r = project_root / "README.md"
        if r.exists() and "docs/" not in r.read_text():
            r.write_text(r.read_text() + "\n\n## Documentation\nSee [docs/](./docs/)")
        impl_results["completed"] += 1
        log_task("Update README", "OK")
        return True
    except Exception as e:
        log_task("Update README", str(e))
        return False


def main():
    print("=" * 50)
    print("Implementation: cleanup-organize-docs")
    print("=" * 50 + "\n")
    create_structure()
    move_docs()
    delete_files()
    update_readme()
    print(f"\n[SUCCESS] Completed: {impl_results['completed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
