from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def to_change_id(md_path: Path) -> str:
    rel = md_path.relative_to(REPO_ROOT).as_posix().lower()
    # Replace non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", rel.replace(".md", "")).strip("-")
    return f"update-doc-{slug}"


def h1_title(change_id: str) -> str:
    return f"# Change Proposal: {change_id}\n"


def proposal_md(change_id: str, rel_path: str) -> str:
    return (
        f"{h1_title(change_id)}\n"
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
    requirement_title = f"Governance for {Path(rel_path).name}"
    return (
        f"# Spec Delta: project-documentation / {change_id}\n\n"
        "## ADDED Requirements\n\n"
        f"### Requirement: {requirement_title}\n\n"
        f"The project SHALL govern material changes to `{rel_path}` via OpenSpec change proposals to maintain consistency and review.\n\n"
        "#### Scenario: Material change requires proposal\n\n"
        f"- **WHEN** a contributor plans a material update to `{rel_path}`\n"
        "- **THEN** they MUST create or update an OpenSpec change with deltas under `project-documentation`\n"
    )


def main() -> None:
    md_files: list[Path] = []
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

    for path in REPO_ROOT.rglob("*.md"):
        p = path.as_posix()
        # Skip generated change proposals and excluded dirs to avoid noise
        if any(part in p for part in EXCLUDED_PARTS):
            continue
        md_files.append(path)

    generated = []
    skipped = []

    for md in sorted(md_files):
        change_id = to_change_id(md)
        change_dir = REPO_ROOT / "openspec" / "changes" / change_id
        if change_dir.exists():
            skipped.append((md, "exists"))
            continue

        rel_path = md.relative_to(REPO_ROOT).as_posix()
        # Create files
        spec_dir = change_dir / "specs" / "project-documentation"
        spec_dir.mkdir(parents=True, exist_ok=True)

        (change_dir / "proposal.md").write_text(
            proposal_md(change_id, rel_path), encoding="utf-8"
        )
        (change_dir / "tasks.md").write_text(
            tasks_md(change_id, rel_path), encoding="utf-8"
        )
        (spec_dir / "spec.md").write_text(
            spec_delta_md(change_id, rel_path), encoding="utf-8"
        )

        generated.append(rel_path)

    print(f"Generated {len(generated)} OpenSpec changes.")
    if generated:
        print("First 10 generated:")
        for g in generated[:10]:
            print(f"  - {g}")
    print(f"Skipped {len(skipped)} existing changes.")


if __name__ == "__main__":
    main()
