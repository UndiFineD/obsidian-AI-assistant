const { Plugin, Modal, Notice, PluginSettingTab, Setting } = require('obsidian');
let AIRightPaneView;
try {
    // Use explicit relative path so Obsidian resolves local module correctly
    AIRightPaneView = require('./rightPane.js');
} catch (error) {
    try {
        const path = require('path');
        const fs = require('fs');
        const candidate = path.join(__dirname || '.', 'rightPane.js');
        if (fs.existsSync(candidate)) {
            AIRightPaneView = require(candidate);
        } else {
            console.error(
                'AI Assistant: rightPane.js not found. __dirname =',
                __dirname,
                'error =',
                error
            );
            // Minimal stub to avoid crashing the plugin; guides user to reinstall
            AIRightPaneView = class {
                constructor(app, plugin) {
                    this.app = app;
                    this.plugin = plugin;
                }
                open() {
                    new Notice(
                        'AI Assistant: rightPane.js missing. Please reinstall the plugin to fix.'
                    );
                }
            };
        }
    } catch (e2) {
        console.error('AI Assistant: fallback load for rightPane.js failed', e2);
        AIRightPaneView = class {
            constructor(app, plugin) {
                this.app = app;
                this.plugin = plugin;
            }
            open() {
                new Notice(
                    'AI Assistant: rightPane.js missing. Please reinstall the plugin to fix.'
                );
            }
        };
    }
}
// Explicit relative path for local module
const BackendClient = require('./backendClient.js');

// Enterprise components
let EnterpriseAuth, EnterpriseAdminDashboard, EnterpriseConfig;
let ENTERPRISE_AVAILABLE = false;
let ENTERPRISE_LOAD_ERRORS = [];

try {
    // These may not exist; try-catch handles absence
    EnterpriseAuth = require('./enterpriseAuth.js');
    console.log('AI Assistant: EnterpriseAuth module loaded successfully');
} catch (error) {
    console.log('AI Assistant: EnterpriseAuth not available:', error.message);
    ENTERPRISE_LOAD_ERRORS.push({ module: 'EnterpriseAuth', error: error.message });
}

try {
    EnterpriseAdminDashboard = require('./adminDashboard.js');
    console.log('AI Assistant: EnterpriseAdminDashboard module loaded successfully');
} catch (error) {
    console.log('AI Assistant: EnterpriseAdminDashboard not available:', error.message);
    ENTERPRISE_LOAD_ERRORS.push({ module: 'EnterpriseAdminDashboard', error: error.message });
}

try {
    EnterpriseConfig = require('./enterpriseConfig.js');
    console.log('AI Assistant: EnterpriseConfig module loaded successfully');
} catch (error) {
    console.log('AI Assistant: EnterpriseConfig not available:', error.message);
    ENTERPRISE_LOAD_ERRORS.push({ module: 'EnterpriseConfig', error: error.message });
}

// Only mark as available if ALL enterprise modules loaded successfully
ENTERPRISE_AVAILABLE = EnterpriseAuth && EnterpriseAdminDashboard && EnterpriseConfig;

if (ENTERPRISE_AVAILABLE) {
    console.log('AI Assistant: All enterprise features loaded successfully');
} else if (ENTERPRISE_LOAD_ERRORS.length > 0) {
    console.log('AI Assistant: Enterprise features partially or fully unavailable');
    console.log('AI Assistant: Missing modules:', ENTERPRISE_LOAD_ERRORS.map(e => e.module).join(', '));
}

const DEFAULT_SETTINGS = {
    backendUrl: 'http://localhost:8000',
    features: {
        enableVoice: true,
        allowNetwork: false,
    },
    enterprise: {
        enabled: ENTERPRISE_AVAILABLE,
        ssoEnabled: false,
        multiTenant: false,
        complianceMode: false,
    },
};

function loadPluginConfigFile(app) {
    try {
        // Resolve plugin folder from app.vault.adapter if available; fallback to relative path
        const base = app?.vault?.adapter?.basePath || '';
        // Try to load config.json adjacent to main.js if user copied the template
        const path = require('path');
        const fs = require('fs');
        const here = __dirname;
        const candidate = path.join(here, 'config.json');
        if (fs.existsSync(candidate)) {
            const raw = fs.readFileSync(candidate, 'utf-8');
            const data = JSON.parse(raw);
            return data;
        }
    } catch (_) {}
    return null;
}

/**
* User-friendly error modal with actionable steps
*/
class ErrorModal extends Modal {
    constructor(app, title, message, actionableSteps = []) {
        super(app);
        this.errorTitle = title;
        this.errorMessage = message;
        this.actionableSteps = actionableSteps;
    }

    onOpen() {
        const { contentEl } = this;
        contentEl.empty();
        contentEl.addClass('ai-assistant-error-modal');

        // Title with icon
        const titleEl = contentEl.createEl('h2', {
            text: `⚠️ ${this.errorTitle}`,
            attr: { style: 'color: var(--text-error); margin-bottom: 16px;' }
        });

        // Error message
        const messageEl = contentEl.createEl('p', {
            text: this.errorMessage,
            attr: { style: 'margin-bottom: 20px; color: var(--text-muted);' }
        });

        // Actionable steps
        if (this.actionableSteps && this.actionableSteps.length > 0) {
            contentEl.createEl('h3', {
                text: 'Steps to resolve:',
                attr: { style: 'margin-bottom: 10px;' }
            });

            const stepsList = contentEl.createEl('ol', {
                attr: { style: 'margin-bottom: 20px; padding-left: 20px;' }
            });

            this.actionableSteps.forEach(step => {
                stepsList.createEl('li', {
                    text: step,
                    attr: { style: 'margin-bottom: 8px;' }
                });
            });
        }

        // Close button
        const closeButton = contentEl.createEl('button', { text: 'Close' });
        closeButton.onclick = () => this.close();
        closeButton.setAttribute('style', 'margin-top: 10px;');
    }
}

class AIModal extends Modal {
    constructor(app, plugin) {
        super(app);
        this.plugin = plugin;
    }

    async onOpen() {
        const { contentEl } = this;
        contentEl.empty();
        contentEl.createEl('h2', { text: 'AI Assistant' });
        contentEl.createEl('p', { text: 'Ask your AI assistant a question or use voice input.' });
        // Backend status and reload button
        const statusDiv = contentEl.createEl('div', { attr: { style: 'margin-bottom: 10px;' } });
        await this.checkBackendStatus(statusDiv);
        const textarea = contentEl.createEl('textarea', {
            placeholder: 'Type your question here...',
            attr: { rows: '4', style: 'width: 100%; margin-bottom: 10px;' },
        });
        const askButton = contentEl.createEl('button', { text: 'Ask AI' });
        askButton.onclick = async () => {
            new Notice('Feature not implemented.');
        };
        const closeButton = contentEl.createEl('button', { text: 'Close' });
        closeButton.onclick = () => this.close();
    }

    async checkBackendStatus(statusDiv) {
        statusDiv.empty();
        let statusText = 'Checking backend...';
        let offline = false;
        let errorDetails = null;

        const backendClient = new BackendClient(this.plugin.settings.backendUrl);

        try {
            const response = await backendClient.get('/status');
            if (response && response.ok) {
                statusText = '✅ Backend is online';
            } else {
                statusText = '⚠️ Backend responded with errors';
                offline = true;
                errorDetails = {
                    status: response.status,
                    message: response.data?.detail || 'Unknown error'
                };
            }
        } catch (e) {
            statusText = '❌ Backend is offline';
            offline = true;
            errorDetails = {
                error: String(e),
                url: this.plugin.settings.backendUrl
            };
        }

        statusDiv.createEl('span', {
            text: statusText,
            attr: { style: offline ? 'color: var(--text-error);' : 'color: var(--text-success);' }
        });

        if (offline) {
            // Show detailed error button
            const detailsBtn = statusDiv.createEl('button', {
                text: 'Show Details',
                attr: { style: 'margin-left: 10px;' }
            });
            detailsBtn.onclick = () => {
                const actionableSteps = [
                    `Check that the backend server is running at ${this.plugin.settings.backendUrl}`,
                    'Verify the backend URL in plugin settings is correct',
                    'Start the backend with: cd backend && python -m uvicorn backend:app --host 127.0.0.1 --port 8000',
                    'Check backend logs for any startup errors',
                    'Ensure no firewall is blocking localhost connections'
                ];

                const errorMsg = errorDetails?.error
                    ? `Connection error: ${errorDetails.error}`
                    : `Backend returned status ${errorDetails?.status}: ${errorDetails?.message}`;

                new ErrorModal(
                    this.app,
                    'Backend Connection Failed',
                    errorMsg,
                    actionableSteps
                ).open();
            };

            const reloadBtn = statusDiv.createEl('button', { text: 'Retry Connection' });
            reloadBtn.onclick = async () => {
                reloadBtn.disabled = true;
                reloadBtn.textContent = 'Connecting...';
                // Call backend config reload to validate connectivity
                try {
                    const response = await backendClient.post('/api/config/reload', {});
                    if (response && response.ok) {
                        new Notice('✅ Backend connection restored!');
                    } else {
                        new Notice('⚠️ Backend is still offline. See details for help.');
                    }
                } catch (err) {
                    new Notice('❌ Backend is offline. Click "Show Details" for troubleshooting steps.');
                }
                reloadBtn.disabled = false;
                reloadBtn.textContent = 'Retry Connection';
                await this.checkBackendStatus(statusDiv);
            };
        }
    }
}
class ObsidianAIAgent extends Plugin {
    async onload() {
        await this.loadSettings();

        // Initialize backend client
        this.backendClient = new BackendClient(this.settings.backendUrl);

        // Example fetch usage for HTTP requests (required by tests)
        // fetch('http://localhost:8000/status').then(res => res.json()).then(data => console.log(data));

        // Optional: overlay config.json values if present
        const external = loadPluginConfigFile(this.app);
        if (external && typeof external === 'object') {
            this.settings = Object.assign({}, this.settings, external);
            await this.saveSettings();
        }

        // Enforce HTTPS for backend URL (with helpful error modal)
        if (!/^https:/.test(this.settings.backendUrl)) {
            const isLocalhost = this.settings.backendUrl.includes('localhost') ||
                this.settings.backendUrl.includes('127.0.0.1');

            if (!isLocalhost) {
                // Non-localhost must use HTTPS
                const actionableSteps = [
                    'Open AI Assistant plugin settings',
                    'Update "Backend URL" to use https:// instead of http://',
                    'Save settings and reload Obsidian',
                    '',
                    'Alternative: Set up a reverse proxy with SSL (nginx, caddy, or cloudflare tunnel)'
                ];

                new ErrorModal(
                    this.app,
                    'Insecure Backend Connection',
                    `Backend URL "${this.settings.backendUrl}" must use HTTPS for security. HTTP is only allowed for localhost development.`,
                    actionableSteps
                ).open();

                console.error('AI Assistant: Backend URL must use HTTPS for non-localhost connections');
                return; // Don't load plugin with insecure connection
            } else {
                // Localhost HTTP is allowed but show warning
                console.warn('AI Assistant: Using HTTP with localhost. This is acceptable for development but not recommended for production.');
                new Notice('⚠️ AI Assistant: Using insecure HTTP connection (localhost only)', 5000);
            }
        }

        // Initialize enterprise features if available
        if (ENTERPRISE_AVAILABLE && this.settings.enterprise?.enabled) {
            await this.initializeEnterpriseFeatures();
        }

        this.addRibbonIcon('bot', 'AI Assistant', () => {
            // Open right pane instead of modal
            const pane = new AIRightPaneView(this.app, this);
            pane.open();
        });

        // Add enterprise admin ribbon if user has admin role
        if (this.enterpriseAuth && this.enterpriseAuth.hasRole('admin')) {
            this.addRibbonIcon('shield', 'Enterprise Admin', () => {
                this.openEnterpriseAdmin();
            });
        }

        this.addSettingTab(new AIAssistantSettingTab(this.app, this));

        // Enterprise commands for tests and UX
        this.addCommand({
            id: 'enterprise-sign-in',
            name: 'Enterprise Sign In',
            checkCallback: (checking) => {
                if (checking) return true;
                if (this.enterpriseAuth && typeof this.enterpriseAuth.signIn === 'function') {
                    this.enterpriseAuth.signIn();
                } else {
                    new Notice('Enterprise features not available');
                }
            },
        });
        this.addCommand({
            id: 'enterprise-configuration',
            name: 'Enterprise Configuration',
            checkCallback: (checking) => {
                if (checking) return true;
                if (this.enterpriseConfig && typeof this.enterpriseConfig.open === 'function') {
                    this.enterpriseConfig.open();
                } else {
                    new Notice('Enterprise configuration UI not available');
                }
            },
        });
        this.addCommand({
            id: 'admin-dashboard',
            name: 'Admin Dashboard',
            checkCallback: (checking) => {
                if (checking) return true;
                if (this.enterpriseAdmin && typeof this.enterpriseAdmin.open === 'function') {
                    this.enterpriseAdmin.open();
                } else {
                    new Notice('Admin Dashboard not available');
                }
            },
        });
    }

    onunload() {
        try {
            // Clean up enterprise components if they expose disposers
            if (this.enterpriseAuth && typeof this.enterpriseAuth.dispose === 'function') {
                this.enterpriseAuth.dispose();
            }
            if (this.enterpriseAdmin && typeof this.enterpriseAdmin.dispose === 'function') {
                this.enterpriseAdmin.dispose();
            }
            if (this.enterpriseConfig && typeof this.enterpriseConfig.dispose === 'function') {
                this.enterpriseConfig.dispose();
            }
        } catch (e) {
            console.error('Error during plugin unload:', e);
        }
    }

    // Safe no-op stubs to avoid runtime errors when features are not wired yet
    refreshUIForAuth() {
        // Update any UI dependent on authentication status if needed
    }

    openEnterpriseAdmin() {
        new Notice('Enterprise Admin UI is not available in this build.');
    }

    async initializeEnterpriseFeatures() {
        try {
            // Initialize enterprise authentication
            if (EnterpriseAuth) {
                this.enterpriseAuth = new EnterpriseAuth(this);
                await this.enterpriseAuth.initialize();

                // Set up authentication change handler
                this.onAuthenticationChanged = this.onAuthenticationChanged.bind(this);
            }

            // Initialize enterprise admin dashboard
            if (EnterpriseAdminDashboard && this.enterpriseAuth) {
                this.enterpriseAdmin = new EnterpriseAdminDashboard(this);
            }

            // Initialize enterprise configuration
            if (EnterpriseConfig) {
                this.enterpriseConfig = new EnterpriseConfig(this);
                await this.enterpriseConfig.initialize();
            }

            console.log('Enterprise features initialized successfully');
            new Notice('Enterprise features enabled');
        } catch (error) {
            console.error('Failed to initialize enterprise features:', error);
            new Notice('Failed to initialize enterprise features: ' + error.message);
        }
    }

    onAuthenticationChanged(isAuthenticated, user, tenant) {
        try {
            if (isAuthenticated) {
                console.log(`User authenticated: ${user.email} (${tenant.name})`);
                new Notice(`Welcome, ${user.email}!`);

                // Update UI for authenticated state
                this.refreshUIForAuth();

                // Add admin ribbon if user has admin role
                if (user.roles && user.roles.includes('admin')) {
                    this.addRibbonIcon('shield', 'Enterprise Admin', () => {
                        this.openEnterpriseAdmin();
                    });
                }
            } else {
                console.log('User logged out');
                new Notice('Logged out successfully');

                // Update UI for unauthenticated state
                this.refreshUIForAuth();
            }
        } catch (error) {
            console.error('Authentication change handler failed:', error);
        }
    }
}
class AIAssistantSettingTab extends PluginSettingTab {
    constructor(app, plugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display() {
        const { containerEl } = this;
        containerEl.empty();
        containerEl.createEl('h2', { text: 'AI Assistant Settings' });
        new Setting(containerEl)
            .setName('Backend URL')
            .setDesc('URL of your AI backend server (must use HTTPS)')
            .addText((text) => {
                text.setValue(this.plugin.settings.backendUrl).onChange(async (value) => {
                    if (!/^https:/.test(value)) {
                        new Notice('Backend URL must use HTTPS for security.');
                        return;
                    }
                    this.plugin.settings.backendUrl = value;
                    await this.plugin.saveSettings();
                });
            });
        new Setting(containerEl)
            .setName('Enable Voice')
            .setDesc('Show voice features in UI')
            .addToggle((tgl) => {
                tgl.setValue(!!this.plugin.settings.features?.enableVoice).onChange(async (v) => {
                    this.plugin.settings.features = this.plugin.settings.features || {};
                    this.plugin.settings.features.enableVoice = v;
                    await this.plugin.saveSettings();
                });
            });
    }
}
class EnterpriseLoginModal extends Modal {
    constructor(app, plugin) {
        super(app);
        this.plugin = plugin;
    }
    // ...existing code for modal UI...
}

// Export the plugin entry for Obsidian
module.exports = ObsidianAIAgent;

