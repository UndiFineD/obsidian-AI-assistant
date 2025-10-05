#!/usr/bin/env python3
"""
Quick System Status Check for Obsidian AI Assistant
"""

import requests
import json
from pathlib import Path

def check_system_status():
    print("🔍 Obsidian AI Assistant - System Status Check")
    print("=" * 50)
    
    # 1. Backend Status
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Server: ONLINE ({data.get('backend_mode', 'unknown')} mode)")
        else:
            print(f"❌ Backend Server: ERROR (HTTP {response.status_code})")
    except:
        print("❌ Backend Server: OFFLINE")
    
    # 2. Quick AI Test
    try:
        test_request = {
            "question": "Hello AI, are you working?",
            "model_name": "qwen2.5-0.5b-instruct"
        }
        response = requests.post("http://127.0.0.1:8000/ask", json=test_request, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Responses: WORKING (Model: {data.get('model_used', 'unknown')})")
        else:
            print(f"❌ AI Responses: ERROR (HTTP {response.status_code})")
    except:
        print("❌ AI Responses: FAILED")
    
    # 3. Plugin Files
    vault_path = Path("C:/Users/kdejo/DEV/Vault/.obsidian/plugins/obsidian-ai-assistant")
    required_files = ["main.js", "manifest.json", "styles.css"]
    
    all_files_present = True
    for file in required_files:
        if (vault_path / file).exists():
            print(f"✅ Plugin File ({file}): DEPLOYED")
        else:
            print(f"❌ Plugin File ({file}): MISSING")
            all_files_present = False
    
    # 4. Overall Status
    print("\n" + "=" * 50)
    if all_files_present:
        print("🎉 SYSTEM STATUS: READY FOR OBSIDIAN!")
        print("   • Open Obsidian")
        print("   • Enable 'AI Assistant' plugin") 
        print("   • Look for 🧠 brain icon in ribbon")
        print("   • Ask AI questions!")
    else:
        print("⚠️  SYSTEM STATUS: NEEDS ATTENTION")
        print("   • Some plugin files missing")
        print("   • Run deployment commands")

if __name__ == "__main__":
    check_system_status()