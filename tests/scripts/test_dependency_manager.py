import subprocess
import tempfile
from pathlib import Path


def test_dependency_manager_merge_and_deduplication():
    """
    Test that dependency_manager.py merges and deduplicates requirements files correctly.
    """
    # Create temporary requirements files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        (tmpdir_path / "requirements.txt").write_text(
            "requests==2.31.0\nflask==2.0.0\n"
        )
        (tmpdir_path / "requirements-dev.txt").write_text(
            "requests>=2.0.0\npytest==7.4.0\n"
        )
        (tmpdir_path / "requirements-test.txt").write_text(
            "pytest==7.4.0\nflask>=2.0.0\n"
        )

        # Run dependency_manager.py in summary mode
        result = subprocess.run(
            [
                "python",
                "scripts/dependency_manager.py",
                "--project-root",
                str(tmpdir_path),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
        )
        # Accept nonzero exit code if conflicts are detected
        # Read the generated dependency-report.json file
        import json

        report_path = tmpdir_path / "dependency-report.json"
        assert report_path.exists(), f"Report file not found: {report_path}"
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
        deps = report["dependencies"]
        # Should deduplicate and show all three packages in the report
        assert "requests" in deps and "flask" in deps and "pytest" in deps, deps
        assert len(deps) == 3, deps
        # Should report at least one conflict (requests, flask, or pytest)
        assert len(report["conflicts"]) >= 1, report["conflicts"]
