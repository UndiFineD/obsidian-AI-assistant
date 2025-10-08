#!/usr/bin/env python3
"""
Test Enterprise Integration
Tests the complete enterprise feature integration in the plugin.
"""

import os
import sys
import json
import requests
from pathlib import Path

def test_plugin_files():
    """Test that all plugin files exist and are properly structured."""
    print("Testing plugin file structure...")
    
    plugin_dir = Path("plugin")
    required_files = [
        "main.js",
        "adminDashboard.js", 
        "enterpriseAuth.js",
        "enterpriseConfig.js",
        "styles.css",
        "manifest.json"
    ]
    
    for file in required_files:
        file_path = plugin_dir / file
        if not file_path.exists():
            print(f"❌ Missing required file: {file}")
            return False
        else:
            print(f"✅ Found: {file}")
    
    return True

def test_enterprise_imports():
    """Test that main.js properly imports enterprise modules."""
    print("\nTesting enterprise imports in main.js...")
    
    main_js = Path("plugin/main.js")
    if not main_js.exists():
        print("❌ main.js not found")
        return False
    
    content = main_js.read_text(encoding='utf-8')
    
    required_imports = [
        "adminDashboard.js",
        "enterpriseAuth.js", 
        "enterpriseConfig.js"
    ]
    
    for import_file in required_imports:
        if import_file in content:
            print(f"✅ Enterprise import found: {import_file}")
        else:
            print(f"❌ Missing enterprise import: {import_file}")
            return False
    
    return True

def test_enterprise_classes():
    """Test that enterprise classes are properly defined."""
    print("\nTesting enterprise class definitions...")
    
    files_to_check = {
        "adminDashboard.js": ["EnterpriseAdminDashboard"],
        "enterpriseAuth.js": ["EnterpriseAuth"],
        "enterpriseConfig.js": ["EnterpriseConfig"]
    }
    
    for file, classes in files_to_check.items():
        file_path = Path("plugin") / file
        if not file_path.exists():
            print(f"❌ File not found: {file}")
            return False
            
        content = file_path.read_text(encoding='utf-8')
        
        for class_name in classes:
            if f"class {class_name}" in content:
                print(f"✅ Class found in {file}: {class_name}")
            else:
                print(f"❌ Missing class in {file}: {class_name}")
                return False
    
    return True

def test_backend_modules():
    """Test that backend enterprise modules exist."""
    print("\nTesting backend enterprise modules...")
    
    enterprise_dir = Path("backend/enterprise")
    if not enterprise_dir.exists():
        print("⚠️ Enterprise backend directory not found - this is optional")
        return True
    
    expected_modules = [
        "auth.py",
        "tenant.py", 
        "rbac.py",
        "gdpr.py",
        "soc2.py",
        "admin.py",
        "integrations.py"
    ]
    
    for module in expected_modules:
        module_path = enterprise_dir / module
        if module_path.exists():
            print(f"✅ Enterprise module found: {module}")
        else:
            print(f"⚠️ Enterprise module missing: {module} (optional)")
    
    return True

def test_css_styles():
    """Test that enterprise CSS styles are included.""" 
    print("\nTesting enterprise CSS styles...")
    
    styles_path = Path("plugin/styles.css")
    if not styles_path.exists():
        print("❌ styles.css not found")
        return False
    
    content = styles_path.read_text(encoding='utf-8')
    
    required_styles = [
        ".enterprise-admin-panel",
        ".enterprise-nav", 
        ".metric-card",
        ".enterprise-table",
        ".enterprise-form-group"
    ]
    
    for style in required_styles:
        if style in content:
            print(f"✅ Enterprise style found: {style}")
        else:
            print(f"❌ Missing enterprise style: {style}")
            return False
    
    return True

def test_plugin_integration():
    """Test that plugin properly integrates enterprise features."""
    print("\nTesting plugin enterprise integration...")
    
    main_js = Path("plugin/main.js")
    content = main_js.read_text(encoding='utf-8')
    
    integration_points = [
        "this.enterpriseAuth",
        "this.enterpriseConfig", 
        "this.enterpriseAdmin",
        "Enterprise Sign In",
        "Enterprise Configuration",
        "Admin Dashboard"
    ]
    
    for point in integration_points:
        if point in content:
            print(f"✅ Integration point found: {point}")
        else:
            print(f"❌ Missing integration point: {point}")
            return False
    
    return True

def test_configuration():
    """Test configuration file structure."""
    print("\nTesting configuration structure...")
    
    # Test plugin manifest
    manifest_path = Path("plugin/manifest.json")
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            if "id" in manifest and "name" in manifest:
                print("✅ Plugin manifest is valid")
            else:
                print("❌ Plugin manifest missing required fields")
                return False
        except json.JSONDecodeError:
            print("❌ Plugin manifest is invalid JSON")
            return False
    else:
        print("❌ Plugin manifest not found")
        return False
    
    # Test backend config template exists
    config_path = Path("backend/config.yaml")
    if config_path.exists():
        print("✅ Backend config found")
    else:
        print("⚠️ Backend config not found (will use defaults)")
    
    return True

def run_all_tests():
    """Run all enterprise integration tests."""
    print("🚀 Running Enterprise Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Plugin Files", test_plugin_files),
        ("Enterprise Imports", test_enterprise_imports), 
        ("Enterprise Classes", test_enterprise_classes),
        ("Backend Modules", test_backend_modules),
        ("CSS Styles", test_css_styles),
        ("Plugin Integration", test_plugin_integration),
        ("Configuration", test_configuration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"Status: {status}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enterprise integration tests passed!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    success = run_all_tests()
    sys.exit(0 if success else 1)