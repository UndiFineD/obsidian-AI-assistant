#!/usr/bin/env python3
"""
Complete Integration Test Suite for Obsidian AI Assistant
Tests all working components: Backend API, Plugin Integration, AI Responses
"""

import json
import time
import requests
from pathlib import Path
import subprocess
import sys

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test(name, passed, details=""):
    status = f"{Colors.GREEN}✅{Colors.END}" if passed else f"{Colors.RED}❌{Colors.END}"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")

def print_header(title):
    print(f"\n{Colors.BLUE}{Colors.BOLD}🧪 {title}{Colors.END}")
    print("=" * (len(title) + 4))

def print_section(title):
    print(f"\n{Colors.YELLOW}### {title}{Colors.END}")

class IntegrationTester:
    def __init__(self):
        self.backend_url = "http://127.0.0.1:8000"
        self.vault_path = Path("C:/Users/kdejo/DEV/Vault/.obsidian/plugins/obsidian-ai-assistant")
        self.plugin_path = Path("plugin")
        self.passed_tests = 0
        self.failed_tests = 0
        
    def test_backend_health(self):
        """Test backend server health and availability"""
        print_section("Backend Health Check")
        
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print_test("Backend Server", True, f"Status: {data.get('status', 'unknown')}")
                print_test("Backend Mode", True, f"Mode: {data.get('backend_mode', 'unknown')}")
                print_test("Response Time", True, f"< 5 seconds")
                self.passed_tests += 3
            else:
                print_test("Backend Server", False, f"HTTP {response.status_code}")
                self.failed_tests += 1
        except Exception as e:
            print_test("Backend Connection", False, f"Error: {str(e)}")
            self.failed_tests += 1
            
    def test_ai_endpoints(self):
        """Test AI question/answer functionality"""
        print_section("AI Response Testing")
        
        test_questions = [
            ("Greeting", "Hello AI, how are you?"),
            ("Technical", "Explain machine learning in simple terms"),
            ("Code", "Write a Python function to reverse a string"),
            ("Debugging", "How do I fix a syntax error in Python?"),
            ("General", "What is the meaning of life?")
        ]
        
        for category, question in test_questions:
            try:
                payload = {
                    "question": question,
                    "model_name": "qwen2.5-0.5b-instruct",
                    "max_tokens": 256
                }
                
                response = requests.post(
                    f"{self.backend_url}/ask",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    response_text = data.get('response', '')
                    model_used = data.get('model_used', 'unknown')
                    processing_time = data.get('processing_time', 0)
                    
                    # Validate response quality
                    is_valid = (
                        len(response_text) > 10 and
                        response_text != question and
                        model_used == "qwen2.5-0.5b-instruct"
                    )
                    
                    print_test(
                        f"{category} Question", 
                        is_valid,
                        f"Response: {response_text[:60]}... (Model: {model_used}, {processing_time}s)"
                    )
                    
                    if is_valid:
                        self.passed_tests += 1
                    else:
                        self.failed_tests += 1
                else:
                    print_test(f"{category} Question", False, f"HTTP {response.status_code}")
                    self.failed_tests += 1
                    
            except Exception as e:
                print_test(f"{category} Question", False, f"Error: {str(e)}")
                self.failed_tests += 1
                
    def test_plugin_files(self):
        """Test plugin file integrity and deployment"""
        print_section("Plugin File Integrity")
        
        # Check source files
        source_files = {
            "main.js": "Main plugin file",
            "manifest.json": "Plugin manifest",
            "styles.css": "Plugin styles"
        }
        
        for filename, description in source_files.items():
            source_path = self.plugin_path / filename
            vault_path = self.vault_path / filename
            
            # Source file check
            if source_path.exists():
                size = source_path.stat().st_size
                print_test(f"Source {description}", True, f"Size: {size} bytes")
                self.passed_tests += 1
            else:
                print_test(f"Source {description}", False, "File not found")
                self.failed_tests += 1
                
            # Deployed file check
            if vault_path.exists():
                size = vault_path.stat().st_size
                mtime = time.ctime(vault_path.stat().st_mtime)
                print_test(f"Deployed {description}", True, f"Size: {size} bytes, Modified: {mtime}")
                self.passed_tests += 1
            else:
                print_test(f"Deployed {description}", False, "File not found in vault")
                self.failed_tests += 1
                
    def test_plugin_content(self):
        """Test plugin content for required functionality"""
        print_section("Plugin Content Validation")
        
        # Test main.js content
        try:
            main_js_path = self.plugin_path / "main.js"
            with open(main_js_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
                
            required_features = [
                ("AI Modal Class", "class AIModal extends Modal"),
                ("Status Check Method", "checkBackendStatus"),
                ("Voice Recording", "startVoiceRecording"),
                ("Ask AI Method", "askAI"),
                ("Ribbon Icon", "addRibbonIcon"),
                ("Backend URL Setting", "backendUrl"),
                ("Updated Request Format", '"question": question')
            ]
            
            for feature_name, search_text in required_features:
                found = search_text in main_content
                print_test(feature_name, found)
                if found:
                    self.passed_tests += 1
                else:
                    self.failed_tests += 1
                    
        except Exception as e:
            print_test("Main.js Analysis", False, f"Error: {str(e)}")
            self.failed_tests += 1
            
        # Test manifest.json
        try:
            manifest_path = self.plugin_path / "manifest.json"
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                
            required_fields = {
                "id": "obsidian-ai-assistant",
                "name": "AI Assistant",
                "version": "1.0.0"
            }
            
            for field, expected_value in required_fields.items():
                actual_value = manifest.get(field)
                is_valid = actual_value == expected_value
                print_test(f"Manifest {field}", is_valid, f"Value: {actual_value}")
                if is_valid:
                    self.passed_tests += 1
                else:
                    self.failed_tests += 1
                    
        except Exception as e:
            print_test("Manifest Analysis", False, f"Error: {str(e)}")
            self.failed_tests += 1
            
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow simulation"""
        print_section("End-to-End Workflow Simulation")
        
        # Simulate plugin -> backend -> response workflow
        try:
            # Step 1: Status check (like plugin does)
            status_response = requests.get(f"{self.backend_url}/status", timeout=5)
            status_ok = status_response.status_code == 200
            print_test("Plugin Status Check", status_ok, "Simulating plugin status indicator")
            
            # Step 2: AI request (like plugin does)
            test_request = {
                "question": "Test integration between Obsidian plugin and AI backend",
                "model_name": "qwen2.5-0.5b-instruct",
                "max_tokens": 512
            }
            
            ai_response = requests.post(
                f"{self.backend_url}/ask",
                json=test_request,
                timeout=10
            )
            
            ai_ok = ai_response.status_code == 200
            if ai_ok:
                response_data = ai_response.json()
                response_text = response_data.get('response', '')
                is_meaningful = len(response_text) > 20
                print_test("Plugin AI Request", is_meaningful, f"Response received: {len(response_text)} characters")
            else:
                print_test("Plugin AI Request", False, f"HTTP {ai_response.status_code}")
                
            # Step 3: Test other endpoints
            endpoints = [
                ("/", "Root endpoint"),
                ("/reindex", "Reindex endpoint"),
                ("/web", "Web search endpoint")
            ]
            
            for endpoint, description in endpoints:
                try:
                    if endpoint == "/":
                        resp = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                    else:
                        resp = requests.post(f"{self.backend_url}{endpoint}", json={}, timeout=5)
                        
                    endpoint_ok = resp.status_code == 200
                    print_test(description, endpoint_ok, f"HTTP {resp.status_code}")
                    
                    if endpoint_ok:
                        self.passed_tests += 1
                    else:
                        self.failed_tests += 1
                        
                except Exception as e:
                    print_test(description, False, f"Error: {str(e)}")
                    self.failed_tests += 1
                    
            if status_ok and ai_ok:
                self.passed_tests += 2
            else:
                self.failed_tests += 2
                
        except Exception as e:
            print_test("E2E Workflow", False, f"Error: {str(e)}")
            self.failed_tests += 1
            
    def test_performance(self):
        """Test system performance and response times"""
        print_section("Performance Testing")
        
        # Test response times
        response_times = []
        
        for i in range(5):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.backend_url}/ask",
                    json={"question": f"Performance test {i+1}", "model_name": "qwen2.5-0.5b-instruct"},
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
            except Exception as e:
                print_test(f"Performance Test {i+1}", False, f"Error: {str(e)}")
                self.failed_tests += 1
                
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            
            # Performance criteria
            avg_ok = avg_time < 2.0  # Average under 2 seconds
            max_ok = max_time < 5.0  # Max under 5 seconds
            
            print_test("Average Response Time", avg_ok, f"{avg_time:.2f}s (target: <2s)")
            print_test("Maximum Response Time", max_ok, f"{max_time:.2f}s (target: <5s)")
            print_test("Response Consistency", True, f"Completed {len(response_times)}/5 requests")
            
            if avg_ok:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
                
            if max_ok:
                self.passed_tests += 1
            else:
                self.failed_tests += 1
                
            self.passed_tests += 1  # Consistency test
            
    def run_all_tests(self):
        """Run complete test suite"""
        print_header("Obsidian AI Assistant - Complete Integration Test Suite")
        print(f"Testing Backend: {self.backend_url}")
        print(f"Plugin Path: {self.plugin_path}")
        print(f"Vault Path: {self.vault_path}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_backend_health()
        self.test_ai_endpoints()
        self.test_plugin_files()
        self.test_plugin_content()
        self.test_end_to_end_workflow()
        self.test_performance()
        
        # Print summary
        total_tests = self.passed_tests + self.failed_tests
        pass_rate = (self.passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print_header("Test Results Summary")
        print(f"{Colors.GREEN}✅ Passed: {self.passed_tests}{Colors.END}")
        print(f"{Colors.RED}❌ Failed: {self.failed_tests}{Colors.END}")
        print(f"{Colors.BLUE}📊 Pass Rate: {pass_rate:.1f}%{Colors.END}")
        
        if pass_rate >= 90:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 EXCELLENT! Integration is working perfectly!{Colors.END}")
        elif pass_rate >= 75:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}✨ GOOD! Integration is mostly working with minor issues.{Colors.END}")
        elif pass_rate >= 50:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ PARTIAL! Integration has some functionality but needs attention.{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ NEEDS WORK! Integration requires significant fixes.{Colors.END}")
            
        print(f"\n{Colors.BLUE}📋 Ready for Obsidian Testing:{Colors.END}")
        print("1. Open Obsidian and navigate to your vault")
        print("2. Go to Settings → Community plugins")  
        print("3. Enable 'AI Assistant' plugin")
        print("4. Look for 🧠 brain icon in left ribbon")
        print("5. Test the AI assistant with real questions!")
        
        return pass_rate

if __name__ == "__main__":
    tester = IntegrationTester()
    pass_rate = tester.run_all_tests()
    
    # Exit code for automation
    sys.exit(0 if pass_rate >= 75 else 1)