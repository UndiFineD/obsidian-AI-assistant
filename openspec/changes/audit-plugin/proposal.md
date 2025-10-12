
# Proposal: Add Plugin Module Audit to OpenSpec

**Target Document:** `project.md`

**Change:** Incorporate the plugin module audit findings into the project's OpenSpec.

**Rationale:** The plugin audit provides a comprehensive overview of the plugin's architecture, key modules, and testing priorities. Adding this to the OpenSpec will improve project clarity, guide development efforts, and ensure that all team members are aligned on the plugin's structure and priorities.

**Content to Add:**

```markdown
# Plugin Module Audit

**Date**: October 11, 2025  
**Task**: T002 - Audit plugin modules in `.obsidian/plugins/obsidian-ai-assistant/` and list all major files/classes/functions

---

## Plugin Directory Structure

```text
.obsidian/plugins/obsidian-ai-assistant/
├── adminDashboard.js         # Enterprise admin dashboard
├── analyticsPane.js          # Analytics display component
├── backendClient.js          # Backend API client
├── config.template.json      # Configuration template
├── enterpriseAuth.js         # Enterprise authentication
├── enterpriseConfig.js       # Enterprise configuration
├── main.js                   # Main plugin entry point
├── main_new.js              # New plugin implementation
├── main_old.js              # Legacy plugin implementation
├── manifest.json            # Obsidian plugin manifest
├── rightPane.js             # Right pane UI component
├── SETUP.md                 # Setup documentation
├── styles.css               # Plugin styles
├── styles_new.css           # New styles
├── styles_old.css           # Legacy styles
├── taskQueue.js             # Task queue management
├── taskQueueView.js         # Task queue UI component
├── voice.js                 # Voice recording functionality
└── voiceInput.js            # Voice input processing
```

## Core Plugin Modules (Priority for Testing)

### 1. main.js - Main Plugin Entry Point

**Classes/Functions to Test:**

- ObsidianAIAssistant class (main plugin class)
- onload() - Plugin initialization
- onunload() - Plugin cleanup
- loadSettings() - Settings loading
- saveSettings() - Settings persistence
- Command registration
- UI component initialization
- Event handlers
- Error handling

### 2. backendClient.js - Backend API Client

**Classes/Functions to Test:**

- BackendClient class
- HTTP request methods (GET, POST, PUT, DELETE)
- Authentication handling
- Request/response processing
- Error handling and retries
- Timeout management
- Connection pooling
- URL construction
- Header management

### 3. rightPane.js - Right Pane UI Component

**Classes/Functions to Test:**

- AIRightPaneView class
- UI rendering methods
- Event handlers
- Backend status display
- Login/logout functionality
- Configuration management
- Voice input integration
- Analytics display
- Task queue display
- Error handling

### 4. taskQueue.js - Task Queue Management

**Classes/Functions to Test:**

- TaskQueue class
- Task creation and management
- Queue processing
- Priority handling
- Task status tracking
- Persistence
- Error recovery
- Queue operations (start, pause, clear)

### 5. taskQueueView.js - Task Queue UI Component

**Classes/Functions to Test:**

- TaskQueueView class
- Task list rendering
- Task status updates
- User interactions
- Queue controls
- Progress indicators
- Error display

### 6. voice.js - Voice Recording Functionality

**Classes/Functions to Test:**

- VoiceRecorder class
- Audio recording
- Recording start/stop
- Audio format handling
- Backend communication
- Error handling
- Browser compatibility
- Permission handling

### 7. voiceInput.js - Voice Input Processing

**Classes/Functions to Test:**

- VoiceInput class
- Voice command processing
- Speech recognition
- Input validation
- Command routing
- Error handling

### 8. analyticsPane.js - Analytics Display Component

**Classes/Functions to Test:**

- Analytics data processing
- Chart rendering
- Data visualization
- Real-time updates
- Performance metrics
- User interaction tracking

## Enterprise Modules (Secondary Priority)

### 9. enterpriseAuth.js - Enterprise Authentication

**Classes/Functions to Test:**

- SSO integration
- Authentication flows
- Token management
- Session handling
- User roles
- Permission checks

### 10. enterpriseConfig.js - Enterprise Configuration

**Classes/Functions to Test:**

- Enterprise settings management
- Configuration validation
- Multi-tenant support
- Feature toggles
- Compliance settings

### 11. adminDashboard.js - Enterprise Admin Dashboard

**Classes/Functions to Test:**

- Admin interface
- User management
- System monitoring
- Configuration management
- Reporting functionality

## Configuration and Assets

### 12. manifest.json - Plugin Manifest

**Properties to Test:**

- Plugin metadata validation
- Version compatibility
- Permission requirements
- Entry point specification

### 13. config.template.json - Configuration Template

**Properties to Test:**

- Default configuration values
- Configuration schema
- Validation rules

## UI and Styling

### 14. styles.css - Plugin Styles

**Elements to Test:**

- CSS class definitions
- Responsive design
- Theme compatibility
- UI component styling

## Legacy Files (Lower Priority)

### 15. main_old.js - Legacy Plugin Implementation

Note: Legacy code for backward compatibility

### 16. main_new.js - New Plugin Implementation

Note: Updated plugin implementation

### 17. styles_old.css / styles_new.css - Style Variants

Note: Different style implementations

## Testing Priority

1. High Priority (Core functionality):

   - main.js
   - backendClient.js
   - rightPane.js
   - taskQueue.js

2. Medium Priority (Features):

   - taskQueueView.js
   - voice.js
   - voiceInput.js
   - analyticsPane.js

3. Low Priority (Enterprise):

   - enterpriseAuth.js
   - enterpriseConfig.js
   - adminDashboard.js

4. Support (Configuration):

   - manifest.json
   - config.template.json

## Sensitive Modules Requiring Security Testing

- enterpriseAuth.js (authentication, tokens)
- backendClient.js (API security, headers)
- main.js (plugin security, settings)
- rightPane.js (user input validation)

## Key Functions and Classes Summary

### Main Classes

- ObsidianAIAssistant (main.js) - Main plugin class
- BackendClient (backendClient.js) - API communication
- AIRightPaneView (rightPane.js) - UI component
- TaskQueue (taskQueue.js) - Task management
- TaskQueueView (taskQueueView.js) - Queue UI
- VoiceRecorder (voice.js) - Voice functionality
- VoiceInput (voiceInput.js) - Voice processing

### Critical Functions

- Plugin lifecycle (onload/onunload)
- API communication methods
- UI rendering and event handling
- Task queue operations
- Voice recording and processing
- Authentication and authorization
- Error handling and recovery

## Notes

- Total plugin modules: 19 files (including legacy and style files)
- Core modules: 8 JavaScript files requiring comprehensive testing
- Enterprise modules: 3 files requiring security-focused testing
- Configuration files: 2 JSON files requiring validation testing
- Legacy files: 3 files requiring minimal testing
- Target coverage: >=90% for all active modules
- Focus on user interactions, API integration, and data processing
- Special attention to browser compatibility and Obsidian API usage
```
