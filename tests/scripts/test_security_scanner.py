import subprocess


def test_security_scanner_script():
    result = subprocess.run(
        ["python", "scripts/security_scanner.py"], capture_output=True
    )
    assert result.returncode == 0
