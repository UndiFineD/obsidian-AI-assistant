#!/usr/bin/env python3
"""
Simple Plugin File Test - focuses on plugin files without backend dependency
"""

import os
import json
from pathlib import Path

# Configuration
PLUGIN_DIR = r"C:\Users\kdejo\DEV\Vault\.obsidian\plugins\obsidian-ai-assistant"
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

def main():
    print('🧪 Obsidian AI Assistant Plugin File Tests')
    print('==========================================')
    print()

    # Core Plugin Tests
    print('📂 Core Plugin Files')
    print('====================')
    
    run_test('Plugin directory exists', 
             lambda: os.path.exists(PLUGIN_DIR))
    
    run_test('main.js exists', 
             lambda: os.path.exists(os.path.join(PLUGIN_DIR, 'main.js')))
    
    run_test('manifest.json exists', 
             lambda: os.path.exists(os.path.join(PLUGIN_DIR, 'manifest.json')))
    
    # Manifest validation
    def test_manifest():
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
    
    run_test('manifest.json is valid JSON with required fields', test_manifest)
    
    # Main.js validation
    def test_main_js():
        main_path = os.path.join(PLUGIN_DIR, 'main.js')
        if not os.path.exists(main_path):
            return False
        
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for plugin structure
        has_class = 'class' in content and 'Plugin' in content
        has_onload = 'onload' in content
        has_export = 'module.exports' in content
        
        print(f"   🔍 Has Plugin class: {has_class}")
        print(f"   🔍 Has onload method: {has_onload}")
        print(f"   🔍 Has module export: {has_export}")
        print(f"   📊 File size: {len(content)} characters")
        
        return has_class and has_onload and has_export
    
    run_test('main.js has correct plugin structure', test_main_js)
    
    # Additional files
    print('\n📁 Additional Plugin Files')
    print('==========================')
    
    optional_files = ['styles.css', 'analyticsPane.js', 'taskQueue.js', 'voice.js']
    
    for file in optional_files:
        run_test(f'{file} exists', 
                lambda f=file: os.path.exists(os.path.join(PLUGIN_DIR, f)))
    
    # File inventory
    print('\n📋 Complete File Inventory')
    print('==========================')
    
    try:
        files = os.listdir(PLUGIN_DIR)
        required_files = ['main.js', 'manifest.json']
        
        print(f"Total files: {len(files)}")
        for file in sorted(files):
            size = os.path.getsize(os.path.join(PLUGIN_DIR, file))
            if file in required_files:
                print(f"   ✅ {file} ({size:,} bytes) - REQUIRED")
            else:
                print(f"   📄 {file} ({size:,} bytes)")
                
        # Check for unwanted files
        ts_files = [f for f in files if f.endswith('.ts')]
        if ts_files:
            print(f"\n⚠️  TypeScript files found: {', '.join(ts_files)}")
            run_test('No TypeScript files in production', lambda: len(ts_files) == 0)
        else:
            run_test('No TypeScript files in production', lambda: True)
            
    except FileNotFoundError:
        print("❌ Plugin directory not accessible")
    
    # Summary
    print('\n📊 Test Results Summary')
    print('=======================')
    print(f'✅ Tests Passed: {tests_passed}')
    print(f'❌ Tests Failed: {tests_failed}')
    print(f'📋 Total Tests: {tests_passed + tests_failed}')
    
    if tests_failed == 0:
        print('\n🎉 All plugin file tests passed!')
        print('🚀 Plugin is ready for installation in Obsidian!')
    else:
        success_rate = f"{(tests_passed / (tests_passed + tests_failed)) * 100:.1f}%"
        print(f'\n⚠️  {tests_failed} test(s) failed. Success rate: {success_rate}')
    
    print('\n🎯 Installation Instructions:')
    print('1. Open Obsidian')
    print('2. Go to Settings > Community Plugins')  
    print('3. Turn on "Community plugins" if not enabled')
    print('4. Click "Browse" or scroll to find "Obsidian AI Assistant"')
    print('5. Enable the plugin')
    print('6. Check if the plugin appears in your ribbon or command palette')
    
    return tests_failed == 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)