# Obsidian AI Agent Plugin Setup

## Installation

1. Copy all plugin files to `.obsidian/plugins/obsidian-ai-agent/` in your Obsidian vault.

2. Ensure `manifest.json` is present and correct.

3. Restart Obsidian to load the plugin.

## Development

- All plugin code is now in `.obsidian/plugins/obsidian-ai-agent/`.

- Use explicit relative paths for all `require()` statements.

- Update code references to avoid using the old `plugin/` folder.

## Migration Notes

- All files from `plugin/` have been moved here.

- Remove any placeholder or duplicate files.

- Validate plugin loading in Obsidian after migration.

