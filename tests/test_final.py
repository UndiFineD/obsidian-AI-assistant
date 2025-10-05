#!/usr/bin/env python3
"""
Final Obsidian AI Assistant Plugin Test
Tests the simplified plugin and backend integration
"""

import os
import json
import requests
import time
from pathlib import Path

# Configuration
PLUGIN_DIR = r"C:\Users\kdejo\DEV\Vault\.obsidian\plugins\obsidian-ai-assistant"
BACKEND_URL = "http://localhost:8000"

def test_plugin_structure():
    """Test the basic plugin file structure"""
    print("🔍 Testing Plugin Structure")
    print("===========================")
    
    # Test required files
    required_files = {
        'main.js': 'Main plugin file',
        'manifest.json': 'Plugin manifest',
        'styles.css': 'Plugin styles'
    }
    
    all_good = True
    for file, description in required_files.items():
        path = os.path.join(PLUGIN_DIR, file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {file} ({size:,} bytes) - {description}")
        else:
            print(f"❌ {file} - Missing!")
            all_good = False
    
    return all_good

def test_manifest_content():
    """Test manifest.json content"""
    print("\n📋 Testing Manifest Content")
    print("============================")
    
    manifest_path = os.path.join(PLUGIN_DIR, 'manifest.json')
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        required_fields = ['id', 'name', 'version', 'minAppVersion']
        all_good = True
        
        for field in required_fields:
            if field in manifest:
                print(f"✅ {field}: {manifest[field]}")
            else:
                print(f"❌ Missing required field: {field}")
                all_good = False
        
        # Check for reasonable values
        if manifest.get('id') == 'obsidian-ai-assistant':
            print("✅ Plugin ID is correct")
        else:
            print(f"⚠️  Plugin ID might be incorrect: {manifest.get('id')}")
        
        return all_good
    
    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        return False

def test_main_js_structure():
    """Test main.js structure"""
    print("\n📄 Testing Main.js Structure")
    print("=============================")
    
    main_path = os.path.join(PLUGIN_DIR, 'main.js')
    try:
        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'Has Plugin class': 'class' in content and 'Plugin' in content,
            'Has onload method': 'onload' in content,
            'Has onunload method': 'onunload' in content,
            'Has module export': 'module.exports' in content,
            'Has Modal class': 'Modal' in content,
            'Has Notice usage': 'Notice' in content
        }
        
        all_good = True
        for check, result in checks.items():
            if result:
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                all_good = False
        
        print(f"📊 File size: {len(content):,} characters")
        print(f"📊 Lines of code: {content.count(chr(10)) + 1}")
        
        return all_good
    
    except Exception as e:
        print(f"❌ Error reading main.js: {e}")
        return False

def test_backend_availability():
    """Test if backend is available"""
    print("\n🌐 Testing Backend Availability")
    print("===============================")
    
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is responding")
            try:
                data = response.json()
                print(f"✅ Backend status: {data.get('status', 'unknown')}")
                return True
            except json.JSONDecodeError:
                print("⚠️  Backend responding but not returning JSON")
                return False
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    
    except requests.RequestException as e:
        print(f"❌ Backend not available: {e}")
        print("💡 Start the backend with: python test_server.py")
        return False

def test_backend_endpoints():
    """Test backend API endpoints"""
    print("\n🔌 Testing Backend API Endpoints")
    print("=================================")
    
    try:
        # Test ask endpoint
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={"prompt": "Test question for plugin integration"},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ /ask endpoint working")
            print(f"   Response: {data.get('response', 'No response')[:50]}...")
            return True
        else:
            print(f"❌ /ask endpoint returned {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Final Obsidian AI Assistant Plugin Test")
    print("===========================================")
    print()
    
    tests = [
        ("Plugin Structure", test_plugin_structure),
    ("Manifest Content", test_manifest_content),
        ("Main.js Structure", test_main_js_structure),
        ("Backend Availability", test_backend_availability),
        ("Backend Endpoints", test_backend_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  {test_name} test had issues")
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
        
        print()  # Add spacing between tests
    
    # Final Summary
    print("📊 Final Test Summary")
    print("====================")
    print(f"✅ Tests Passed: {passed}")
    print(f"❌ Tests Failed: {total - passed}")
    print(f"📋 Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 All tests passed! Plugin is ready!")
        print("\n🚀 Next Steps:")
        print("1. Open Obsidian")
        print("2. Go to Settings > Community Plugins")
        print("3. Find and enable 'AI Assistant'")
        print("4. Look for the brain icon in the ribbon")
        print("5. Use Ctrl+P and search for 'AI Assistant' commands")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)