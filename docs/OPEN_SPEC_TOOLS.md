# OpenSpec Tools

This project includes a small helper CLI to scaffold new OpenSpec change directories.

## Scaffold a New Change

- Preview actions (no files created):

```bash
python scripts/openspec_new_change.py "My New Change" --dry-run
```

- Create with defaults (change-id will be `YYYY-MM-DD-my-new-change`):

```bash
python scripts/openspec_new_change.py "My New Change" --owner @yourhandle
```

- Create with explicit id:

```bash
python scripts/openspec_new_change.py --id 2025-10-18-my-new-change --title "My New Change"
```

## Outputs

The tool creates the structure:

```
openspec/
  changes/
    <change-id>/
      todo.md        # from template with placeholders filled
      proposal.md
      spec.md
      tasks.md
      test_plan.md
```

## Notes

- Use `--force` to overwrite an existing directory
- Use `--base-dir` if you're running from a different working directory
- The `todo.md` template lives in `openspec/templates/todo.md`
