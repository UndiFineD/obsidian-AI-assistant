"""
Automated Dependency Audit Script
Runs Safety (Python) and npm audit (JavaScript), logs results for weekly review.
"""
import subprocess
import sys
import os
from datetime import datetime

def run_safety():
    print("[Audit] Running Safety (Python)...")
    result = subprocess.run([
        sys.executable, "-m", "safety", "check", "--full-report", "--file", "../requirements.txt"
    ], capture_output=True, text=True)
    return result.stdout

def run_npm_audit():
    print("[Audit] Running npm audit (JavaScript)...")
    result = subprocess.run([
        "npm", "audit", "--json"
    ], capture_output=True, text=True)
    return result.stdout

def main():
    timestamp = datetime.utcnow().isoformat()
    log_path = os.path.abspath("../logs/dependency_audit.log")
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n=== Dependency Audit {timestamp} ===\n")
        log.write("\n--- Safety (Python) ---\n")
        log.write(run_safety())
        log.write("\n--- npm audit (JavaScript) ---\n")
        log.write(run_npm_audit())
        log.write("\n=== End Audit ===\n")
    print(f"[Audit] Results logged to {log_path}")

if __name__ == "__main__":
    main()
