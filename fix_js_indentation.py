#!/usr/bin/env python3
"""
JavaScript Code Formatter for PEP8-style Conventions
Converts JavaScript files to use 4-space indentation consistently
"""

import os
import re
from pathlib import Path


def fix_indentation(content):
    """
    Convert JavaScript file content to use 4-space indentation
    """
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            fixed_lines.append('')
            continue
            
        # Count leading spaces/tabs
        leading_whitespace = len(line) - len(line.lstrip())
        content_part = line.lstrip()
        
        # Convert tabs to spaces first
        line_no_tabs = line.replace('\t', '    ')
        
        # Count indentation level (assuming original was 2-space or mixed)
        # Look for patterns of 2 spaces and convert to 4
        indent_match = re.match(r'^(\s*)', line_no_tabs)
        if indent_match:
            current_indent = indent_match.group(1)
            # Convert 2-space indents to 4-space
            if '  ' in current_indent and '    ' not in current_indent:
                # This is likely 2-space indentation
                indent_level = len(current_indent) // 2
                new_indent = '    ' * indent_level
                fixed_line = new_indent + content_part
            else:
                # Keep existing 4-space or handle mixed indentation
                fixed_line = line_no_tabs
        else:
            fixed_line = line_no_tabs
            
        fixed_lines.append(fixed_line)
    
    return '\n'.join(fixed_lines)


def improve_js_style(content):
    """
    Apply PEP8-like style improvements to JavaScript
    """
    # Fix spacing around operators
    content = re.sub(r'(\w)\s*=\s*(\w)', r'\1 = \2', content)
    
    # Fix spacing after commas
    content = re.sub(r',(\w)', r', \1', content)
    
    # Fix spacing around parentheses in function calls
    content = re.sub(r'(\w)\s*\(\s*', r'\1(', content)
    content = re.sub(r'\s*\)\s*{', r') {', content)
    
    # Ensure consistent spacing in object literals
    content = re.sub(r'{\s*(\w)', r'{ \1', content)
    content = re.sub(r'(\w)\s*}', r'\1 }', content)
    
    # Fix spacing around colons in object literals
    content = re.sub(r'(\w)\s*:\s*(\w)', r'\1: \2', content)
    
    return content


def format_javascript_file(file_path):
    """
    Format a single JavaScript file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Apply indentation fixes
        fixed_content = fix_indentation(content)
        
        # Apply style improvements
        improved_content = improve_js_style(fixed_content)
        
        # Write back the formatted content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(improved_content)
            
        print(f"✅ Formatted: {file_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error formatting {file_path}: {e}")
        return False


def main():
    """
    Format all JavaScript files in the plugin directory
    """
    plugin_dir = Path("plugin")
    if not plugin_dir.exists():
        print("❌ Plugin directory not found!")
        return
    
    js_files = list(plugin_dir.glob("*.js"))
    if not js_files:
        print("❌ No JavaScript files found in plugin directory!")
        return
    
    print(f"🔧 Formatting {len(js_files)} JavaScript files...")
    print("Converting to PEP8-style 4-space indentation")
    
    success_count = 0
    for js_file in js_files:
        if format_javascript_file(js_file):
            success_count += 1
    
    print(f"\n✅ Successfully formatted {success_count}/{len(js_files)} files")
    
    if success_count == len(js_files):
        print("🎉 All JavaScript files now use consistent 4-space indentation!")
    else:
        print("⚠️  Some files had formatting issues - please check manually")


if __name__ == "__main__":
    main()