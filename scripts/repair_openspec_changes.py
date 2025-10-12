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


def proposal_md(change_id: str, rel_path: str) -> str:
    return (
        f"# Change Proposal: {change_id}\n\n"
        "## Why\n\n"
        f"Ensure `{rel_path}` is governed by OpenSpec so material updates are reviewed and stay consistent with project standards.\n\n"
        "## What Changes\n\n"
        f"- Add a documentation governance requirement for `{rel_path}` under the `project-documentation` capability.\n"
        "- Track material updates via OpenSpec proposals (no functional code changes).\n\n"
        "## Impact\n\n"
        "- Affected specs: project-documentation\n"
        "- Affected code: none (documentation only)\n"
    )


def tasks_md(change_id: str, rel_path: str) -> str:
    return (
        f"# Tasks: {change_id}\n\n"
        "## 1. Implementation\n\n"
        f"- [ ] 1.1 Review `{rel_path}` and classify changes as material or minor\n"
        "- [ ] 1.2 For material changes, update this proposal and add/modify deltas as needed\n"
        f"- [ ] 1.3 Validate: `openspec validate {change_id} --strict`\n"
        "- [ ] 1.4 Open PR referencing this change and request review\n"
    )


def spec_delta_md(change_id: str, rel_path: str) -> str:
    req_title = f"Governance for {Path(rel_path).name}"
    return (
        f"# Spec Delta: project-documentation / {change_id}\n\n"
        "## ADDED Requirements\n\n"
        f"### Requirement: {req_title}\n\n"
        f"The project SHALL govern material changes to `{rel_path}` via OpenSpec change proposals to maintain consistency and review.\n\n"
        "#### Scenario: Material change requires proposal\n\n"
        f"- **WHEN** a contributor plans a material update to `{rel_path}`\n"
        "- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`\n"
    )


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

    # Create archive directory structure
    ARCHIVE_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    archive_subdir = ARCHIVE_DIR / f"{timestamp}-duplicate-cleanup"
    archive_subdir.mkdir(exist_ok=True)

    archived = []
    regenerated = []

    for rel in md_rel_paths:
        canonical_dir = canonical_change_dir_for(rel)
        # Archive duplicates that are not canonical
        duplicates = [d for d in target_to_changes.get(rel, []) if d != canonical_dir]
        for dup in duplicates:
            if dup.exists():
                archive_path = archive_subdir / dup.name
                shutil.move(str(dup), str(archive_path))
                archived.append(f"{dup.name} -> {archive_path.relative_to(CHANGES_DIR)}")

        # Ensure canonical regenerated
        spec_dir = canonical_dir / "specs" / "project-documentation"
        spec_dir.mkdir(parents=True, exist_ok=True)
        change_id = canonical_dir.name
        (canonical_dir / "proposal.md").write_text(proposal_md(change_id, rel), encoding="utf-8")
        (canonical_dir / "tasks.md").write_text(tasks_md(change_id, rel), encoding="utf-8")
        (spec_dir / "spec.md").write_text(spec_delta_md(change_id, rel), encoding="utf-8")
        regenerated.append(canonical_dir.relative_to(REPO_ROOT).as_posix())

    print(f"Regenerated {len(regenerated)} canonical changes.")
    print(f"Archived {len(archived)} duplicate change folders to {archive_subdir.relative_to(CHANGES_DIR)}.")
    if archived:
        print("Archived changes:")
        for a in archived[:10]:
            print(f"  - {a}")
        if len(archived) > 10:
            print(f"  ... and {len(archived) - 10} more")


if __name__ == "__main__":
    main()
