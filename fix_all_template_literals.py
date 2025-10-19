#!/usr/bin/env python3
"""Fix all template literal syntax errors in JavaScript plugin files."""

import re
from pathlib import Path

# Files and their line fixes
fixes = [
    {
        'file': '.obsidian/plugins/obsidian-ai-assistant/enhancedTaskQueueView.js',
        'patterns': [
            (r'(\s+text:)\s+(\$\{)', r'\1 `\2'),  # Fix "text:  ${" -> "text: `${"
        ]
    },
    {
        'file': '.obsidian/plugins/obsidian-ai-assistant/rightPane.js',
        'patterns': [
            (r'(\s+text:)\s+(\$\{)', r'\1 `\2'),  # Fix "text:  ${" -> "text: `${"
        ]
    },
]

def fix_file(filepath, patterns):
    """Apply regex patterns to fix a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"Warning: {filepath} not found")
        return False

    content = path.read_text(encoding='utf-8')
    original_content = content

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        path.write_text(content, encoding='utf-8')
        print(f"Fixed: {filepath}")
        return True
    else:
        print(f"No changes needed: {filepath}")
        return False

def main():
    """Fix all JavaScript template literal errors."""
    print("Fixing JavaScript template literal syntax errors...")

    fixed_count = 0
    for fix_info in fixes:
        if fix_file(fix_info['file'], fix_info['patterns']):
            fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}")

if __name__ == '__main__':
    main()
