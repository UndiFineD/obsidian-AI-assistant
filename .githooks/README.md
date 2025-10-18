# Local Git Hooks

This repository includes a PowerShell pre-commit hook to validate OpenSpec TODO markdown files.

Enable it locally:

```powershell
# From the repository root
git config core.hooksPath .githooks
# Make sure scripts are allowed to run (if needed)
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

What it does:
- Scans staged `openspec/changes/*/todo.md` and `openspec/templates/todo.md`
- Checks for required heading and checklist
- Fails on trailing whitespace

You can also run the Python checker manually:

```powershell
python scripts/check_markdown_todos.py
```
