#!/usr/bin/env python3
"""
Script to fix remaining Markdown linting issues automatically.
"""

import os
import re
import glob
from pathlib import Path

def fix_line_length_issues(content, max_length=120):
    """Fix overly long lines by breaking them sensibly."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        if len(line) <= max_length:
            fixed_lines.append(line)
            continue
            
        # Don't break URLs, code blocks, or tables
        if (line.strip().startswith('http') or 
            line.strip().startswith('|') or
            line.strip().startswith('```') or
            '```' in line):
            fixed_lines.append(line)
            continue
            
        # Try to break at logical points
        if len(line) > max_length:
            # Find good break points (after punctuation, before conjunctions)
            break_points = []
            for i, char in enumerate(line):
                if i < max_length and char in '.,;: ' and i > 50:
                    break_points.append(i)
            
            if break_points:
                break_point = max(break_points)
                first_part = line[:break_point].rstrip()
                second_part = line[break_point:].lstrip()
                fixed_lines.append(first_part)
                if second_part:
                    fixed_lines.append(second_part)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_ordered_list_numbering(content):
    """Fix ordered list numbering to be consistent."""
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line starts an ordered list
        if re.match(r'^\d+\.\s', line):
            # Start of ordered list - collect all consecutive list items
            list_items = []
            indent_level = len(line) - len(line.lstrip())
            
            while i < len(lines) and re.match(r'^\s*\d+\.\s', lines[i]):
                current_line = lines[i]
                current_indent = len(current_line) - len(current_line.lstrip())
                
                if current_indent == indent_level:
                    # Same level - renumber
                    item_content = re.sub(r'^\s*\d+\.', f'{len(list_items) + 1}.', current_line)
                    list_items.append(item_content)
                else:
                    # Different indent level - keep as is for now
                    list_items.append(current_line)
                i += 1
            
            fixed_lines.extend(list_items)
        else:
            fixed_lines.append(line)
            i += 1
    
    return '\n'.join(fixed_lines)

def fix_trailing_newlines(content):
    """Ensure files end with exactly one newline."""
    return content.rstrip() + '\n'

def fix_markdown_file(file_path):
    """Fix all markdown issues in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_line_length_issues(content)
        content = fix_ordered_list_numbering(content)
        content = fix_trailing_newlines(content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return True
        else:
            print(f"No changes: {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix all markdown files."""
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("docs/ directory not found")
        return
    
    markdown_files = list(docs_dir.glob("*.md"))
    print(f"Found {len(markdown_files)} markdown files")
    
    fixed_count = 0
    for file_path in markdown_files:
        if fix_markdown_file(file_path):
            fixed_count += 1
    
    print(f"\nFixed {fixed_count} files out of {len(markdown_files)} total")

if __name__ == "__main__":
    main()