#!/usr/bin/env python3
"""
Advanced JavaScript Quality Fixer
Fixes indentation, trailing whitespace, quotes, and other issues
"""

import re
from pathlib import Path


def fix_trailing_whitespace(content):
    """Remove trailing whitespace from all lines"""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        # Remove trailing spaces and tabs
        fixed_line = line.rstrip(" \t")
        fixed_lines.append(fixed_line)

    return "\n".join(fixed_lines)


def fix_indentation_consistency(content):
    """Fix indentation to be consistent 4-space multiples"""
    lines = content.split("\n")
    fixed_lines = []

    for line in lines:
        if not line.strip():  # Empty line
            fixed_lines.append("")
            continue

        # Convert tabs to spaces
        line = line.replace("\t", "    ")

        # Get the content and leading spaces
        content_part = line.lstrip(" ")
        leading_spaces = len(line) - len(content_part)

        if leading_spaces > 0:
            # Round to nearest 4-space multiple
            corrected_spaces = (leading_spaces + 2) // 4 * 4
            # But don't reduce indentation too much - preserve basic structure
            if corrected_spaces < leading_spaces - 2:
                corrected_spaces = leading_spaces
            fixed_line = " " * corrected_spaces + content_part
        else:
            fixed_line = line

        fixed_lines.append(fixed_line)

    return "\n".join(fixed_lines)


def fix_quotes_to_double(content):
    """Convert single quotes to double quotes where reasonable"""
    # This is a simple approach - more sophisticated parsing would be better

    # Replace single quotes that are likely string literals
    # Be careful not to replace quotes inside existing strings or comments

    # Simple regex to find single-quoted strings
    single_quote_pattern = r"(?<!\\)'([^'\\]*(\\.[^'\\]*)*)'(?=[\s,;\)\]\}]|$)"

    def replace_single_quote(match):
        inner_content = match.group(1)
        # If the inner content contains double quotes, keep single quotes
        if '"' in inner_content:
            return match.group(0)
        else:
            # Replace with double quotes
            return f'"{inner_content}"'

    content = re.sub(single_quote_pattern, replace_single_quote, content)

    return content


def add_basic_error_handling(content):
    """Add basic try-catch blocks to functions that lack error handling"""
    # Look for async functions without try-catch
    lines = content.split("\n")
    fixed_lines = []
    in_async_function = False
    function_indent = 0
    needs_try_catch = False
    has_try_catch = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Detect async function start
        if re.match(r"\s*async\s+\w+\s*\([^)]*\)\s*{", stripped):
            in_async_function = True
            function_indent = len(line) - len(line.lstrip())
            needs_try_catch = True
            has_try_catch = False
            fixed_lines.append(line)

        # Detect if function already has try-catch
        elif in_async_function and "try" in stripped:
            has_try_catch = True
            fixed_lines.append(line)

        # Detect end of function
        elif (
            in_async_function
            and stripped == "}"
            and len(line) - len(line.lstrip()) == function_indent
        ):
            # End of function - add try-catch if needed
            if needs_try_catch and not has_try_catch and len(fixed_lines) > 1:
                # Insert try-catch around function body
                function_start_idx = len(fixed_lines) - 1
                while (
                    function_start_idx > 0
                    and "async" not in fixed_lines[function_start_idx]
                ):
                    function_start_idx -= 1

                # Simple approach: just add a catch block before the closing brace
                indent = " " * (function_indent + 4)
                catch_block = [
                    indent + "} catch (error) {",
                    indent + '    console.error("Error:", error);',
                    indent + "    throw error;",
                ]

                # Insert catch block before closing brace
                for catch_line in catch_block:
                    fixed_lines.append(catch_line)

            fixed_lines.append(line)
            in_async_function = False

        else:
            fixed_lines.append(line)

        i += 1

    return "\n".join(fixed_lines)


def fix_typos(content):
    """Fix common typos in the code"""
    # Fix the typo in voice.js: stopRecordiing -> stopRecording
    content = content.replace("stopRecordiing", "stopRecording")

    # Fix other common typos
    content = content.replace("cleartimeout", "clearTimeout")
    content = content.replace("settimeout", "setTimeout")
    content = content.replace("gettime", "getTime")
    content = content.replace("tokenexpiry", "tokenExpiry")
    content = content.replace("refreshtimer", "refreshTimer")
    content = content.replace("backendclient", "backendClient")
    content = content.replace("refreshauthtoken", "refreshAuthToken")
    content = content.replace("clearauth", "clearAuth")
    content = content.replace("getavailableproviders", "getAvailableProviders")

    return content


def clean_regex_false_positives(content):
    """Clean up patterns that trigger false positives in security tests"""
    # The security test is detecting ', error);\n' as a token pattern
    # This is a false positive - it's just error handling code

    # We don't need to change the actual code since it's correct,
    # but we could make the test smarter instead
    return content


def process_js_file(file_path):
    """Process a single JavaScript file to fix all quality issues"""
    print(f"Processing {file_path.name}...")

    # Read original content
    content = file_path.read_text(encoding="utf-8")

    # Apply fixes in order
    content = fix_trailing_whitespace(content)
    content = fix_indentation_consistency(content)
    # content = fix_quotes_to_double(content)  # Skip for now - too complex
    content = fix_typos(content)
    # content = add_basic_error_handling(content)  # Skip for now - too complex
    content = clean_regex_false_positives(content)

    # Write back to file
    file_path.write_text(content, encoding="utf-8")

    print(f"  ✅ Fixed {file_path.name}")


def main():
    """Main function to fix all JavaScript files"""
    plugin_dir = Path(".obsidian/plugins/obsidian-ai-assistant")

    if not plugin_dir.exists():
        print("❌ Plugin directory not found!")
        return

    js_files = list(plugin_dir.glob("*.js"))

    print(f"🔧 Fixing quality issues in {len(js_files)} JavaScript files...")
    print("=" * 60)

    for js_file in js_files:
        try:
            process_js_file(js_file)
        except Exception as e:
            print(f"  ❌ Error processing {js_file.name}: {e}")

    print("=" * 60)
    print(f"🎉 Finished processing {len(js_files)} JavaScript files!")
    print("\n🧪 Now run the tests again to check improvements:")
    print("python -m pytest tests/obsidian-ai-assistant/test_js_code_quality.py -v")


if __name__ == "__main__":
    main()
