// EnterpriseConfig.js
// Provides enterprise configuration management for Obsidian AI Agent plugin

class EnterpriseConfig {
    constructor(plugin) {
        this.plugin = plugin;
        this.settings = {};
    }

    async loadSettings() {
        // Load settings from config file or backend
        try {
            const response = await this.plugin.backendClient.request('GET', '/api/config');
            this.settings = response.data || {};
        } catch (error) {
            console.error('Failed to load enterprise config:', error);
        }
    }

    async saveSettings(newSettings) {
        // Save settings to backend
        try {
            await this.plugin.backendClient.request('POST', '/api/config', newSettings);
            this.settings = { ...this.settings, ...newSettings };
        } catch (error) {
            console.error('Failed to save enterprise config:', error);
        }
    }

    getSetting(key) {
        return this.settings[key];
    }

    setSetting(key, value) {
        this.settings[key] = value;
    }
}

module.exports = EnterpriseConfig;

