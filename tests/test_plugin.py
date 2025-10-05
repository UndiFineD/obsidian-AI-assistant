#!/usr/bin/env python3
"""
Pure Python test script for the Obsidian AI Assistant Plugin
Tests plugin files, structure, and backend API functionality
"""

# This file is a standalone script, not a pytest suite. Skip during pytest collection.
try:
    import pytest  # type: ignore
    pytestmark = pytest.mark.skip(reason="tests/test_plugin.py is a standalone script, not a pytest test")
except Exception:
    pass

import os
import json
import requests
import time
from pathlib import Path

# Configuration
PLUGIN_DIR = r"C:\Users\kdejo\DEV\Vault\.obsidian\plugins\obsidian-ai-assistant"
BACKEND_URL = "http://localhost:8000"
tests_passed = 0
tests_failed = 0

def run_test(test_name, test_function):
    """Run a test and track results"""
    global tests_passed, tests_failed
    try:
        result = test_function()
        if result:
            print(f"✅ {test_name}")
            tests_passed += 1
        else:
            print(f"❌ {test_name}")
            tests_failed += 1
        return result
    except Exception as error:
        print(f"❌ {test_name} - Error: {error}")
        tests_failed += 1
        return False

def test_file_exists(filename):
    """Test if a file exists in the plugin directory"""
    return os.path.exists(os.path.join(PLUGIN_DIR, filename))

def test_file_content(filename, content_checks):
    """Test if file contains required content"""
    filepath = os.path.join(PLUGIN_DIR, filename)
    if not os.path.exists(filepath):
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return all(check in content for check in content_checks)

def test_manifest_json():
    """Test manifest.json structure"""
    manifest_path = os.path.join(PLUGIN_DIR, 'manifest.json')
    if not os.path.exists(manifest_path):
        return False
    
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_fields = ['id', 'name', 'version', 'minAppVersion']
        if not all(field in manifest for field in required_fields):
            return False
        
        print(f"   📋 Plugin ID: {manifest.get('id')}")
        print(f"   📋 Plugin Name: {manifest.get('name')}")
        print(f"   📋 Version: {manifest.get('version')}")
        
        return True
    except json.JSONDecodeError:
        return False

def test_backend_endpoint(endpoint, method='GET', data=None):
    """Test a backend API endpoint"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        
        return response.status_code == 200
    except requests.RequestException:
        return False

def test_backend_json_response(endpoint, method='GET', data=None):
    """Test that backend returns valid JSON"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            response.json()  # This will raise if not valid JSON
            return True
        return False
    except (requests.RequestException, json.JSONDecodeError):
        return False

def main():
    print('🧪 Testing Obsidian AI Assistant Plugin')
    print('=====================================')
    print()

    # Plugin File Tests
    print('📂 Plugin File Tests')
    print('=====================')
    
    run_test('Plugin directory exists', lambda: os.path.exists(PLUGIN_DIR))
    run_test('main.js exists', lambda: test_file_exists('main.js'))
    run_test('manifest.json exists', lambda: test_file_exists('manifest.json'))
    run_test('styles.css exists', lambda: test_file_exists('styles.css'))
    
    # Plugin Structure Tests
    print('\n🏗️  Plugin Structure Tests')
    print('==========================')
    
    run_test('main.js contains Plugin class', 
             lambda: test_file_content('main.js', ['class', 'Plugin']))
    
    run_test('main.js contains lifecycle methods', 
             lambda: test_file_content('main.js', ['onload']))
    
    run_test('main.js has module export', 
             lambda: test_file_content('main.js', ['module.exports']))
    
    run_test('manifest.json is valid', test_manifest_json)
    
    # Code Quality Tests
    print('\n🔍 Code Quality Tests')
    print('=====================')
    
    def no_typescript_files():
        files = os.listdir(PLUGIN_DIR)
        ts_files = [f for f in files if f.endswith('.ts')]
        if ts_files:
            print(f"   ⚠️  Found TypeScript files: {', '.join(ts_files)}")
            return False
        return True
    
    run_test('No TypeScript files in plugin directory', no_typescript_files)
    
    def main_js_syntax_check():
        main_path = os.path.join(PLUGIN_DIR, 'main.js')
        if not os.path.exists(main_path):
            return False
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic syntax check - balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        return open_braces == close_braces
    
    run_test('main.js has balanced braces', main_js_syntax_check)
    
    # Backend API Tests
    print('\n🌐 Backend API Tests')
    print('====================')
    
    run_test('Backend server is running', 
             lambda: test_backend_endpoint('/status'))
    
    run_test('Status endpoint returns JSON', 
             lambda: test_backend_json_response('/status'))
    
    run_test('Ask endpoint accepts POST', 
             lambda: test_backend_endpoint('/ask', 'POST', {'prompt': 'test'}))
    
    run_test('Reindex endpoint works', 
             lambda: test_backend_endpoint('/reindex', 'POST', {}))
    
    run_test('Web search endpoint works', 
             lambda: test_backend_endpoint('/web', 'POST', {'query': 'test'}))
    
    # File Inventory
    print('\n📁 Plugin Files Inventory')
    print('=========================')
    
    try:
        files = os.listdir(PLUGIN_DIR)
        required_files = ['main.js', 'manifest.json']
        
        for file in sorted(files):
            if file in required_files:
                print(f"   ✅ {file} (required)")
            else:
                print(f"   📄 {file}")
    except FileNotFoundError:
        print("❌ Plugin directory not found")
    
    # Test Results Summary
    print('\n📊 Test Results Summary')
    print('=======================')
    print(f'✅ Tests Passed: {tests_passed}')
    print(f'❌ Tests Failed: {tests_failed}')
    print(f'📋 Total Tests: {tests_passed + tests_failed}')
    
    if tests_failed == 0:
        print('\n🎉 All tests passed! Plugin is ready for use.')
        success_rate = "100%"
    else:
        success_rate = f"{(tests_passed / (tests_passed + tests_failed)) * 100:.1f}%"
        print(f'\n⚠️  {tests_failed} test(s) failed. Success rate: {success_rate}')
    
    print('\n🎯 Plugin Ready for Testing in Obsidian!')
    print('\nNext steps:')
    print('1. Open Obsidian')
    print('2. Go to Settings > Community Plugins')
    print('3. Enable "Obsidian AI Assistant"')
    print('4. The plugin should appear in your sidebar')
    print('5. Backend API is running on http://localhost:8000')
    
    return tests_failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)