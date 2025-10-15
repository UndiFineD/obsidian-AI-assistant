from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

#!/usr/bin/env python
"""Automated repository hygiene fixer (conservative mode).

Safe operations only:
- Remove trailing whitespace on each line
- Remove whitespace-only lines (preserve real blank lines)
- Normalize to a single trailing newline at EOF
- Remove non-printable control characters (except tab/newline/CR)
- Markdown formatting (headings/lists spacing, collapse multiple blank lines)

Intentionally NOT doing:
- Import reordering/moving or deletion
- Indentation changes (tabs/spaces) or block structure edits
- Bare-except or code semantics modifications

Usage:
python scripts/auto_fix_issues.py             # dry-run: show prospective changes
python scripts/auto_fix_issues.py --apply     # apply changes in-place (backs up to .bak)

The script is conservative: it won't modify files larger than 1 MB and skips virtualenv,
cache, build, model, and coverage directories.
"""

ROOT = Path(__file__).resolve().parents[1]
PYTHON_PAT = re.compile(r"^.+\.py$")
MARKDOWN_PAT = re.compile(r"^.+\.(?:md|MD)$")
MAX_SIZE = 1_000_000  # 1 MB safety limit
SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "backend/models",
    "backend/cache",
    "htmlcov",
}


MD_HEADING_RE = re.compile(r"^(#{1,6})\s+\S")
MD_LIST_RE = re.compile(r"^\s*([*-]|\d+\.)\s+")


@dataclass
class FileChange:
    path: Path
    original: str
    updated: str

    def diff_preview(self, lines: int = 6) -> str:
        o_lines = self.original.splitlines()
        u_lines = self.updated.splitlines()
        # Simple context diff (manual, to avoid difflib noise for large files)
        preview = []
        for i, (o, u) in enumerate(zip(o_lines, u_lines)):
            if o != u:
                preview.append(f"@@ line {i+1} @@")
                preview.append(f"- {o}")
                preview.append(f"+ {u}")
                if len(preview) > lines:
                    break
        if len(o_lines) != len(u_lines):
            preview.append(f"@@ length changed: {len(o_lines)} -> {len(u_lines)} @@")
        return "\n".join(preview)


def iter_files(pattern: re.Pattern) -> Iterable[Path]:
    for p in ROOT.rglob("*"):
        if not pattern.match(p.name):
            continue
        if any(skip in p.parts for skip in SKIP_DIRS):
            continue
        if p.is_file() and p.stat().st_size <= MAX_SIZE:
            yield p


# --- Python fixers ---
def fix_python(content: str) -> str:
    original = content
    # 1) Trim trailing whitespace on each line
    lines = [re.sub(r"[ \t]+$", "", line) for line in content.splitlines()]
    new_content = "\n".join(lines)
    # 2) Remove whitespace-only lines (leave true blank lines intact)
    new_content = re.sub(r"^[ \t]+$", "", new_content, flags=re.MULTILINE)
    # 3) Normalize EOF newline (single trailing newline)
    new_content = new_content.rstrip() + "\n"
    # 4) Remove non-printable control characters except tab/newline/CR
    new_content = "".join(c for c in new_content if c >= " " or c in "\t\n\r")
    return new_content if new_content != original else original


# --- Markdown fixers ---


def fix_markdown(content: str) -> str:
    original = content
    lines = content.splitlines()

    # 1. Collapse multiple blank lines to single (MD012)
    collapsed: List[str] = []
    blank_run = 0
    for line in lines:
        # Remove trailing whitespace (MD009)
        line = line.rstrip()
        # Remove tabs for indentation (MD010)
        if "\t" in line:
            line = line.replace("\t", "    ")
        if line.strip() == "":
            blank_run += 1
            if blank_run > 1:
                continue
        else:
            blank_run = 0
        collapsed.append(line)

    lines = collapsed

    # 2. Ensure blank line before and after headings (MD022)
    i = 0
    out: List[str] = []
    while i < len(lines):
        line = lines[i]
        if MD_HEADING_RE.match(line):
            # ensure previous line blank (unless start)
            if out and out[-1].strip() != "":
                out.append("")
            out.append(line)
            # ensure next line blank (unless already or end)
            if i + 1 < len(lines) and lines[i + 1].strip() != "":
                out.append("")
        else:
            out.append(line)
        i += 1

    # 3. Ensure blank lines around lists (MD032)
    final: List[str] = []
    for idx, line in enumerate(out):
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            if final and final[-1].strip() != "":
                final.append("")
            final.append(line)
        else:
            final.append(line)

    # 4. Remove trailing spaces from headings (MD018)
    final = [re.sub(r"(#+\s+\S.*?)\s+$", r"\1", l) for l in final]

    # 5. Remove spaces before list markers (MD030)
    final = [re.sub(r"^ +([-*]|\d+\.)", r"\1", l) for l in final]

    # 6. Remove consecutive heading levels (MD025)
    prev_heading = 0
    for idx, line in enumerate(final):
        m = MD_HEADING_RE.match(line)
        if m:
            level = len(m.group(1))
            if prev_heading and abs(level - prev_heading) > 1:
                # Demote heading to previous level + 1
                final[idx] = "#" * (prev_heading + 1) + line[level:]
            prev_heading = level
        elif line.strip():
            prev_heading = 0

    # 7. Normalize EOF newline (MD047)
    new_content = "\n".join(final).rstrip() + "\n"

    return new_content if new_content != original else original


def process_files(apply: bool, target_file: str = None) -> List[FileChange]:
    changes: List[FileChange] = []

    # If target_file is specified, only process that file
    if target_file:
        target_path = Path(target_file).resolve()
        if not target_path.exists():
            print(f"Error: File not found: {target_file}")
            return changes

        try:
            text = target_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error reading {target_file}: {e}")
            return changes

        # Determine file type and apply appropriate fixes
        if PYTHON_PAT.match(target_path.name):
            updated = fix_python(text)
        elif MARKDOWN_PAT.match(target_path.name):
            updated = fix_markdown(text)
        else:
            print(f"Warning: {target_file} is neither Python nor Markdown, skipping.")
            return changes

        if updated != text:
            changes.append(FileChange(target_path, text, updated))

        if apply and changes:
            backup_path = target_path.with_suffix(target_path.suffix + ".bak")
            try:
                backup_path.write_text(text, encoding="utf-8")
                print(f"Backup saved to: {backup_path}")
            except Exception as e:
                print(f"Warning: could not create backup for {target_path}: {e}")
            target_path.write_text(updated, encoding="utf-8")

        return changes

    # Otherwise, process all files
    for path in iter_files(PYTHON_PAT):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        updated = fix_python(text)
        if updated != text:
            changes.append(FileChange(path, text, updated))

    for path in iter_files(MARKDOWN_PAT):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        updated = fix_markdown(text)
        if updated != text:
            changes.append(FileChange(path, text, updated))

    if apply:
        for ch in changes:
            # Make .bak backup before applying changes
            backup_path = ch.path.with_suffix(ch.path.suffix + ".bak")
            try:
                backup_path.write_text(ch.original, encoding="utf-8")
            except Exception as e:
                print(f"Warning: could not create backup for {ch.path}: {e}")
            ch.path.write_text(ch.updated, encoding="utf-8")
    return changes


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Auto-fix common lint issues")
    parser.add_argument(
        "--apply", action="store_true", help="Apply changes instead of dry-run"
    )
    parser.add_argument("--file", type=str, help="Apply fixes to a specific file only")
    args = parser.parse_args(argv)

    changes = process_files(apply=args.apply, target_file=args.file)
    if not changes:
        print("No changes needed.")
        return 0

    # Show summary with diffs in dry-run mode
    if args.apply:
        # Apply mode: just show files changed
        for ch in changes[:20]:
            print(f"Applied changes to: {ch.path}")
        if len(changes) > 20:
            print(f"...and {len(changes) - 20} more files.")
        print(
            f"\n✓ Successfully applied changes to {len(changes)} files (backups saved as .bak)"
        )
    else:
        # Dry-run mode: show diffs
        for idx, ch in enumerate(changes[:5], 1):
            print(f"\n{'='*70}")
            print(f"[{idx}] {ch.path}")
            print("=" * 70)
            print(ch.diff_preview(lines=10))
        if len(changes) > 5:
            print(f"\n...and {len(changes) - 5} more files would be changed.")
        print(f"\nTotal files to change: {len(changes)}")
        print("Run with --apply to apply these changes.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
