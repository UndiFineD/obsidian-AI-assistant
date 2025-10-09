#!/usr/bin/env python3
"""
Comprehensive Async Test Runner for Obsidian AI Assistant
- Removes redundant test directories and files
- Merges all tests into a unified suite
- Provides numbered tests with timing and colored results
- Runs tests asynchronously where possible for better performance
"""

import os
import sys
import time
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
import re
import shutil
from concurrent.futures import ThreadPoolExecutor
import threading

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestStatus(Enum):
    """Test status enumeration."""
    PASSED = "PASSED"
    FAILED = "FAILED" 
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"
    RUNNING = "RUNNING"
    PENDING = "PENDING"


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
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
    category: str
    start_time: float
    end_time: Optional[float] = None
    error_message: Optional[str] = None
    worker_id: Optional[str] = None


@dataclass
class TestFile:
    """Test file metadata."""
    path: Path
    category: str
    priority: int
    estimated_duration: float
    test_functions: List[str]


class AsyncTestRunner:
    """Async test runner with comprehensive features."""
    
    def __init__(self, max_workers: int = 4):
        self.test_root = Path(__file__).parent
        self.project_root = self.test_root.parent
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.test_count = 0
        self.total_tests = 0
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.lock = threading.Lock()
        self.status_lock = threading.Lock()
        
    def cleanup_test_directories(self):
        """Remove redundant test directories and files."""
        print(f"{Colors.colorize('🧹 CLEANING UP TEST DIRECTORIES', Colors.BOLD + Colors.YELLOW)}")
        print("=" * 60)
        
        # Directories to remove completely
        dirs_to_remove = [
            "cache",
            "models", 
            "vector_db",
            "setup",
            "__pycache__"
        ]
        
        # Files to remove
        files_to_remove = [
            # Redundant backend tests
            "backend/test_backend_comprehensive_original.py",
            "backend/test_backend_simple_fixed.py", 
            "backend/test_caching_extended.py",
            "backend/test_modelmanager_comprehensive_new.py",
            "backend/test_modelmanager_fixed.py",
            
            # Old root level tests
            "test_plugin.py",
            "test_plugin_simple.py",
            "test_server.py",
            "simple_backend.py",
            "comprehensive_integration_test.py",
            "quick_status_check.py",
            "run_tests.py",
            "run_tests_stronger.py",
            
            # HTML and JS test files
            "microphone_test.html",
            "speech_to_text_test.html", 
            "test_push_to_talk.html",
            "test_plugin.js",
            "test_plugin_functionality.js",
            
            # Documentation that should be elsewhere
            "INTEGRATION_TEST_RESULTS.md",
            "MICROPHONE_FEATURE.md",
            "STATUS_INDICATOR_README.md",
            "TEST_STATUS.md",
            "TROUBLESHOOTING.md"
        ]
        
        removed_count = 0
        
        # Remove directories
        for dir_name in dirs_to_remove:
            dir_path = self.test_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                try:
                    shutil.rmtree(dir_path)
                    print(f"  {Colors.colorize('✅ Removed directory:', Colors.GREEN)} {dir_name}")
                    removed_count += 1
                except Exception as e:
                    print(f"  {Colors.colorize('⚠️ Could not remove directory:', Colors.YELLOW)} {dir_name} - {e}")
        
        # Remove files
        for file_path in files_to_remove:
            full_path = self.test_root / file_path
            if full_path.exists() and full_path.is_file():
                try:
                    full_path.unlink()
                    print(f"  {Colors.colorize('✅ Removed file:', Colors.GREEN)} {file_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"  {Colors.colorize('⚠️ Could not remove file:', Colors.YELLOW)} {file_path} - {e}")
        
        print(f"\n{Colors.colorize(f'🧹 Cleanup complete: {removed_count} items removed', Colors.BOLD + Colors.GREEN)}")
        print("=" * 60 + "\n")
        
    def discover_and_categorize_tests(self) -> List[TestFile]:
        """Discover all test files and categorize them."""
        print(f"{Colors.colorize('🔍 DISCOVERING AND CATEGORIZING TESTS', Colors.BOLD + Colors.CYAN)}")
        print("=" * 60)
        
        test_files = []
        
        # Define categories with priorities (lower = higher priority)
        categories = {
            "Core Backend": {"priority": 1, "patterns": ["backend/test_backend.py", "backend/test_settings.py"]},
            "Model Management": {"priority": 2, "patterns": ["backend/test_modelmanager*.py"]},
            "Embeddings & Search": {"priority": 3, "patterns": ["backend/test_embeddings*.py", "backend/test_indexing*.py"]},
            "Caching & Storage": {"priority": 4, "patterns": ["backend/test_caching*.py"]},
            "Security & Config": {"priority": 5, "patterns": ["backend/test_security.py", "backend/test_config*.py"]},
            "Voice & Audio": {"priority": 6, "patterns": ["backend/test_voice.py"]},
            "LLM Router": {"priority": 7, "patterns": ["backend/test_llm_router.py"]},
            "Plugin System": {"priority": 8, "patterns": ["plugin/test_*.py", "test_plugin_python.py"]},
            "Integration Tests": {"priority": 9, "patterns": ["integration/test_*.py"]},
            "Enterprise Tests": {"priority": 10, "patterns": ["integration/test_enterprise*.py"]},
            "Performance Tests": {"priority": 11, "patterns": ["test_performance.py"]},
            "Utility & Server": {"priority": 12, "patterns": ["test_server.py", "run_tests.py"]},
            "Final & Misc": {"priority": 13, "patterns": ["test_final.py"]}
        }
        
        # Discover all test files
        all_test_files = []
        for pattern in ["test_*.py", "*_test.py"]:
            all_test_files.extend(self.test_root.rglob(pattern))
        
        # Remove duplicates and __pycache__ files and test runners
        excluded_files = {
            "comprehensive_test_runner.py",
            "comprehensive_async_test_runner.py"
        }
        all_test_files = [f for f in set(all_test_files) 
            if "__pycache__" not in str(f) and f.name not in excluded_files]
        
        print(f"Found {len(all_test_files)} potential test files:")
        
        # Categorize files
        for test_file in all_test_files:
            rel_path = test_file.relative_to(self.test_root)
            category = "Uncategorized"
            priority = 99
            
            # Find matching category
            for cat_name, cat_info in categories.items():
                for pattern in cat_info["patterns"]:
                    if test_file.match(pattern) or str(rel_path).replace("\\", "/") == pattern:
                        category = cat_name
                        priority = cat_info["priority"]
                        break
                if category != "Uncategorized":
                    break
            
            # Get test functions
            test_functions = self.get_test_functions_from_file(test_file)
            estimated_duration = len(test_functions) * 0.5  # Rough estimate
            
            test_file_obj = TestFile(
                path=test_file,
                category=category,
                priority=priority,
                estimated_duration=estimated_duration,
                test_functions=test_functions
            )
            
            test_files.append(test_file_obj)
            
            print(f"  {Colors.colorize(f'[{category}]', Colors.BLUE)} {rel_path} "
                f"({len(test_functions)} tests, ~{estimated_duration:.1f}s)")
        
        # Sort by priority and estimated duration
        test_files.sort(key=lambda x: (x.priority, x.estimated_duration))
        
        print(f"\n{Colors.colorize(f'📊 Total: {len(test_files)} test files, {sum(len(tf.test_functions) for tf in test_files)} individual tests', Colors.BOLD + Colors.GREEN)}")
        print("=" * 60 + "\n")
        
        return test_files
        
    def get_test_functions_from_file(self, file_path: Path) -> List[str]:
        """Extract test function names from a file using improved class context tracking."""
        test_functions = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            current_class = None
            indent_stack = []
            
            for line in lines:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    continue
                    
                indent = len(line) - len(line.lstrip())
                
                # Track indentation to know when we exit a class
                while indent_stack and indent <= indent_stack[-1][1]:
                    indent_stack.pop()
                    if indent_stack:
                        current_class = indent_stack[-1][0] if isinstance(indent_stack[-1][0], str) and indent_stack[-1][0].startswith('Test') else None
                    else:
                        current_class = None
                
                # Find test classes
                class_match = re.match(r'class\s+(Test\w+)', stripped)
                if class_match:
                    current_class = class_match.group(1)
                    indent_stack.append((current_class, indent))
                    continue
                
                # Find test methods/functions
                test_match = re.match(r'(?:async\s+)?def\s+(test_\w+)', stripped)
                if test_match:
                    test_name = test_match.group(1)
                    if current_class:
                        test_functions.append(f"{current_class}::{test_name}")
                    else:
                        test_functions.append(test_name)
                        
        except Exception as e:
            # If we can't parse the file, just run the entire file
            print(f"Warning: Could not parse {file_path}: {e}")
            test_functions = ["*"]
        return list(set(test_functions)) if test_functions else [file_path.stem]
        
    def print_header(self, test_files: List[TestFile]):
        """Print the comprehensive test runner header."""
        total_functions = sum(len(tf.test_functions) for tf in test_files)
        total_estimated_time = sum(tf.estimated_duration for tf in test_files)
        print("\n" + "=" * 100)
        print(Colors.colorize("🧪 OBSIDIAN AI ASSISTANT - COMPREHENSIVE ASYNC TEST SUITE", Colors.BOLD + Colors.CYAN))
        print("=" * 100)
        print("🔧 Configuration:")
        print(f"   • Max Workers: {Colors.colorize(str(self.max_workers), Colors.GREEN)}")
        print(f"   • Test Files: {Colors.colorize(str(len(test_files)), Colors.GREEN)}")
        print(f"   • Total Tests: {Colors.colorize(str(total_functions), Colors.GREEN)}")
        print(f"   • Estimated Time: {Colors.colorize(f'{total_estimated_time:.1f}s', Colors.BLUE)}")
        print(f"   • Timestamp: {Colors.colorize(time.strftime('%Y-%m-%d %H:%M:%S'), Colors.BLUE)}")
        print("=" * 100 + "\n")
        
    def print_test_status(self, test_result: TestResult, total_tests: int):
        """Print individual test status with colors and timing."""
        
        # Color mapping for status
        status_colors = {
            TestStatus.PASSED: Colors.GREEN,
            TestStatus.FAILED: Colors.RED,
            TestStatus.ERROR: Colors.RED,
            TestStatus.SKIPPED: Colors.YELLOW,
            TestStatus.RUNNING: Colors.CYAN,
            TestStatus.PENDING: Colors.GRAY
        }
        
        # Status symbols
        status_symbols = {
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌", 
            TestStatus.ERROR: "💥",
            TestStatus.SKIPPED: "⏭️",
            TestStatus.RUNNING: "🔄",
            TestStatus.PENDING: "⏳"
        }
        
        # Format timing
        if test_result.duration > 0:
            if test_result.duration < 0.001:
                time_str = "<1ms"
            elif test_result.duration < 1:
                time_str = f"{test_result.duration*1000:.0f}ms"
            else:
                time_str = f"{test_result.duration:.2f}s"
        else:
            time_str = "---"
            
        # Format test counter
        counter_str = f"[{test_result.number:3d}/{total_tests:3d}]"
        
        # Format status with color
        status_color = status_colors.get(test_result.status, Colors.WHITE)
        symbol = status_symbols.get(test_result.status, "?")
        status_str = Colors.colorize(f"{symbol} {test_result.status.value}", status_color)
        
        # Format category
        category_str = Colors.colorize(f"[{test_result.category}]", Colors.DIM + Colors.BLUE)
        
        # Truncate test name if too long
        max_name_len = 40
        if len(test_result.name) > max_name_len:
            display_name = test_result.name[:max_name_len-3] + "..."
        else:
            display_name = test_result.name.ljust(max_name_len)
            
        # Worker ID
        worker_str = f"W{test_result.worker_id or '0'}" if test_result.worker_id else ""
        worker_colored = Colors.colorize(worker_str, Colors.DIM + Colors.MAGENTA) if worker_str else ""
        
        # Print formatted line with thread-safe output
        timestamp = time.strftime('%H:%M:%S')
        line = (f"[{timestamp}] {counter_str} {category_str:<20} {display_name} "
                f"{status_str} ({time_str}) {worker_colored}")
        
        with self.status_lock:
            print(line)
        
    async def run_test_file_async(self, test_file: TestFile, worker_id: str) -> List[TestResult]:
        """Run a single test file asynchronously."""
        results = []
        relative_path = test_file.path.relative_to(self.project_root)

        for test_func in test_file.test_functions:
            with self.lock:
                self.test_count += 1
                current_test_num = self.test_count

            # Create test result record
            test_result = TestResult(
                number=current_test_num,
                name=test_func,
                status=TestStatus.RUNNING,
                duration=0.0,
                file_path=str(relative_path),
                category=test_file.category,
                start_time=time.time(),
                worker_id=worker_id
            )

            # Show running status
            self.print_test_status(test_result, self.total_tests)

            start_time = time.time()

            try:
                # Prepare pytest command
                if test_func.endswith("::*") or "::" in test_func:
                    # Run entire class or specific test
                    if test_func.endswith("::*"):
                        cmd = ["python", "-m", "pytest", str(test_file.path), "-v", "--tb=short", "-q"]
                    else:
                        cmd = ["python", "-m", "pytest", f"{test_file.path}::{test_func}", "-v", "--tb=short", "-q"]
                else:
                    # Run specific test function
                    cmd = ["python", "-m", "pytest", f"{test_file.path}::{test_func}", "-v", "--tb=short", "-q"]

                # Run test in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    self._run_subprocess,
                    cmd
                )

                duration = time.time() - start_time

                # Determine status based on return code
                if result["returncode"] == 0:
                    status = TestStatus.PASSED
                    error_msg = None
                elif result["returncode"] == 5:  # No tests collected
                    status = TestStatus.SKIPPED
                    error_msg = "No tests collected"
                else:
                    status = TestStatus.FAILED
                    error_msg = result["stdout"] + result["stderr"]

            except asyncio.TimeoutError:
                duration = 60.0
                status = TestStatus.ERROR
                error_msg = "Test timeout (60s)"
            except Exception as e:
                duration = time.time() - start_time
                status = TestStatus.ERROR
                error_msg = str(e)

            # Update result
            test_result.status = status
            test_result.duration = duration
            test_result.end_time = time.time()
            test_result.error_message = error_msg

            results.append(test_result)

            with self.lock:
                self.results.append(test_result)

            # Update status display
            self.print_test_status(test_result, self.total_tests)

        return results
        
    def _run_subprocess(self, cmd: List[str]) -> Dict[str, str]:
        """Run subprocess and return results."""
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout per test
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": "Process timed out"
            }
        
    async def run_all_tests_async(self, test_files: List[TestFile]) -> Dict:
        """Run all tests asynchronously with worker management."""
        
        # Calculate total tests for progress tracking
        self.total_tests = sum(len(tf.test_functions) for tf in test_files)
        
        print(f"{Colors.colorize('🚀 STARTING ASYNC TEST EXECUTION', Colors.BOLD + Colors.GREEN)}")
        print(f"Running {len(test_files)} test files with {self.max_workers} workers...\n")
        
        # Create semaphore to limit concurrent file executions
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def run_with_semaphore(test_file: TestFile, worker_id: int):
            async with semaphore:
                return await self.run_test_file_async(test_file, f"{worker_id}")
        
        # Create tasks for all test files
        tasks = []
        for i, test_file in enumerate(test_files):
            task = asyncio.create_task(
                run_with_semaphore(test_file, i % self.max_workers + 1)
            )
            tasks.append(task)
            
        # Run all tasks concurrently
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except KeyboardInterrupt:
            print(f"\n{Colors.colorize('⚠️ Test execution interrupted by user', Colors.YELLOW)}")
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
                    
        return self.generate_summary_dict()
        
    def print_comprehensive_summary(self):
        """Print comprehensive test summary with detailed analytics."""
        total_duration = time.time() - self.start_time
        
        # Count results by status and category
        status_counts = {
            TestStatus.PASSED: 0,
            TestStatus.FAILED: 0,
            TestStatus.ERROR: 0,
            TestStatus.SKIPPED: 0
        }
        
        category_stats = {}
        total_test_time = 0.0
        
        for result in self.results:
            status_counts[result.status] += 1
            total_test_time += result.duration
            
            if result.category not in category_stats:
                category_stats[result.category] = {
                    "passed": 0, "failed": 0, "error": 0, "skipped": 0, "total_time": 0.0
                }
            
            category_stats[result.category][result.status.value.lower()] += 1
            category_stats[result.category]["total_time"] += result.duration
            
        print("\n" + "=" * 100)
        print(Colors.colorize("📊 COMPREHENSIVE ASYNC TEST SUMMARY", Colors.BOLD + Colors.CYAN))
        print("=" * 100)
        
        # Overall statistics
        total_tests = len(self.results)
        pass_rate = (status_counts[TestStatus.PASSED] / total_tests * 100) if total_tests > 0 else 0
        
        print(f"🕐 Total Execution Time: {Colors.colorize(f'{total_duration:.2f}s', Colors.BLUE)}")
        print(f"⚡ Total Test Time: {Colors.colorize(f'{total_test_time:.2f}s', Colors.BLUE)}")
        print(f"🚀 Speedup Factor: {Colors.colorize(f'{total_test_time/total_duration:.1f}x', Colors.GREEN)}")
        print(f"🧪 Total Tests: {Colors.colorize(str(total_tests), Colors.BOLD)}")
        print(f"👥 Workers Used: {Colors.colorize(str(self.max_workers), Colors.MAGENTA)}")
        print(f"📈 Pass Rate: {Colors.colorize(f'{pass_rate:.1f}%', Colors.GREEN if pass_rate >= 90 else Colors.YELLOW)}")
        
        print("\n📋 Overall Results:")
        print(f"  ✅ Passed:  {Colors.colorize(str(status_counts[TestStatus.PASSED]), Colors.GREEN)}")
        print(f"  ❌ Failed:  {Colors.colorize(str(status_counts[TestStatus.FAILED]), Colors.RED)}")
        print(f"  💥 Errors:  {Colors.colorize(str(status_counts[TestStatus.ERROR]), Colors.RED)}")
        print(f"  ⏭️ Skipped: {Colors.colorize(str(status_counts[TestStatus.SKIPPED]), Colors.YELLOW)}")

        # Category breakdown
        print("\n📂 Results by Category:")
        for category, stats in sorted(category_stats.items()):
            total_cat = sum(v for k, v in stats.items() if k != "total_time")
            if total_cat > 0:
                cat_pass_rate = (stats.get("passed", 0) / total_cat * 100)
                status_color = Colors.GREEN if cat_pass_rate >= 90 else Colors.YELLOW if cat_pass_rate >= 70 else Colors.RED
                print(f"  📁 {category:<20} {Colors.colorize(f'{cat_pass_rate:5.1f}%', status_color)} "
                    f"({stats.get('passed', 0)}/{total_cat}) {stats['total_time']:.2f}s")

        # Performance insights
        if self.results:
            slowest_tests = sorted(self.results, key=lambda x: x.duration, reverse=True)[:10]
            print("\n⏱️ Slowest Tests (Top 10):")
            for i, result in enumerate(slowest_tests, 1):
                duration_color = Colors.RED if result.duration > 5 else Colors.YELLOW if result.duration > 2 else Colors.GREEN
                print(f"  {i:2d}. {result.name:<35} {Colors.colorize(f'{result.duration:.3f}s', duration_color)} [{result.category}]")

            # Fastest tests
            fastest_tests = sorted([r for r in self.results if r.status == TestStatus.PASSED], 
                key=lambda x: x.duration)[:5]
            if fastest_tests:
                print("\n⚡ Fastest Tests (Top 5):")
                for i, result in enumerate(fastest_tests, 1):
                    print(f"  {i}. {result.name:<35} {Colors.colorize(f'{result.duration:.3f}s', Colors.GREEN)} [{result.category}]")

        # Show failed tests if any
        failed_tests = [r for r in self.results if r.status in [TestStatus.FAILED, TestStatus.ERROR]]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for result in failed_tests[:10]:  # Show max 10 failures
                print(f"  {result.number:3d}. {result.name} ({result.category})")
                if result.error_message and len(result.error_message) < 200:
                    error_preview = result.error_message.strip().replace('\n', ' ')[:150]
                    print(f"       {Colors.colorize(error_preview + '...', Colors.DIM + Colors.RED)}")
                    
        print("=" * 100)
        
        # Final status
        if status_counts[TestStatus.FAILED] == 0 and status_counts[TestStatus.ERROR] == 0:
            print(Colors.colorize("🎉 ALL TESTS PASSED! EXCELLENT WORK! 🎉", Colors.BOLD + Colors.GREEN))
        elif pass_rate >= 90:
            print(Colors.colorize("🌟 GREAT SUCCESS - 90%+ PASS RATE! 🌟", Colors.BOLD + Colors.YELLOW))
        else:
            print(Colors.colorize("💥 SOME TESTS FAILED - NEEDS ATTENTION", Colors.BOLD + Colors.RED))
            
        print("=" * 100 + "\n")
        
    def generate_summary_dict(self) -> Dict:
        """Generate detailed summary data as dictionary."""
        status_counts = {
            TestStatus.PASSED: 0,
            TestStatus.FAILED: 0, 
            TestStatus.ERROR: 0,
            TestStatus.SKIPPED: 0
        }
        
        category_stats = {}
        
        for result in self.results:
            status_counts[result.status] += 1
            
            if result.category not in category_stats:
                category_stats[result.category] = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
            category_stats[result.category][result.status.value.lower()] += 1
            
        return {
            "execution_mode": "async",
            "max_workers": self.max_workers,
            "total_tests": len(self.results),
            "passed": status_counts[TestStatus.PASSED],
            "failed": status_counts[TestStatus.FAILED],
            "errors": status_counts[TestStatus.ERROR],
            "skipped": status_counts[TestStatus.SKIPPED],
            "pass_rate": (status_counts[TestStatus.PASSED] / len(self.results) * 100) if self.results else 0,
            "total_duration": time.time() - self.start_time,
            "total_test_time": sum(r.duration for r in self.results),
            "speedup_factor": sum(r.duration for r in self.results) / (time.time() - self.start_time),
            "category_stats": category_stats,
            "results": [
                {
                    "number": r.number,
                    "name": r.name,
                    "status": r.status.value,
                    "duration": r.duration,
                    "file_path": r.file_path,
                    "category": r.category,
                    "worker_id": r.worker_id,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }


async def main():
    """Main async entry point."""
    print(Colors.colorize("🚀 INITIALIZING COMPREHENSIVE ASYNC TEST RUNNER", Colors.BOLD + Colors.CYAN))
    print(Colors.colorize("=" * 70, Colors.CYAN))
    
    # Initialize runner with optimal worker count
    max_workers = min(8, (os.cpu_count() or 4) + 1)
    runner = AsyncTestRunner(max_workers=max_workers)
    
    try:
        # Step 1: Cleanup redundant files and directories
        runner.cleanup_test_directories()
        
        # Step 2: Discover and categorize all test files
        test_files = runner.discover_and_categorize_tests()
        
        if not test_files:
            print(Colors.colorize("⚠️ No test files found!", Colors.YELLOW))
            return
            
        # Step 3: Print header with summary
        runner.print_header(test_files)
        
        # Step 4: Run all tests asynchronously
        summary = await runner.run_all_tests_async(test_files)
        
        # Step 5: Print comprehensive summary
        runner.print_comprehensive_summary()
        
        # Step 6: Save detailed results
        results_file = runner.test_root / "comprehensive_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
            
        print(f"📄 Detailed results saved to: {Colors.colorize(str(results_file), Colors.BLUE)}")
        
        # Return appropriate exit code
        if summary["failed"] > 0 or summary["errors"] > 0:
            return 1
        else:
            return 0
            
    except KeyboardInterrupt:
        print(f"\n{Colors.colorize('🛑 Test execution interrupted by user', Colors.YELLOW)}")
        return 130
    except Exception as e:
        print(f"\n{Colors.colorize(f'💥 Unexpected error: {e}', Colors.RED)}")
        return 1
    finally:
        # Cleanup executor
        runner.executor.shutdown(wait=True)


if __name__ == "__main__":
    # Run async main function
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Colors.colorize('🛑 Execution interrupted', Colors.YELLOW)}")
        sys.exit(130)