#!/usr/bin/env python3
"""Progress Indicators Module

Provides visual feedback for long-running operations with spinners,
progress bars, and status updates.
"""

import sys
import time
import threading
from typing import Optional, Callable
from contextlib import contextmanager

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    import codecs
    # Only wrap if not already wrapped
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


class Spinner:
    """Animated spinner for indeterminate operations."""
    
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    
    def __init__(self, message: str = "Processing", color: str = "cyan"):
        """Initialize spinner.
        
        Args:
            message: Message to display alongside spinner
            color: Color code (cyan, green, yellow, red)
        """
        self.message = message
        self.color = color
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._frame_index = 0
        
        # ANSI color codes
        self._colors = {
            "cyan": "\033[36m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "red": "\033[31m",
            "reset": "\033[0m",
        }
    
    def _animate(self):
        """Animation loop running in background thread."""
        while self._running:
            frame = self.FRAMES[self._frame_index % len(self.FRAMES)]
            color_code = self._colors.get(self.color, "")
            reset_code = self._colors["reset"]
            
            # Write spinner frame
            sys.stdout.write(
                f"\r{color_code}{frame}{reset_code} {self.message}..."
            )
            sys.stdout.flush()
            
            self._frame_index += 1
            time.sleep(0.08)  # ~12 fps
    
    def start(self):
        """Start the spinner animation."""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._animate, daemon=True)
            self._thread.start()
    
    def stop(self, final_message: Optional[str] = None, status: str = "success"):
        """Stop the spinner animation.
        
        Args:
            final_message: Optional message to display after stopping
            status: Status indicator (success, fail, info)
        """
        if self._running:
            self._running = False
            if self._thread:
                self._thread.join()
            
            # Clear spinner line
            sys.stdout.write("\r" + " " * (len(self.message) + 20) + "\r")
            
            # Display final message if provided
            if final_message:
                status_icons = {
                    "success": "✓",
                    "fail": "✗",
                    "info": "ℹ",
                }
                status_colors = {
                    "success": "green",
                    "fail": "red",
                    "info": "cyan",
                }
                
                icon = status_icons.get(status, "•")
                color = self._colors.get(status_colors.get(status, "cyan"), "")
                reset = self._colors["reset"]
                
                sys.stdout.write(f"{color}{icon}{reset} {final_message}\n")
            
            sys.stdout.flush()


class ProgressBar:
    """Progress bar for operations with known total."""
    
    def __init__(
        self,
        total: int,
        message: str = "Progress",
        width: int = 40,
        show_percentage: bool = True,
        show_count: bool = True,
    ):
        """Initialize progress bar.
        
        Args:
            total: Total number of items to process
            message: Message to display
            width: Width of progress bar in characters
            show_percentage: Show percentage completion
            show_count: Show current/total count
        """
        self.total = total
        self.message = message
        self.width = width
        self.show_percentage = show_percentage
        self.show_count = show_count
        self.current = 0
        
        # ANSI color codes
        self._green = "\033[32m"
        self._cyan = "\033[36m"
        self._reset = "\033[0m"
    
    def update(self, increment: int = 1, item_name: Optional[str] = None):
        """Update progress bar.
        
        Args:
            increment: Number to increment current by
            item_name: Optional name of current item being processed
        """
        self.current = min(self.current + increment, self.total)
        self._render(item_name)
    
    def set(self, value: int, item_name: Optional[str] = None):
        """Set progress to specific value.
        
        Args:
            value: Absolute value to set progress to
            item_name: Optional name of current item being processed
        """
        self.current = min(value, self.total)
        self._render(item_name)
    
    def _render(self, item_name: Optional[str] = None):
        """Render the progress bar."""
        if self.total == 0:
            percentage = 100.0
        else:
            percentage = (self.current / self.total) * 100
        
        filled = int((self.current / self.total) * self.width) if self.total > 0 else 0
        bar = "█" * filled + "░" * (self.width - filled)
        
        # Build progress line
        parts = [f"\r{self._cyan}{self.message}{self._reset}: "]
        parts.append(f"[{self._green}{bar}{self._reset}]")
        
        if self.show_percentage:
            parts.append(f" {percentage:5.1f}%")
        
        if self.show_count:
            parts.append(f" ({self.current}/{self.total})")
        
        if item_name:
            parts.append(f" - {item_name}")
        
        sys.stdout.write("".join(parts))
        sys.stdout.flush()
    
    def complete(self, final_message: Optional[str] = None):
        """Mark progress as complete.
        
        Args:
            final_message: Optional final message to display
        """
        self.current = self.total
        self._render()
        
        if final_message:
            sys.stdout.write(f"\n✓ {final_message}\n")
        else:
            sys.stdout.write("\n")
        
        sys.stdout.flush()


class WorkflowProgress:
    """Nested progress display showing overall workflow and current step progress.
    
    Displays two levels of progress:
    1. Overall workflow progress (which steps are complete)
    2. Current step progress (what's happening in the current step)
    """
    
    def __init__(self, total_steps: int, workflow_name: str = "Workflow"):
        """Initialize workflow progress tracker.
        
        Args:
            total_steps: Total number of steps in the workflow
            workflow_name: Name of the workflow
        """
        self.total_steps = total_steps
        self.workflow_name = workflow_name
        self.current_step = 0
        self.current_step_name = ""
        self.step_progress: Optional[str] = None
        self._lock = threading.Lock()
        
        # ANSI codes
        self._cyan = "\033[36m"
        self._green = "\033[32m"
        self._yellow = "\033[33m"
        self._reset = "\033[0m"
        self._clear_line = "\033[2K"
        self._move_up = "\033[1A"
    
    def start_step(self, step_number: int, step_name: str):
        """Start a new workflow step.
        
        Args:
            step_number: Step number (1-based)
            step_name: Name of the step
        """
        with self._lock:
            self.current_step = step_number
            self.current_step_name = step_name
            self.step_progress = None
            self._render()
    
    def update_step_progress(self, progress_text: str):
        """Update the current step's progress text.
        
        Args:
            progress_text: Progress text to display for current step
        """
        with self._lock:
            self.step_progress = progress_text
            self._render()
    
    def complete_step(self):
        """Mark current step as complete."""
        with self._lock:
            self.step_progress = None
            self._render()
    
    def _render(self):
        """Render the nested progress display."""
        # Clear previous display if not first render
        if hasattr(self, '_displayed'):
            # Move up and clear 2 lines
            sys.stdout.write(f"{self._move_up}{self._clear_line}")
            sys.stdout.write(f"{self._move_up}{self._clear_line}")
        
        self._displayed = True
        
        # Overall progress bar
        if self.total_steps > 0:
            percentage = (self.current_step / self.total_steps) * 100
            filled = int((self.current_step / self.total_steps) * 30)
        else:
            percentage = 0
            filled = 0
        
        bar = "█" * filled + "░" * (30 - filled)
        
        overall_line = (
            f"{self._cyan}{self.workflow_name}{self._reset}: "
            f"[{self._green}{bar}{self._reset}] "
            f"{percentage:5.1f}% ({self.current_step}/{self.total_steps})"
        )
        
        # Current step line
        if self.current_step > 0 and self.current_step_name:
            step_icon = "◐" if self.step_progress else "○"
            step_line = (
                f"  {self._yellow}{step_icon}{self._reset} "
                f"Step {self.current_step}: {self.current_step_name}"
            )
            
            if self.step_progress:
                step_line += f" - {self.step_progress}"
        else:
            step_line = "  (waiting...)"
        
        # Write both lines
        sys.stdout.write(f"{overall_line}\n")
        sys.stdout.write(f"{step_line}\n")
        sys.stdout.flush()
    
    def finish(self, message: str = "Complete"):
        """Finish workflow progress display.
        
        Args:
            message: Final message to display
        """
        with self._lock:
            # Clear the two-line display
            if hasattr(self, '_displayed'):
                sys.stdout.write(f"{self._move_up}{self._clear_line}")
                sys.stdout.write(f"{self._move_up}{self._clear_line}")
            
            # Show completion
            sys.stdout.write(
                f"{self._green}✓{self._reset} {self.workflow_name}: {message}\n"
            )
            sys.stdout.flush()


class StatusTracker:
    """Track and display status of multiple concurrent operations."""
    
    def __init__(self, title: str = "Processing"):
        """Initialize status tracker.
        
        Args:
            title: Title for the status display
        """
        self.title = title
        self.items = {}  # item_id -> {name, status, message}
        self._lock = threading.Lock()
        
        # ANSI codes
        self._colors = {
            "pending": "\033[33m",  # Yellow
            "running": "\033[36m",  # Cyan
            "success": "\033[32m",  # Green
            "failed": "\033[31m",   # Red
            "reset": "\033[0m",
        }
        self._status_icons = {
            "pending": "○",
            "running": "◐",
            "success": "✓",
            "failed": "✗",
        }
    
    def add_item(self, item_id: str, name: str, status: str = "pending"):
        """Add an item to track.
        
        Args:
            item_id: Unique identifier for the item
            name: Display name
            status: Initial status (pending, running, success, failed)
        """
        with self._lock:
            self.items[item_id] = {
                "name": name,
                "status": status,
                "message": "",
            }
            self._render()
    
    def update_item(
        self,
        item_id: str,
        status: Optional[str] = None,
        message: Optional[str] = None
    ):
        """Update an item's status.
        
        Args:
            item_id: Item identifier
            status: New status (pending, running, success, failed)
            message: Optional status message
        """
        with self._lock:
            if item_id in self.items:
                if status:
                    self.items[item_id]["status"] = status
                if message is not None:
                    self.items[item_id]["message"] = message
                self._render()
    
    def _render(self):
        """Render the status display."""
        # Move cursor to start and clear lines
        sys.stdout.write("\033[2K\r")  # Clear line
        
        lines = [f"\n{self.title}:"]
        
        for item_id, item in self.items.items():
            color = self._colors.get(item["status"], "")
            icon = self._status_icons.get(item["status"], "•")
            reset = self._colors["reset"]
            
            line = f"  {color}{icon}{reset} {item['name']}"
            if item["message"]:
                line += f" - {item['message']}"
            lines.append(line)
        
        sys.stdout.write("\n".join(lines))
        sys.stdout.write("\n")
        sys.stdout.flush()
    
    def complete(self, summary: Optional[str] = None):
        """Mark all items as complete and show summary.
        
        Args:
            summary: Optional summary message
        """
        if summary:
            sys.stdout.write(f"\n{summary}\n")
            sys.stdout.flush()


@contextmanager
def spinner(message: str = "Processing", success_msg: Optional[str] = None):
    """Context manager for spinner.
    
    Args:
        message: Message to display
        success_msg: Message to display on success
        
    Yields:
        Spinner instance
        
    Example:
        with spinner("Loading files", "Files loaded"):
            # Do work
            pass
    """
    s = Spinner(message)
    s.start()
    try:
        yield s
        s.stop(success_msg or f"{message} complete", "success")
    except Exception as e:
        s.stop(f"{message} failed: {e}", "fail")
        raise


@contextmanager
def progress_bar(
    total: int,
    message: str = "Progress",
    complete_msg: Optional[str] = None
):
    """Context manager for progress bar.
    
    Args:
        total: Total number of items
        message: Message to display
        complete_msg: Message to display on completion
        
    Yields:
        ProgressBar instance
        
    Example:
        with progress_bar(100, "Processing files") as bar:
            for i in range(100):
                # Do work
                bar.update(1, f"file_{i}.txt")
    """
    pb = ProgressBar(total, message)
    try:
        yield pb
        pb.complete(complete_msg or f"{message} complete")
    except Exception as e:
        sys.stdout.write(f"\n✗ {message} failed: {e}\n")
        raise


@contextmanager
def workflow_progress(total_steps: int, workflow_name: str = "Workflow"):
    """Context manager for nested workflow progress.
    
    Args:
        total_steps: Total number of steps in workflow
        workflow_name: Name of the workflow
        
    Yields:
        WorkflowProgress instance
        
    Example:
        with workflow_progress(5, "Build Pipeline") as wp:
            wp.start_step(1, "Compile")
            wp.update_step_progress("Compiling source files...")
            # Do work
            wp.complete_step()
            
            wp.start_step(2, "Test")
            wp.update_step_progress("Running tests...")
            # Do work
            wp.complete_step()
    """
    wp = WorkflowProgress(total_steps, workflow_name)
    try:
        yield wp
        wp.finish("Complete")
    except Exception as e:
        wp.finish(f"Failed: {e}")
        raise


def demo():
    """Demonstration of progress indicators."""
    print("=" * 60)
    print("Progress Indicators Demo")
    print("=" * 60)
    print()
    
    # Demo 1: Spinner
    print("1. Spinner (indeterminate operation)")
    with spinner("Loading configuration", "Configuration loaded"):
        time.sleep(2)
    print()
    
    # Demo 2: Progress Bar
    print("2. Progress Bar (known total)")
    with progress_bar(10, "Processing files", "All files processed") as bar:
        for i in range(10):
            time.sleep(0.3)
            bar.update(1, f"file_{i:02d}.txt")
    print()
    
    # Demo 3: Status Tracker
    print("3. Status Tracker (concurrent operations)")
    tracker = StatusTracker("Building components")
    
    tracker.add_item("backend", "Backend API", "pending")
    tracker.add_item("frontend", "Frontend UI", "pending")
    tracker.add_item("database", "Database schema", "pending")
    
    time.sleep(0.5)
    tracker.update_item("backend", "running", "Compiling...")
    time.sleep(1)
    tracker.update_item("backend", "success", "Build complete")
    
    tracker.update_item("frontend", "running", "Bundling...")
    time.sleep(1)
    tracker.update_item("frontend", "success", "Bundle complete")
    
    tracker.update_item("database", "running", "Migrating...")
    time.sleep(1)
    tracker.update_item("database", "success", "Migration complete")
    
    tracker.complete("✓ All components built successfully")
    print()
    
    # Demo 4: Nested Workflow Progress
    print("4. Nested Workflow Progress (overall + step progress)")
    with workflow_progress(3, "Deployment Pipeline") as wp:
        # Step 1
        wp.start_step(1, "Build")
        time.sleep(0.5)
        wp.update_step_progress("Compiling...")
        time.sleep(1)
        wp.update_step_progress("Linking...")
        time.sleep(1)
        wp.complete_step()
        
        # Step 2
        wp.start_step(2, "Test")
        time.sleep(0.5)
        wp.update_step_progress("Running unit tests...")
        time.sleep(1)
        wp.update_step_progress("Running integration tests...")
        time.sleep(1)
        wp.complete_step()
        
        # Step 3
        wp.start_step(3, "Deploy")
        time.sleep(0.5)
        wp.update_step_progress("Uploading artifacts...")
        time.sleep(1)
        wp.update_step_progress("Configuring services...")
        time.sleep(1)
        wp.complete_step()
    print()


if __name__ == "__main__":
    demo()
