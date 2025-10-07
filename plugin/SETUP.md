# Obsidian AI Assistant Plugin Setup Guide

## 1. Prerequisites
- Obsidian v1.0+ (Desktop)
- Node.js (for building, if needed)
- Backend server running (default: http://localhost:8000)

## 2. Plugin Files
Ensure the following files are present in your plugin folder:
- `main.js` (entry point)
- `rightPane.js` (right pane UI)
- `styles.css` (plugin styles)
- `taskQueue.js`, `taskQueueView.js` (task queue logic/UI)
- `voiceInput.js`, `voice.js` (voice features)
- `analyticsPane.js` (analytics dashboard)
- `manifest.json` (plugin manifest)

## 3. Installation Steps
1. Copy the entire `plugin/` folder into your Obsidian vault's plugins directory:
   - Windows: `%APPDATA%\Obsidian\plugins\obsidian-AI-assistant`
   - macOS/Linux: `~/.config/Obsidian/plugins/obsidian-AI-assistant`
2. Open Obsidian, go to **Settings > Community Plugins > Installed Plugins**.
3. Enable **Developer Mode** (if not already enabled).
4. Click **Reload Plugins** or restart Obsidian.
5. Enable the **Obsidian AI Assistant** plugin.

## 4. Configuration
- Click the AI Assistant ribbon icon to open the right pane UI.
- Set the backend server URL in the plugin settings or right pane config section.
- (Optional) Adjust voice and network features in settings.

## 5. Usage
- Use the right pane to:
  - Check backend status and reload
  - Login to backend (if required)
  - Ask questions via text or voice
  - View analytics and task queue
  - Configure backend server/port

## 6. Troubleshooting
- If the pane does not appear, check for errors in the Obsidian console (Ctrl+Shift+I).
- Ensure all required files are present and up-to-date.
- Verify backend server is running and accessible.
- For advanced issues, consult plugin logs or backend logs.

## 7. Uninstalling
- Disable the plugin in Obsidian settings.
- Delete the plugin folder from your vault's plugins directory.

---
For advanced configuration, backend integration, or feature requests, see the project README or contact the maintainer.