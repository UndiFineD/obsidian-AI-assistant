import subprocess

def test_fix_dependencies_script():
    result = subprocess.run(['python', 'scripts/fix_dependencies.py'], capture_output=True)
    assert result.returncode == 0
