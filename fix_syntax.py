#!/usr/bin/env python3
"""
Fix common syntax errors in test files.
"""

import re
import os

def fix_syntax_file(filepath):
    """Fix common syntax errors in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix common patterns
    # 1. response.json( -> response.json()
    content = re.sub(r'response\.json\(\s*$', 'response.json()', content, flags=re.MULTILINE)
    
    # 2. assert ... ))  -> assert ... )
    content = re.sub(r'(assert [^)]+)\)\)', r'\1)', content)
    
    # 3. assert len(data > 0) -> assert len(data) > 0
    content = re.sub(r'assert len\(([^>]+) > ([^)]+)\)', r'assert len(\1) > \2', content)
    
    # 4. Missing closing parentheses in pytest.main calls
    content = re.sub(r'pytest\.main\(\[__file__\]\s*$', 'pytest.main([__file__])', content, flags=re.MULTILINE)
    
    # 5. Fix generator expressions without proper parentheses
    content = re.sub(r'all\(isinstance\(([^,]+), ([^)]+) for ([^)]+)\)', r'all(isinstance(\1, \2) for \3)', content)
    
    # 6. Fix unmatched parentheses in assert statements
    content = re.sub(r'(assert [^)]+[^)])\)$', r'\1', content, flags=re.MULTILINE)
    
    # 7. Fix missing closing parentheses in with open statements
    content = re.sub(r"with open\(([^,]+), 'r', encoding='utf-8' as f\):", r"with open(\1, 'r', encoding='utf-8') as f:", content)
    
    # 8. Fix unterminated string literals
    content = re.sub(r'print\(f"([^"]+)$', r'print(f"\1")', content, flags=re.MULTILINE)
    
    # 9. Fix .exists( -> .exists()
    content = re.sub(r'\.exists\(,', '.exists() and', content)
    
    # 10. Fix memory_info issue
    content = re.sub(r'memory_info\(\.rss', 'memory_info().rss', content)
    
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed syntax in: {filepath}")
        return True
    return False

def main():
    """Fix syntax in all test files."""
    test_dirs = ['tests/backend', 'tests/integration', 'tests/plugin', 'tests']
    
    for test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue
            
    for root, _, files in os.walk(test_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    fix_syntax_file(filepath)

if __name__ == "__main__":
    main()