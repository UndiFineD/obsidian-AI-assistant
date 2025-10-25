import argparse
import os

# Supported indent styles: 4 spaces (default), tabs (optional)
DEFAULT_INDENT = 4


def detect_indent_style(lines):
    """Detects the most common indentation style in the file."""
    space_count = 0
    tab_count = 0
    for line in lines:
        if line.startswith("\t"):
            tab_count += 1
        elif line.startswith(" "):
            space_count += 1
    if tab_count > space_count:
        return "tab"
    return "space"


def normalize_indentation(lines, indent_size=4):
    """
    Normalize indentation by converting mixed tabs/spaces to consistent spaces.
    This preserves the existing indent levels but standardizes the format.
    Also fixes misplaced 'pass' statements that appear on the same line as block keywords.
    """
    normalized = []
    i = 0
    while i < len(lines):
        line = lines[i]

        if not line.strip():
            normalized.append("\n")
            i += 1
            continue

        # Check for misplaced pass statements like "try:\n        pass\n            code"
        stripped = line.lstrip()

        # Fix pattern where pass is on wrong indent after block keyword
        if stripped == "pass" and i > 0:
            prev_line = lines[i - 1].lstrip()
            # If previous line ends with ':', this pass might be wrongly indented
            if prev_line.rstrip().endswith(":"):
                # Check if next line exists and is more indented (actual block content)
                if i + 1 < len(lines) and lines[i + 1].strip():
                    next_stripped = lines[i + 1].lstrip()
                    next_indent = len(lines[i + 1]) - len(next_stripped)
                    curr_indent = len(line) - len(stripped)

                    # If current pass has same or less indent than next line, skip it
                    # (it's likely a misplaced pass before the real block)
                    if curr_indent <= next_indent:
                        i += 1
                        continue

        # Count leading whitespace (treating tab as 4 spaces)
        leading = line[: len(line) - len(stripped)]

        # Convert tabs to spaces for measurement
        expanded = leading.expandtabs(indent_size)
        indent_level = len(expanded) // indent_size

        # Reconstruct line with normalized indentation
        new_line = (" " * (indent_level * indent_size)) + stripped
        normalized.append(new_line.rstrip() + "\n")
        i += 1

    return normalized


def process_file(
    filepath, indent=DEFAULT_INDENT, style=None, dry_run=False, backup=True
):
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    if style is None:
        style = detect_indent_style(lines)

    # Use normalization instead of reconstruction
    fixed = normalize_indentation(lines, indent)

    if dry_run:
        # Show diff
        diff_count = 0
        for i, (orig, fixed_line) in enumerate(zip(lines, fixed)):
            if orig != fixed_line:
                print(f"Line {i + 1}:\n- {orig.rstrip()}\n+ {fixed_line.rstrip()}\n")
                diff_count += 1
        if diff_count == 0:
            print("No indentation changes needed.")
        else:
            print(f"\nTotal lines to change: {diff_count}")
        return

    if backup:
        bak_path = filepath + ".bak"
        if not os.path.exists(bak_path):
            try:
                with open(bak_path, "w", encoding="utf-8") as bak:
                    bak.writelines(lines)
            except Exception as e:
                print(f"Warning: could not create backup: {e}")

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(fixed)
        print(f"[OK] Indentation fixed for {filepath}")
    except Exception as e:
        print(f"[ERROR] Error writing file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Fix indentation issues in a Python file."
    )
    parser.add_argument("--file", required=True, help="Path to the file to fix.")
    parser.add_argument(
        "--indent",
        type=int,
        default=DEFAULT_INDENT,
        help="Indent size (spaces, default 4)",
    )
    parser.add_argument(
        "--style", choices=["space", "tab"], help="Indent style (space or tab)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without applying."
    )
    parser.add_argument(
        "--no-backup", action="store_true", help="Do not create .bak backup."
    )
    args = parser.parse_args()
    process_file(
        args.file,
        indent=args.indent,
        style=args.style,
        dry_run=args.dry_run,
        backup=not args.no_backup,
    )


if __name__ == "__main__":
    main()
