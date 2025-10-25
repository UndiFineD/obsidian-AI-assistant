import subprocess


def test_code_quality_improvements_script():
    result = subprocess.run(
        ["python", "scripts/code_quality_improvements.py"], capture_output=True
    )
    assert result.returncode == 0
