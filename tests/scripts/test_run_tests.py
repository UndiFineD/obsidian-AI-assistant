import subprocess


def test_run_tests_script():
    result = subprocess.run(["python", "scripts/run_tests.py"], capture_output=True)
    assert result.returncode == 0
