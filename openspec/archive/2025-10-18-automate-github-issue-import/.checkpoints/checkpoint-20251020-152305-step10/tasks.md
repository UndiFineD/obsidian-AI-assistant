# Tasks: Automate GitHub Issue Import to OpenSpec

## 1. CLI Design
- [ ] Choose approach: new script vs extend `openspec_new_change.py`
- [ ] Define flags: `--issue`, `--owner`, `--id`, `--base-dir`, `--dry-run`, `--force`

## 2. GitHub Fetch
- [ ] Parse URL or number
- [ ] Call GitHub API (use `GITHUB_TOKEN` if available)
- [ ] Extract: title, body, labels, author, link

## 3. Scaffolding
- [ ] Build change-id from date + slug of issue title
- [ ] Create directory and files
- [ ] Populate proposal.md with issue data and link
- [ ] Replace placeholders in todo.md (owner/date/id)

## 4. Tests
- [ ] Unit tests for parser and id generation
- [ ] Unit tests for file creation (tmp dir)
- [ ] Mock GitHub calls

## 5. Docs
- [ ] Add usage to `docs/OPEN_SPEC_TOOLS.md`
- [ ] Add mention in `openspec/PROJECT_WORKFLOW.md`

## 6. Plumbing
- [ ] Pre-commit integration (optional)
- [ ] CI smoke check for the script
