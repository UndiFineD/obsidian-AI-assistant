#!/usr/bin/env python3
"""
Comprehensive Test Runner for Obsidian AI Assistant
Provides numbered tests with timing and colored status results.
"""

import os
import sys
import time
import subprocess
import pytest
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStatus(Enum):
    """Test status enumeration."""
    PASSED = "PASSED"
    FAILED = "FAILED" 
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    RUNNING = "RUNNING"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """Apply color to text."""
        return f"{color}{text}{cls.RESET}"


@dataclass
class TestResult:
    """Individual test result data."""
    number: int
    name: str
    status: TestStatus
    duration: float
    file_path: str
    error_message: Optional[str] = None


class ComprehensiveTestRunner:
    """Main test runner class."""
    
    def __init__(self):
        self.test_root = Path(__file__).parent
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.test_count = 0
        
    def discover_all_tests(self) -> List[Path]:
        """Discover all test files in the project."""
        test_files = []
        
        # Define test discovery patterns
        patterns = [
            "test_*.py",
            "*_test.py"
        ]
        
        # Search in all relevant directories
        search_dirs = [
            self.test_root / "backend",
            self.test_root / "integration", 
            self.test_root / "plugin",
            self.test_root  # Root level tests
        ]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for pattern in patterns:
                    test_files.extend(search_dir.glob(pattern))
                    
        # Remove duplicates and sort
        test_files = sorted(list(set(test_files)))
        
        # Filter out specific files to exclude
        exclude_patterns = [
            "*simple*",
            "*comprehensive_original*", 
            "*_fixed*",
            "*_extended*",
            "*test_plugin.py",  # Keep only the newer plugin tests
            "test_server.py",
            "simple_backend.py"
        ]
        
        filtered_files = []
        for test_file in test_files:
            should_exclude = False
            for exclude_pattern in exclude_patterns:
                if test_file.match(exclude_pattern):
                    should_exclude = True
                    break
            if not should_exclude:
                filtered_files.append(test_file)
                
        return filtered_files
        
    def get_test_functions_from_file(self, file_path: Path) -> List[str]:
        """Extract test function names from a file."""
        test_functions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find test functions and test methods
            patterns = [
                r'def\s+(test_\w+)',  # Standalone test functions
                r'def\s+(test_\w+)\s*\(',  # Test functions with parameters
                r'async\s+def\s+(test_\w+)'  # Async test functions
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                test_functions.extend(matches)
                
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")
            
        return list(set(test_functions))  # Remove duplicates
        
    def print_header(self):
        """Print the test runner header."""
        print("\n" + "=" * 80)
        print(Colors.colorize("🧪 OBSIDIAN AI ASSISTANT - COMPREHENSIVE TEST SUITE", Colors.BOLD + Colors.CYAN))
        print("=" * 80)
        print(f"Test Discovery: {Colors.colorize('ACTIVE', Colors.GREEN)}")
        print(f"Timestamp: {Colors.colorize(time.strftime('%Y-%m-%d %H:%M:%S'), Colors.BLUE)}")
        print("=" * 80 + "\n")
        
    def print_test_status(self, test_num: int, total_tests: int, test_name: str, 
                         status: TestStatus, duration: float = 0.0):
        """Print individual test status with colors and timing."""
        
        # Color mapping for status
        status_colors = {
            TestStatus.PASSED: Colors.GREEN,
            TestStatus.FAILED: Colors.RED,
            TestStatus.ERROR: Colors.RED,
            TestStatus.SKIPPED: Colors.YELLOW,
            TestStatus.RUNNING: Colors.CYAN
        }
        
        # Status symbols
        status_symbols = {
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌", 
            TestStatus.ERROR: "💥",
            TestStatus.SKIPPED: "⏭️",
            TestStatus.RUNNING: "🔄"
        }
        
        # Format timing
        if duration > 0:
            time_str = f"{duration:.3f}s"
        else:
            time_str = "---"
            
        # Format test counter
        counter_str = f"[{test_num:3d}/{total_tests:3d}]"
        
        # Format status with color
        status_color = status_colors.get(status, Colors.WHITE)
        symbol = status_symbols.get(status, "?")
        status_str = Colors.colorize(f"{symbol} {status.value}", status_color)
        
        # Truncate test name if too long
        max_name_len = 50
        if len(test_name) > max_name_len:
            display_name = test_name[:max_name_len-3] + "..."
        else:
            display_name = test_name.ljust(max_name_len)
            
        # Print formatted line
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] {counter_str} {display_name} {status_str} ({time_str})")
        
    def run_single_test_file(self, test_file: Path) -> List[TestResult]:
        """Run a single test file and return results."""
        results = []
        relative_path = test_file.relative_to(self.test_root.parent)
        
        print(f"\n{Colors.colorize(f'📁 Running {relative_path}', Colors.BOLD + Colors.BLUE)}")
        
        # Get individual test functions
        test_functions = self.get_test_functions_from_file(test_file)
        
        if not test_functions:
            # If we can't parse functions, run the whole file
            test_functions = [f"{test_file.stem}::ALL_TESTS"]
            
        for i, test_func in enumerate(test_functions):
            self.test_count += 1
            
            # Show running status
            self.print_test_status(
                self.test_count, 
                len(test_functions), 
                test_func,
                TestStatus.RUNNING
            )
            
            start_time = time.time()
            
            try:
                # Run individual test
                if test_func.endswith("::ALL_TESTS"):
                    # Run entire file
                    cmd = ["python", "-m", "pytest", str(test_file), "-v", "--tb=short", "-q"]
                else:
                    # Run specific test function
                    cmd = ["python", "-m", "pytest", f"{test_file}::{test_func}", "-v", "--tb=short", "-q"]
                    
                result = subprocess.run(
                    cmd,
                    cwd=self.test_root.parent,
                    capture_output=True,
                    text=True,
                    timeout=60  # 60 second timeout per test
                )
                
                duration = time.time() - start_time
                
                # Determine status based on return code
                if result.returncode == 0:
                    status = TestStatus.PASSED
                    error_msg = None
                elif result.returncode == 5:  # No tests collected
                    status = TestStatus.SKIPPED 
                    error_msg = "No tests collected"
                else:
                    status = TestStatus.FAILED
                    error_msg = result.stdout + result.stderr
                    
            except subprocess.TimeoutExpired:
                duration = 60.0
                status = TestStatus.ERROR
                error_msg = "Test timeout (60s)"
            except Exception as e:
                duration = time.time() - start_time
                status = TestStatus.ERROR
                error_msg = str(e)
                
            # Create result record
            test_result = TestResult(
                number=self.test_count,
                name=test_func,
                status=status,
                duration=duration,
                file_path=str(relative_path),
                error_message=error_msg
            )
            
            results.append(test_result)
            self.results.append(test_result)
            
            # Update status display
            self.print_test_status(
                self.test_count,
                self.get_total_test_estimate(),
                test_func,
                status,
                duration
            )
            
        return results
        
    def get_total_test_estimate(self) -> int:
        """Estimate total number of tests (for display purposes)."""
        # This is a rough estimate - we'll update it as we discover more
        return max(100, self.test_count + 20)
        
    def run_all_tests(self) -> Dict:
        """Run all discovered tests."""
        self.print_header()
        
        # Discover all test files
        test_files = self.discover_all_tests()
        
        print(f"📋 Discovered {len(test_files)} test files:")
        for i, test_file in enumerate(test_files, 1):
            rel_path = test_file.relative_to(self.test_root.parent)
            print(f"  {i:2d}. {rel_path}")
            
        print(f"\n🚀 Starting comprehensive test execution...\n")
        
        # Run each test file
        for test_file in test_files:
            try:
                self.run_single_test_file(test_file)
            except KeyboardInterrupt:
                print(f"\n{Colors.colorize('⚠️ Test execution interrupted by user', Colors.YELLOW)}")
                break
            except Exception as e:
                print(f"\n{Colors.colorize(f'💥 Error running {test_file}: {e}', Colors.RED)}")
                continue
                
        # Print final summary
        self.print_summary()
        
        return self.generate_summary_dict()
        
    def print_summary(self):
        """Print comprehensive test summary."""
        total_duration = time.time() - self.start_time
        
        # Count results by status
        status_counts = {
            TestStatus.PASSED: 0,
            TestStatus.FAILED: 0,
            TestStatus.ERROR: 0,
            TestStatus.SKIPPED: 0
        }
        
        total_test_time = 0.0
        for result in self.results:
            status_counts[result.status] += 1
            total_test_time += result.duration
            
        print("\n" + "=" * 80)
        print(Colors.colorize("📊 COMPREHENSIVE TEST SUMMARY", Colors.BOLD + Colors.CYAN))
        print("=" * 80)
        
        # Overall statistics
        total_tests = len(self.results)
        pass_rate = (status_counts[TestStatus.PASSED] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🕐 Total Execution Time: {Colors.colorize(f'{total_duration:.2f}s', Colors.BLUE)}")
        print(f"⚡ Total Test Time: {Colors.colorize(f'{total_test_time:.2f}s', Colors.BLUE)}")
        print(f"🧪 Total Tests: {Colors.colorize(str(total_tests), Colors.BOLD)}")
        print(f"📈 Pass Rate: {Colors.colorize(f'{pass_rate:.1f}%', Colors.GREEN if pass_rate >= 90 else Colors.YELLOW)}")
        
        print("\n📋 Results Breakdown:")
        print(f"  ✅ Passed:  {Colors.colorize(str(status_counts[TestStatus.PASSED]), Colors.GREEN)}")
        print(f"  ❌ Failed:  {Colors.colorize(str(status_counts[TestStatus.FAILED]), Colors.RED)}")
        print(f"  💥 Errors:  {Colors.colorize(str(status_counts[TestStatus.ERROR]), Colors.RED)}")
        print(f"  ⏭️ Skipped: {Colors.colorize(str(status_counts[TestStatus.SKIPPED]), Colors.YELLOW)}")
        
        # Show failed tests if any
        failed_tests = [r for r in self.results if r.status in [TestStatus.FAILED, TestStatus.ERROR]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for result in failed_tests:
                print(f"  {result.number:3d}. {result.name} ({result.file_path})")
                if result.error_message and len(result.error_message) < 100:
                    print(f"       {Colors.colorize(result.error_message.strip(), Colors.RED)}")
                    
        # Performance insights
        slowest_tests = sorted(self.results, key=lambda x: x.duration, reverse=True)[:5]
        if slowest_tests:
            print(f"\n⏱️ Slowest Tests:")
            for i, result in enumerate(slowest_tests, 1):
                print(f"  {i}. {result.name} - {result.duration:.3f}s")
                
        print("=" * 80)
        
        # Final status
        if status_counts[TestStatus.FAILED] == 0 and status_counts[TestStatus.ERROR] == 0:
            print(Colors.colorize("🎉 ALL TESTS PASSED! 🎉", Colors.BOLD + Colors.GREEN))
        else:
            print(Colors.colorize("💥 SOME TESTS FAILED", Colors.BOLD + Colors.RED))
            
        print("=" * 80 + "\n")
        
    def generate_summary_dict(self) -> Dict:
        """Generate summary data as dictionary."""
        status_counts = {
            TestStatus.PASSED: 0,
            TestStatus.FAILED: 0, 
            TestStatus.ERROR: 0,
            TestStatus.SKIPPED: 0
        }
        
        for result in self.results:
            status_counts[result.status] += 1
            
        return {
            "total_tests": len(self.results),
            "passed": status_counts[TestStatus.PASSED],
            "failed": status_counts[TestStatus.FAILED],
            "errors": status_counts[TestStatus.ERROR],
            "skipped": status_counts[TestStatus.SKIPPED],
            "pass_rate": (status_counts[TestStatus.PASSED] / len(self.results) * 100) if self.results else 0,
            "total_duration": time.time() - self.start_time,
            "results": [
                {
                    "number": r.number,
                    "name": r.name,
                    "status": r.status.value,
                    "duration": r.duration,
                    "file_path": r.file_path,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }


def cleanup_old_test_files():
    """Remove redundant and outdated test files."""
    test_root = Path(__file__).parent
    
    # Directories to remove completely
    # This is risky; prefer cleaning specific cache/log files if possible.
    # For now, we will only remove the 'setup' test directory which is safe.
    dirs_to_remove = ["setup"]
    
    files_to_remove = [
        # Redundant backend tests
        "backend/test_caching_extended.py",
        "backend/test_modelmanager_fixed.py",
        
        "test_plugin.py",
        "test_server.py",
    ]
    
    print(Colors.colorize('🧹 CLEANING UP TEST DIRECTORIES', Colors.BOLD + Colors.YELLOW))
    print("=" * 60)
    
    removed_count = 0
    
    # Remove directories first
    for dir_name in dirs_to_remove:
        dir_path = test_root / dir_name
        if dir_path.exists() and dir_path.is_dir():
            try:
                import shutil
                shutil.rmtree(dir_path)
                print(f"  {Colors.colorize('✅ Removed directory:', Colors.GREEN)} {dir_name}")
                removed_count += 1
            except Exception as e:
                print(f"  {Colors.colorize('⚠️ Could not remove directory:', Colors.YELLOW)} {dir_name} - {e}")
    
    # Remove files
    for file_path in files_to_remove:
        full_path = test_root / file_path
        try:
            if full_path.is_file():
                full_path.unlink()
                print(f"  {Colors.colorize('✅ Removed file:', Colors.GREEN)} {file_path}")
                removed_count += 1
        except Exception as e:
            print(f"  {Colors.colorize('⚠️ Could not remove file:', Colors.YELLOW)} {file_path} - {e}")
            
    print(f"\n{Colors.colorize(f'🧹 Cleanup complete: {removed_count} items removed', Colors.BOLD + Colors.GREEN)}")
    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    print(Colors.colorize("🚀 Initializing Comprehensive Test Runner", Colors.BOLD + Colors.CYAN))
    
    # Cleanup old files first
    cleanup_old_test_files()
    
    # Run comprehensive tests
    runner = ComprehensiveTestRunner()
    summary = runner.run_all_tests()
    
    # Save results to JSON for later analysis
    results_file = Path(__file__).parent / "test_results.json"
    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2)
        
    print(f"📄 Detailed results saved to: {results_file}")
    
    # Return appropriate exit code
    if summary["failed"] > 0 or summary["errors"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()