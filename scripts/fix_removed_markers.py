#!/usr/bin/env python3
"""Fix corrupted ***REMOVED*** markers in Python files."""

import re
import sys
from pathlib import Path

# Files that contain the corrupted marker
FILES_TO_FIX = [
    "backend/backend.py",
    "backend/enterprise_integration.py",
    "scripts/auto_fix_issues.py",
    "tests/backend/test_backend.py",
    "tests/backend/test_enterprise_auth.py",
    "tests/backend/test_indexing.py",
    "tests/backend/test_indexing_comprehensive.py",
    "tests/backend/test_modelmanager.py",
    "tests/backend/test_modelmanager_comprehensive.py"
]

# Mapping of variable names to replacement values
REPLACEMENTS = {
    'client_secret': 'test-client-secret',
    'secret_key': 'test-secret-key',
    'hf_token': 'test-hf-token',
    'correct_secret': 'correct-secret',
    'wrong_secret': 'wrong-secret',
    'malformed_token': 'malformed-token'
}

def fix_file(filepath):
    """Fix corrupted markers in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Replace patterns like: client_secret="***REMOVED***"
        # or: secret_ = "***REMOVED***"
        for var_name, replacement in REPLACEMENTS.items():
            # Match full variable names
            pattern = rf'({var_name})\s*=\s*"[^"]*REMOVED[^"]*"'
            content = re.sub(pattern, rf'\1="{replacement}"', content)
            
            # Match truncated variable names (client_, secret_, etc.)
            truncated = var_name.rsplit('_', 1)[0] + '_'
            pattern = rf'({truncated})\s*=\s*"[^"]*REMOVED[^"]*"'
            content = re.sub(pattern, rf'\1secret="{replacement}"', content)
        
        # Generic replacement for any remaining instances
        content = re.sub(r'"[^"]*\*\*\*REMOVED\*\*\*[^"]*"', '"***PLACEHOLDER***"', content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"â Fixed: {filepath}")
            return True
        else:
            print(f"  No changes: {filepath}")
            return False
    except Exception as e:
        print(f"â Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all files with corrupted markers."""
    root = Path(__file__).parent.parent
    fixed_count = 0
    
    print("Fixing corrupted ***REMOVED*** markers...\n")
    
    for file_path in FILES_TO_FIX:
        full_path = root / file_path
        if full_path.exists():
            if fix_file(full_path):
                fixed_count += 1
        else:
            print(f"  File not found: {file_path}")
    
    print(f"\n{fixed_count} file(s) fixed.")
    return 0 if fixed_count > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
