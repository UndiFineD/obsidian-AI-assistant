#!/usr/bin/env python3
"""
Final Obsidian AI Assistant Plugin Test
Tests the simplified plugin and backend integration
"""

import json
import os
from pathlib import Path

import requests

# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
PLUGIN_DIR = PROJECT_ROOT / ".obsidian" / "plugins" / "obsidian-ai-assistant"
BACKEND_URL = "http://localhost:8000"


def test_plugin_structure():
    """Test the basic plugin file structure"""
    print("🔍 Testing Plugin Structure")
    print("===========================")

    # Test required files from the actual Obsidian plugin folder
    required_files = {
        "main.js": "Main plugin file",
        "manifest.json": "Plugin manifest",
        "styles.css": "Plugin styles",
    }

    for file, description in required_files.items():
        path = PLUGIN_DIR / file
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {file} ({size:,} bytes) - {description}")
        else:
            print(f"❌ {file} - Missing!")
            raise AssertionError(f"{file} - Missing!")

    assert True


def test_manifest_content():
    """Test manifest.json content"""
    print("\n📋 Testing Manifest Content")
    print("============================")

    manifest_path = PLUGIN_DIR / "manifest.json"
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        required_fields = ["id", "name", "version", "minAppVersion"]
        all_good = True

        for field in required_fields:
            if field in manifest:
                print(f"✅ {field}: {manifest[field]}")
            else:
                print(f"❌ Missing required field: {field}")
                all_good = False

        # Check for reasonable values
        if manifest.get("id") == "obsidian-ai-assistant":
            print("✅ Plugin ID is correct")
        else:
            print(f"⚠️  Plugin ID might be incorrect: {manifest.get('id')}")

        assert all_good, "Manifest validation failed"

    except Exception as e:
        print(f"❌ Error reading manifest: {e}")
        raise AssertionError(f"Error reading manifest: {e}") from e


def test_main_js_structure():
    """Test main.js structure"""
    print("\n📄 Testing Main.js Structure")
    print("=============================")

    main_path = PLUGIN_DIR / "main.js"
    try:
        with open(main_path, "r", encoding="utf-8") as f:
            content = f.read()

        checks = {
            "Has Plugin class": "class" in content and "Plugin" in content,
            "Has onload method": "onload" in content,
            "Has onunload method": "onunload" in content,
            "Has module export": "module.exports" in content,
            "Has Modal class": "Modal" in content,
            "Has Notice usage": "Notice" in content,
        }

        for check, result in checks.items():
            if result:
                print(f"✅ {check}")
            else:
                print(f"❌ {check}")
                raise AssertionError(f"Failed check: {check}")

        print(f"📊 File size: {len(content):,} characters")
        print(f"📊 Lines of code: {len(content.splitlines())}")

        assert True

    except Exception as e:
        print(f"❌ Error reading main.js: {e}")
        raise AssertionError(f"Error reading main.js: {e}") from e


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
                assert True
            except json.JSONDecodeError as e:
                print("⚠️  Backend responding but not returning JSON")
                raise AssertionError("Backend responding but not returning JSON") from e
        else:
            print(f"❌ Backend returned status {response.status_code}")
            raise AssertionError(f"Backend returned status {response.status_code}")

    except requests.RequestException as e:
        print(f"❌ Backend not available: {e}")
        print("💡 Start the backend with: python test_server.py")
        raise AssertionError(f"Backend not available: {e}") from e


def test_backend_endpoints():
    """Test backend API endpoints"""
    print("\n🔌 Testing Backend API Endpoints")
    print("=================================")

    try:
        # Test ask endpoint
        response = requests.post(
            f"{BACKEND_URL}/ask",
            json={"question": "Test question for plugin integration"},
            timeout=5,
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ /ask endpoint working")
            # Ensure we can safely print a preview regardless of type
            preview = str(data.get("answer", "No answer key in response"))
            print(f"   Response: {preview[:50]}...")
            assert True
        elif response.status_code == 500:
            # Acceptable in environments without a local model available
            data = response.json()
            print(
                "⚠️  /ask endpoint returned 500 as expected in test env without models"
            )
            assert "detail" in data
            assert (
                "Model unavailable" in data["detail"]
                or "failed to generate" in data["detail"]
            )
        else:
            print(f"❌ /ask endpoint returned {response.status_code}")
            raise AssertionError(f"/ask endpoint returned {response.status_code}")

    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        raise AssertionError(f"Error testing endpoints: {e}") from e


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
        ("Backend Endpoints", test_backend_endpoints),
    ]

    passed = 0
    total = len(tests)

    for name, func in tests:
        try:
            if func():
                passed += 1
            else:
                print(f"⚠️  {name} test had issues")
        except Exception as e:
            import traceback

            print(f"❌ {name} test failed with an unexpected error: {e}")
            traceback.print_exc()

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
