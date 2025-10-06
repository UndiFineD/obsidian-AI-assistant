# tests/integration/run_integration_tests.py
"""
Integration test runner for the Obsidian AI Assistant.
Runs all integration tests in proper order and provides comprehensive reporting.
"""
import pytest
import sys
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class IntegrationTestRunner:
    """Manages and runs integration tests with proper sequencing and reporting."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.results: Dict[str, Dict] = {}
        
    def discover_integration_tests(self) -> List[Path]:
        """Discover all integration test files."""
        test_files = []
        for file in self.test_dir.glob("test_*.py"):
            if file.name != "run_integration_tests.py":
                test_files.append(file)
        
        # Sort tests by logical execution order
        ordered_tests = []
        test_order = [
            "test_service_integration.py",    # Services first
            "test_full_workflow.py",          # Full workflows
            "test_api_integration.py",        # API endpoints last
        ]
        
        # Add tests in preferred order
        for test_name in test_order:
            test_path = self.test_dir / test_name
            if test_path in test_files:
                ordered_tests.append(test_path)
                test_files.remove(test_path)
        
        # Add any remaining tests
        ordered_tests.extend(sorted(test_files))
        
        return ordered_tests
        
    def run_test_file(self, test_file: Path) -> Tuple[bool, Dict]:
        """Run a single integration test file and capture results."""
        print(f"\n🧪 Running {test_file.name}")
        print("=" * 50)
        
        start_time = time.time()
        
        # Run pytest programmatically
        pytest_args = [
            str(test_file),
            "-v",
            "--tb=short",
            "--no-header",
            "--quiet"
        ]
        
        result_code = pytest.main(pytest_args)
        
        end_time = time.time()
        duration = end_time - start_time
        
        success = result_code == 0
        
        results = {
            "success": success,
            "duration": duration,
            "pytest_code": result_code
        }
        
        if success:
            print(f"✅ {test_file.name} passed in {duration:.2f}s")
        else:
            print(f"❌ {test_file.name} failed in {duration:.2f}s")
            
        return success, results
        
    def run_all_integration_tests(self) -> bool:
        """Run all integration tests in sequence."""
        print("🚀 Starting Integration Test Suite")
        print("==================================")
        print(f"Test directory: {self.test_dir}")
        
        # Discover tests
        test_files = self.discover_integration_tests()
        
        if not test_files:
            print("⚠️  No integration test files found!")
            return False
            
        print(f"Found {len(test_files)} integration test files:")
        for test_file in test_files:
            print(f"  - {test_file.name}")
            
        # Run tests sequentially
        total_success = True
        total_duration = 0.0
        
        for test_file in test_files:
            success, results = self.run_test_file(test_file)
            self.results[test_file.name] = results
            
            if not success:
                total_success = False
                
            total_duration += results["duration"]
            
        # Print final summary
        self.print_summary(total_success, total_duration)
        
        return total_success
        
    def print_summary(self, overall_success: bool, total_duration: float):
        """Print comprehensive test results summary."""
        print("\n" + "=" * 60)
        print("🏁 Integration Test Suite Summary")
        print("=" * 60)
        
        passed_count = sum(1 for r in self.results.values() if r["success"])
        failed_count = len(self.results) - passed_count
        
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed: {passed_count}")
        print(f"Failed: {failed_count}")
        print(f"Total Duration: {total_duration:.2f}s")
        
        if overall_success:
            print("\n🎉 ALL INTEGRATION TESTS PASSED! 🎉")
        else:
            print("\n💥 Some integration tests failed")
            
        print("\nDetailed Results:")
        print("-" * 40)
        
        for test_name, results in self.results.items():
            status = "✅ PASS" if results["success"] else "❌ FAIL"
            duration = results["duration"]
            print(f"{status} {test_name:<25} ({duration:.2f}s)")
            
        # Test coverage insights
        print("\n📊 Integration Test Coverage:")
        print("-" * 40)
        
        coverage_areas = [
            ("Service Integration", "test_service_integration.py"),
            ("Full Workflow", "test_full_workflow.py"),  
            ("API Integration", "test_api_integration.py")
        ]
        
        for area, filename in coverage_areas:
            if filename in self.results:
                status = "✅" if self.results[filename]["success"] else "❌"
                print(f"{status} {area}")
            else:
                print(f"⚠️  {area} (not found)")
                
        print("\n" + "=" * 60)


def validate_test_environment():
    """Validate that the test environment is properly set up."""
    print("🔍 Validating test environment...")
    
    # Check Python path
    backend_path = Path(__file__).parent.parent.parent / "backend"
    if not backend_path.exists():
        print(f"❌ Backend directory not found: {backend_path}")
        return False
        
    # Check required dependencies
    required_modules = ["pytest", "httpx", "fastapi"]
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
            
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Install with: pip install " + " ".join(missing_modules))
        return False
        
    print("✅ Test environment validation passed")
    return True


def main():
    """Main entry point for integration test runner."""
    print("🧪 Obsidian AI Assistant - Integration Test Runner")
    print("==================================================")
    
    # Validate environment
    if not validate_test_environment():
        print("❌ Environment validation failed. Cannot run tests.")
        sys.exit(1)
        
    # Initialize and run tests
    runner = IntegrationTestRunner()
    success = runner.run_all_integration_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()