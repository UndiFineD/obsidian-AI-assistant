#!/usr/bin/env python3
"""Remove malformed pass statements that break indentation."""
import sys
import re

def fix_file(filepath):
    """Remove pass statements that appear on their own line before other code."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        fixed_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            stripped = line.strip()
            
            # Check if this is a standalone pass statement
            if stripped == 'pass':
                # Look at next non-empty line
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line:
                        # If next line is also pass, keep one
                        if next_line == 'pass':
                            fixed_lines.append(line)
                        # If next line is meaningful code (not pass), skip this pass
                        elif next_line and not next_line.startswith('#'):
                            # Skip this pass statement
                            pass
                        else:
                            fixed_lines.append(line)
                        break
                else:
                    # No more lines, keep the pass
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f'Fixed: {filepath}')
        return True
        
    except Exception as e:
        print(f'Error fixing {filepath}: {e}')
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python remove_bad_pass.py <file1> <file2> ...')
        sys.exit(1)
    
    for filepath in sys.argv[1:]:
        fix_file(filepath)
