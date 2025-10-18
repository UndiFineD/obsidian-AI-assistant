#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

TEMPLATES_DIR = Path("openspec/templates")
CHANGES_DIR = Path("openspec/changes")


_slug_re = re.compile(r"[^a-z0-9-]+")


def slugify(title: str) -> str:
    """Convert a title to a filesystem-friendly slug.

    - Lowercase
    - Replace spaces/underscores with hyphens
    - Remove invalid characters
    - Collapse multiple hyphens
    """
    s = title.strip().lower().replace("_", "-").replace(" ", "-")
    s = _slug_re.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s or "change"


@dataclass
class ChangeSpec:
    title: str
    change_id: str
    owner: Optional[str]
    date: str
    base_dir: Path


def build_change_id(title: str, date: Optional[str] = None, explicit_id: Optional[str] = None) -> str:
    if explicit_id:
        return explicit_id
    date_str = date or dt.date.today().isoformat()
    return f"{date_str}-{slugify(title)}"


def replace_placeholders(text: str, spec: ChangeSpec) -> str:
    text = text.replace("<Change Title>", spec.title)
    text = text.replace("<change-id>", spec.change_id)
    text = text.replace("YYYY-MM-DD", spec.date)
    if spec.owner:
        text = text.replace("@username", spec.owner)
    return text


def create_change(spec: ChangeSpec, *, force: bool = False, dry_run: bool = False) -> Path:
    change_dir = spec.base_dir / CHANGES_DIR / spec.change_id
    if change_dir.exists() and not force:
        raise FileExistsError(f"Change directory already exists: {change_dir}")

    if dry_run:
        return change_dir

    change_dir.mkdir(parents=True, exist_ok=True)

    # Copy todo.md from template with replacements
    todo_tpl = (spec.base_dir / TEMPLATES_DIR / "todo.md").read_text(encoding="utf-8")
    (change_dir / "todo.md").write_text(replace_placeholders(todo_tpl, spec), encoding="utf-8")

    # Minimal other files if not already present
    for name, header in [
        ("proposal.md", "# Proposal\n\nTBD\n"),
        ("spec.md", "# Specification\n\nTBD\n"),
        ("tasks.md", "# Tasks\n\n- [ ] TODO\n"),
        ("test_plan.md", "# Test Plan\n\nTBD\n"),
    ]:
        p = change_dir / name
        if not p.exists():
            p.write_text(header, encoding="utf-8")

    return change_dir


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scaffold a new OpenSpec change")
    parser.add_argument("title", help="Human-readable change title")
    parser.add_argument("--id", dest="change_id", help="Explicit change-id (default: YYYY-MM-DD-<slug>)")
    parser.add_argument("--owner", help="Owner handle (e.g., @kdejo)")
    parser.add_argument("--date", help="Override date (YYYY-MM-DD)")
    parser.add_argument("--base-dir", default=str(Path.cwd()), help="Project root (default: CWD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating files")
    parser.add_argument("--force", action="store_true", help="Overwrite existing change directory")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    ns = parse_args(argv)
    base_dir = Path(ns.base_dir)
    date_str = ns.date or dt.date.today().isoformat()
    change_id = build_change_id(ns.title, date=ns.date, explicit_id=ns.change_id)
    spec = ChangeSpec(title=ns.title, change_id=change_id, owner=ns.owner, date=date_str, base_dir=base_dir)

    try:
        target = create_change(spec, force=ns.force, dry_run=ns.dry_run)
    except FileExistsError as e:
        print(str(e))
        return 1

    print(target)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
