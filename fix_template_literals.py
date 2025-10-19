#!/usr/bin/env python3
"""Fix template literal syntax errors in adminDashboard.js"""
import re

file_path = r'c:\Users\kdejo\DEV\obsidian-llm-assistant\obsidian-AI-assistant\.obsidian\plugins\obsidian-ai-assistant\adminDashboard.js'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all instances where text: or value: is followed by ${...}` without opening backtick
# Pattern: (text|value): ${...}` should become (text|value): `${...}`
lines = content.split('\n')
fixed_lines = []

for line in lines:
    # Match: text: ${...}` or value: ${...}`
    if re.search(r'(text|value):\s+\$\{', line) and '`' in line:
        # Add backtick before ${
        line = re.sub(r'(text|value):\s+(\$\{[^`]*`)', r'\1: `\2', line)
    fixed_lines.append(line)

content = '\n'.join(fixed_lines)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed all template literal syntax errors in adminDashboard.js')
