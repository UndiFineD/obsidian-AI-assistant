"""
Automated CHANGELOG.md generator for OpenSpec change proposals.

- Scans openspec/changes/ for proposal.md files
- Extracts proposal title, date, type (update-doc, update-spec, etc)
- Groups by version (if available) or by month
- Outputs CHANGELOG.md in root directory

Usage:
    python scripts/generate_changelog.py [--output CHANGELOG.md]
"""

import argparse
import glob
import os
import re

CHANGE_PROPOSALS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "openspec", "changes"
)
DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "..", "CHANGELOG.md")

PROPOSAL_PATTERN = re.compile(r"^# (.+)$", re.MULTILINE)
DATE_PATTERN = re.compile(r"Date:\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
TYPE_PATTERN = re.compile(
    r"update-(doc|spec|test|ci|security|release)-[\w-]+", re.IGNORECASE
)


def extract_proposal_info(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    title_match = PROPOSAL_PATTERN.search(content)
    date_match = DATE_PATTERN.search(content)
    type_match = TYPE_PATTERN.search(content)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath)
    date = date_match.group(1) if date_match else None
    change_type = type_match.group(0) if type_match else "update-doc-unknown"
    return {
        "title": title,
        "date": date,
        "type": change_type,
        "file": os.path.basename(filepath),
    }


def group_by_month(proposals):
    grouped = {}
    for p in proposals:
        month = p["date"][:7] if p["date"] else "Unknown"
        grouped.setdefault(month, []).append(p)
    return grouped


def generate_changelog(proposals):
    grouped = group_by_month(proposals)
    lines = ["# 📝 CHANGELOG", "", "Generated from OpenSpec change proposals.", ""]
    for month in sorted(grouped.keys(), reverse=True):
        lines.append(f"## {month}")
        for p in grouped[month]:
            lines.append(f"- **{p['title']}** ({p['type']}, {p['date']})")
            lines.append(f"  _File: {p['file']}_")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate CHANGELOG.md from OpenSpec proposals."
    )
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUTPUT, help="Output file path"
    )
    args = parser.parse_args()
    proposal_files = glob.glob(
        os.path.join(CHANGE_PROPOSALS_DIR, "**", "proposal.md"), recursive=True
    )
    proposals = [extract_proposal_info(f) for f in proposal_files]
    changelog = generate_changelog(proposals)
    with open(args.output, "w", encoding="utf-8") as out:
        out.write(changelog)
    print(f"CHANGELOG generated: {args.output} ({len(proposals)} proposals)")


if __name__ == "__main__":
    main()
