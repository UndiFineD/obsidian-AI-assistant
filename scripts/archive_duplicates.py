from __future__ import annotations

import re
from pathlib import Path
import shutil
from datetime import datetime


REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGES_DIR = REPO_ROOT / "openspec" / "changes"
ARCHIVE_DIR = CHANGES_DIR / "archive"


EXCLUDED_PARTS = {
    "/openspec/changes/",
    "/.git/",
    "/node_modules/",
    "/.venv/",
    "/venv/",
    "/env/",
    "/.pytest_cache/",
    "/tests/.pytest_cache/",
    "/htmlcov/",
}


def to_change_id_for_path(rel_path: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", rel_path.lower().replace(".md", "")).strip("-")
    return f"update-doc-{slug}"


def find_all_md_files() -> list[Path]:
    md_files: list[Path] = []
    for p in REPO_ROOT.rglob("*.md"):
        posix = p.as_posix()
        if any(x in posix for x in EXCLUDED_PARTS):
            continue
        md_files.append(p)
    return md_files


def canonical_change_dir_for(rel_path: str) -> Path:
    return CHANGES_DIR / to_change_id_for_path(rel_path)


def infer_target_relpath_from_text(text: str, all_rel_paths: set[str], name_map: dict[str, list[str]]) -> str | None:
    # Try exact backticked file path
    for m in re.findall(r"`([^`]+?\.md)`", text, flags=re.IGNORECASE):
        if m in all_rel_paths:
            return m
    # Try by basename mention (e.g., README.md)
    for base, rels in name_map.items():
        pattern = re.compile(rf"\b{re.escape(base)}\b", flags=re.IGNORECASE)
        if pattern.search(text):
            if len(rels) == 1:
                return rels[0]
    return None


def build_name_map(md_rel_paths: list[str]) -> dict[str, list[str]]:
    name_map: dict[str, list[str]] = {}
    for rel in md_rel_paths:
        base = Path(rel).name
        name_map.setdefault(base, []).append(rel)
    return name_map


def main() -> None:
    md_files = find_all_md_files()
    md_rel_paths = sorted([p.relative_to(REPO_ROOT).as_posix() for p in md_files])
    all_rel_paths = set(md_rel_paths)
    name_map = build_name_map(md_rel_paths)

    # Map target -> keep change dir (canonical) and duplicates
    target_to_changes: dict[str, list[Path]] = {rel: [] for rel in md_rel_paths}

    # Index existing change dirs by their inferred target, to find duplicates
    for change_dir in sorted(p for p in CHANGES_DIR.iterdir() if p.is_dir() and p.name != "archive"):
        prop = change_dir / "proposal.md"
        spec = change_dir / "specs" / "project-documentation" / "spec.md"
        target: str | None = None
        for file in (prop, spec):
            if file.exists():
                text = file.read_text(encoding="utf-8", errors="ignore")
                target = infer_target_relpath_from_text(text, all_rel_paths, name_map) or target
        if target and target in target_to_changes:
            target_to_changes[target].append(change_dir)

    # Create archive directory
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    # Create timestamped archive subdirectory
    timestamp = datetime.now().strftime("%Y-%m-%d")
    archive_subdir = ARCHIVE_DIR / f"{timestamp}-duplicate-cleanup"
    archive_subdir.mkdir(exist_ok=True)

    archived = []

    for rel in md_rel_paths:
        canonical_dir = canonical_change_dir_for(rel)
        # Archive duplicates that are not canonical
        duplicates = [d for d in target_to_changes.get(rel, []) if d != canonical_dir]
        for dup in duplicates:
            if dup.exists():
                archive_path = archive_subdir / dup.name
                shutil.move(str(dup), str(archive_path))
                archived.append(f"{dup.name} -> {archive_path.relative_to(CHANGES_DIR)}")

    print(f"Archived {len(archived)} duplicate change folders to {archive_subdir.relative_to(CHANGES_DIR)}.")
    if archived:
        print("Archived changes:")
        for a in archived[:10]:
            print(f"  - {a}")
        if len(archived) > 10:
            print(f"  ... and {len(archived) - 10} more")


if __name__ == "__main__":
    main()