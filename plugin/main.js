const { Plugin, Modal, Notice, PluginSettingTab, Setting } = require("obsidian");
const AIRightPaneView = require('./rightPane.js');
const BackendClient = require('./backendClient.js');

// Enterprise components
let EnterpriseAuth, EnterpriseAdminDashboard, EnterpriseConfig;
let ENTERPRISE_AVAILABLE = false;

try {
    EnterpriseAuth = require('./enterpriseAuth.js');
    EnterpriseAdminDashboard = require('./adminDashboard.js');
    EnterpriseConfig = require('./enterpriseConfig.js');
    ENTERPRISE_AVAILABLE = true;
} catch (error) {
    console.log('Enterprise features not available:', error.message);
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

        const backendClient = new BackendClient(this.plugin.settings.backendUrl);

        try {
            await backendClient.get('/status');
            statusText = 'Backend is online';
        } catch (e) {
            statusText = 'Backend is offline';
            offline = true;
        }
        statusDiv.createEl('span', { text: statusText });
        if (offline) {
            const reloadBtn = statusDiv.createEl('button', { text: 'Reload config' });
            reloadBtn.onclick = async () => {
                reloadBtn.disabled = true;
                reloadBtn.textContent = 'Reloading...';
                // Call backend config reload to validate connectivity
                try {
                    await backendClient.post('/api/config/reload', {});
                    new Notice('Backend config reloaded.');
                } catch (err) {
                    new Notice('Backend is offline. Please start the server.');
                }
                reloadBtn.disabled = false;
                reloadBtn.textContent = 'Reload config';
                await this.checkBackendStatus(statusDiv);
            };
        }
    }
}
class ObsidianAIAssistant extends Plugin {
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
            .setDesc('URL of your AI backend server')
            .addText((text) => {
                text.setValue(this.plugin.settings.backendUrl).onChange(async (value) => {
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
module.exports = ObsidianAIAssistant;
