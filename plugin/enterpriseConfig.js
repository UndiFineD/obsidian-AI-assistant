// Enterprise Configuration Management Component
// Manages enterprise settings, tenant configurations, and compliance policies

class EnterpriseConfig { constructor(plugin) { this.plugin = plugin;
        this.backendClient = plugin.backendClient;
        this.enterpriseAuth = plugin.enterpriseAuth;
        this.config = {};
        this.tenantConfig = {};
        this.complianceConfig = {};
    }

    async initialize() { try { await this.loadConfiguration();
        } catch(error) { console.error('Failed to initialize enterprise config:', error);
        }
    }

    async loadConfiguration() { try {
            // Load enterprise configuration
            const configResponse = await this.backendClient.request('/admin/config', { method: 'GET'
            });

            if(configResponse.ok) { this.config = configResponse.data;
            }

            // Load tenant-specific configuration if authenticated
            if(this.enterpriseAuth.isAuthenticated()) { const tenantId = this.enterpriseAuth.getCurrentTenant().tenant_id;
                const tenantResponse = await this.backendClient.request(`/tenant/${ tenantId }/config`, { method: 'GET'
                });

                if(tenantResponse.ok) { this.tenantConfig = tenantResponse.data;
                }
            }

        } catch(error) { console.error('Failed to load configuration:', error);
        }
    }

    createConfigurationInterface(containerEl) { containerEl.empty();

        const configEl = containerEl.createEl('div', { cls: 'enterprise-config' });

        // Configuration tabs
        this.createConfigTabs(configEl);

        // Configuration content
        const contentEl = configEl.createEl('div', { cls: 'config-content' });

        // Default to general settings
        this.renderGeneralSettings(contentEl);
    }

    createConfigTabs(containerEl) { const tabsEl = containerEl.createEl('div', { cls: 'config-tabs' });

        const tabs = [
            { id: 'general', label: 'General', icon: '⚙️' },
            { id: 'security', label: 'Security', icon: '🛡️' },
            { id: 'compliance', label: 'Compliance', icon: '📋' },
            { id: 'tenant', label: 'Tenant Settings', icon: '🏢' },
            { id: 'integrations', label: 'Integrations', icon: '🔗' },
            { id: 'notifications', label: 'Notifications', icon: '🔔' }
        ];

        tabs.forEach(tab => { const tabEl = tabsEl.createEl('button', { cls: 'config-tab',
                text: `${ tab.icon } ${ tab.label }`
            });

            tabEl.addEventListener('click', () => { this.switchConfigTab(tab.id, containerEl);
            });
        });
    }

    switchConfigTab(tabId, containerEl) {
        // Update active tab
        const tabs = containerEl.querySelectorAll('.config-tab');
        tabs.forEach(tab => tab.removeClass('active'));

        const activeTab = Array.from(tabs).find(tab =>
            tab.textContent.toLowerCase().includes(tabId.toLowerCase())
        );
        if(activeTab) activeTab.addClass('active');

        // Update content
        const contentEl = containerEl.querySelector('.config-content');
        if(contentEl) { this.renderConfigContent(tabId, contentEl);
        }
    }

    renderConfigContent(tabId, contentEl) { contentEl.empty();

        switch(tabId) { case 'general':
                this.renderGeneralSettings(contentEl);
                break;
            case 'security':
                this.renderSecuritySettings(contentEl);
                break;
            case 'compliance':
                this.renderComplianceSettings(contentEl);
                break;
            case 'tenant':
                this.renderTenantSettings(contentEl);
                break;
            case 'integrations':
                this.renderIntegrationSettings(contentEl);
                break;
            case 'notifications':
                this.renderNotificationSettings(contentEl);
                break;
            default: this.renderGeneralSettings(contentEl);
        }
    }

    renderGeneralSettings(contentEl) { const settingsEl = contentEl.createEl('div', { cls: 'settings-section' });

        settingsEl.createEl('h3', { text: 'General Settings' });

        // Enterprise features toggle
        const featuresGroup = this.createSettingGroup(settingsEl, 'Enterprise Features');

        this.createToggleSetting(featuresGroup, { key: 'enterprise_enabled',
            label: 'Enable Enterprise Features',
            description: 'Enable advanced enterprise functionality',
            value: this.config.enterprise_enabled || false });

        this.createToggleSetting(featuresGroup, { key: 'sso_enabled',
            label: 'Single Sign-On(SSO)',
            description: 'Enable SSO authentication',
            value: this.config.sso_enabled || false });

        this.createToggleSetting(featuresGroup, { key: 'multi_tenant',
            label: 'Multi-Tenant Mode',
            description: 'Enable multi-tenant architecture',
            value: this.config.multi_tenant || false });

        // System settings
        const systemGroup = this.createSettingGroup(settingsEl, 'System Configuration');

        this.createTextSetting(systemGroup, { key: 'organization_name',
            label: 'Organization Name',
            description: 'Name of your organization',
            value: this.config.organization_name || '',
            placeholder: 'Enter organization name'
        });

        this.createSelectSetting(systemGroup, { key: 'default_timezone',
            label: 'Default Timezone',
            description: 'Default timezone for the system',
            value: this.config.default_timezone || 'UTC',
            options: [
                { value: 'UTC', label: 'UTC' },
                { value: 'America/New_York', label: 'Eastern Time' },
                { value: 'America/Chicago', label: 'Central Time' },
                { value: 'America/Denver', label: 'Mountain Time' },
                { value: 'America/Los_Angeles', label: 'Pacific Time' },
                { value: 'Europe/London', label: 'London' },
                { value: 'Europe/Paris', label: 'Paris' },
                { value: 'Asia/Tokyo', label: 'Tokyo' }
            ]
        });

        this.createNumberSetting(systemGroup, { key: 'session_timeout',
            label: 'Session Timeout(minutes)',
            description: 'User session timeout in minutes',
            value: this.config.session_timeout || 480,
            min: 30,
            max: 1440 });

        // Save button
        this.createSaveButton(settingsEl, () => this.saveGeneralSettings());
    }

    renderSecuritySettings(contentEl) { const settingsEl = contentEl.createEl('div', { cls: 'settings-section' });

        settingsEl.createEl('h3', { text: 'Security Settings' });

        // Authentication settings
        const authGroup = this.createSettingGroup(settingsEl, 'Authentication');

        this.createToggleSetting(authGroup, { key: 'require_mfa',
            label: 'Require Multi-Factor Authentication',
            description: 'Force all users to enable MFA',
            value: this.config.require_mfa || false });

        this.createToggleSetting(authGroup, { key: 'strong_passwords',
            label: 'Enforce Strong Passwords',
            description: 'Require complex passwords',
            value: this.config.strong_passwords || true });

        this.createNumberSetting(authGroup, { key: 'password_min_length',
            label: 'Minimum Password Length',
            description: 'Minimum number of characters for passwords',
            value: this.config.password_min_length || 12,
            min: 8,
            max: 128 });

        this.createNumberSetting(authGroup, { key: 'max_login_attempts',
            label: 'Maximum Login Attempts',
            description: 'Lock account after this many failed attempts',
            value: this.config.max_login_attempts || 5,
            min: 3,
            max: 10 });

        // Access control
        const accessGroup = this.createSettingGroup(settingsEl, 'Access Control');

        this.createToggleSetting(accessGroup, { key: 'ip_restriction',
            label: 'IP Address Restrictions',
            description: 'Restrict access by IP address',
            value: this.config.ip_restriction || false });

        this.createTextAreaSetting(accessGroup, { key: 'allowed_ips',
            label: 'Allowed IP Addresses',
            description: 'One IP or CIDR range per line',
            value: this.config.allowed_ips || '',
            placeholder: '192.168.1.0/24\n10.0.0.0/8'
        });

        this.createToggleSetting(accessGroup, { key: 'geo_blocking',
            label: 'Geographic Restrictions',
            description: 'Block access from certain countries',
            value: this.config.geo_blocking || false });

        // Encryption settings
        const encryptionGroup = this.createSettingGroup(settingsEl, 'Encryption');

        this.createSelectSetting(encryptionGroup, { key: 'encryption_level',
            label: 'Encryption Level',
            description: 'Data encryption strength',
            value: this.config.encryption_level || 'aes256',
            options: [
                { value: 'aes128', label: 'AES-128' },
                { value: 'aes256', label: 'AES-256' },
                { value: 'aes256gcm', label: 'AES-256-GCM' }
            ]
        });

        this.createToggleSetting(encryptionGroup, { key: 'encrypt_at_rest',
            label: 'Encrypt Data at Rest',
            description: 'Encrypt stored data',
            value: this.config.encrypt_at_rest || true });

        this.createToggleSetting(encryptionGroup, { key: 'encrypt_in_transit',
            label: 'Encrypt Data in Transit',
            description: 'Force HTTPS/TLS encryption',
            value: this.config.encrypt_in_transit || true });

        this.createSaveButton(settingsEl, () => this.saveSecuritySettings());
    }

    renderComplianceSettings(contentEl) { const settingsEl = contentEl.createEl('div', { cls: 'settings-section' });

        settingsEl.createEl('h3', { text: 'Compliance Settings' });

        // GDPR settings
        const gdprGroup = this.createSettingGroup(settingsEl, 'GDPR Compliance');

        this.createToggleSetting(gdprGroup, { key: 'gdpr_enabled',
            label: 'Enable GDPR Compliance',
            description: 'Activate GDPR data protection features',
            value: this.config.gdpr_enabled || false });

        this.createSelectSetting(gdprGroup, { key: 'data_retention_period',
            label: 'Default Data Retention Period',
            description: 'How long to keep user data',
            value: this.config.data_retention_period || '7years',
            options: [
                { value: '1year', label: '1 Year' },
                { value: '2years', label: '2 Years' },
                { value: '3years', label: '3 Years' },
                { value: '5years', label: '5 Years' },
                { value: '7years', label: '7 Years' },
                { value: '10years', label: '10 Years' },
                { value: 'indefinite', label: 'Indefinite(User Controlled)' }
            ]
        });

        this.createToggleSetting(gdprGroup, { key: 'consent_management',
            label: 'Consent Management',
            description: 'Track and manage user consent',
            value: this.config.consent_management || true });

        this.createToggleSetting(gdprGroup, { key: 'right_to_erasure',
            label: 'Right to Erasure',
            description: 'Allow users to delete their data',
            value: this.config.right_to_erasure || true });

        // SOC2 settings
        const soc2Group = this.createSettingGroup(settingsEl, 'SOC2 Compliance');

        this.createToggleSetting(soc2Group, { key: 'soc2_enabled',
            label: 'Enable SOC2 Compliance',
            description: 'Activate SOC2 security controls',
            value: this.config.soc2_enabled || false });

        this.createToggleSetting(soc2Group, { key: 'audit_logging',
            label: 'Comprehensive Audit Logging',
            description: 'Log all system activities for auditing',
            value: this.config.audit_logging || true });

        this.createSelectSetting(soc2Group, { key: 'log_retention_period',
            label: 'Log Retention Period',
            description: 'How long to keep audit logs',
            value: this.config.log_retention_period || '7years',
            options: [
                { value: '1year', label: '1 Year' },
                { value: '2years', label: '2 Years' },
                { value: '3years', label: '3 Years' },
                { value: '5years', label: '5 Years' },
                { value: '7years', label: '7 Years' }
            ]
        });

        // Compliance reporting
        const reportingGroup = this.createSettingGroup(settingsEl, 'Compliance Reporting');

        this.createToggleSetting(reportingGroup, { key: 'automated_reports',
            label: 'Automated Compliance Reports',
            description: 'Generate compliance reports automatically',
            value: this.config.automated_reports || false });

        this.createSelectSetting(reportingGroup, { key: 'report_frequency',
            label: 'Report Frequency',
            description: 'How often to generate reports',
            value: this.config.report_frequency || 'monthly',
            options: [
                { value: 'weekly', label: 'Weekly' },
                { value: 'monthly', label: 'Monthly' },
                { value: 'quarterly', label: 'Quarterly' },
                { value: 'annually', label: 'Annually' }
            ]
        });

        this.createSaveButton(settingsEl, () => this.saveComplianceSettings());
    }

    renderTenantSettings(contentEl) { if(!this.enterpriseAuth.isAuthenticated()) { contentEl.createEl('p', { text: 'Please sign in to manage tenant settings',
                cls: 'error-message'
            });
            return;
        }

        const settingsEl = contentEl.createEl('div', { cls: 'settings-section' });

        const currentTenant = this.enterpriseAuth.getCurrentTenant();
        settingsEl.createEl('h3', { text: `Tenant Settings - ${ currentTenant.name }` });

        // Tenant information
        const infoGroup = this.createSettingGroup(settingsEl, 'Tenant Information');

        this.createTextSetting(infoGroup, { key: 'tenant_name',
            label: 'Tenant Name',
            description: 'Display name for this tenant',
            value: this.tenantConfig.tenant_name || currentTenant.name,
            placeholder: 'Enter tenant name'
        });

        this.createTextAreaSetting(infoGroup, { key: 'tenant_description',
            label: 'Description',
            description: 'Brief description of this tenant',
            value: this.tenantConfig.tenant_description || '',
            placeholder: 'Enter tenant description'
        });

        // Resource limits
        const limitsGroup = this.createSettingGroup(settingsEl, 'Resource Limits');

        this.createNumberSetting(limitsGroup, { key: 'max_users',
            label: 'Maximum Users',
            description: 'Maximum number of users for this tenant',
            value: this.tenantConfig.max_users || 100,
            min: 1,
            max: 10000 });

        this.createNumberSetting(limitsGroup, { key: 'max_storage_gb',
            label: 'Storage Limit(GB)',
            description: 'Maximum storage in gigabytes',
            value: this.tenantConfig.max_storage_gb || 10,
            min: 1,
            max: 1000 });

        this.createNumberSetting(limitsGroup, { key: 'max_api_calls_monthly',
            label: 'Monthly API Call Limit',
            description: 'Maximum API calls per month',
            value: this.tenantConfig.max_api_calls_monthly || 10000,
            min: 1000,
            max: 1000000 });

        // Feature settings
        const featuresGroup = this.createSettingGroup(settingsEl, 'Tenant Features');

        this.createToggleSetting(featuresGroup, { key: 'voice_processing',
            label: 'Voice Processing',
            description: 'Enable voice input and transcription',
            value: this.tenantConfig.voice_processing !== false });

        this.createToggleSetting(featuresGroup, { key: 'web_search',
            label: 'Web Search',
            description: 'Enable web search capabilities',
            value: this.tenantConfig.web_search !== false });

        this.createToggleSetting(featuresGroup, { key: 'analytics',
            label: 'Analytics Dashboard',
            description: 'Enable usage analytics',
            value: this.tenantConfig.analytics !== false });

        this.createSaveButton(settingsEl, () => this.saveTenantSettings());
    }

    renderIntegrationSettings(contentEl) { const settingsEl = contentEl.createEl('div', { cls: 'settings-section' });

        settingsEl.createEl('h3', { text: 'Integration Settings' });

        // SSO providers
        const ssoGroup = this.createSettingGroup(settingsEl, 'SSO Providers');

        const providers = ['Azure AD', 'Google Workspace', 'Okta', 'SAML', 'LDAP'];

        providers.forEach(provider => { const providerKey = provider.toLowerCase().replace(/\s+/g, '_');

            this.createToggleSetting(ssoGroup, { key: `sso_${ providerKey }_enabled`,
                label: `Enable ${ provider }`,
                description: `Enable ${ provider } SSO integration`,
                value: this.config[`sso_${ providerKey }_enabled`] || false });
        });

        // API integrations
        const apiGroup = this.createSettingGroup(settingsEl, 'API Integrations');

        this.createTextSetting(apiGroup, { key: 'webhook_url',
            label: 'Webhook URL',
            description: 'URL for system notifications',
            value: this.config.webhook_url || '',
            placeholder: 'https://example.com/webhook'
        });

        this.createSelectSetting(apiGroup, { key: 'api_rate_limit',
            label: 'API Rate Limit',
            description: 'Requests per minute per user',
            value: this.config.api_rate_limit || '60',
            options: [
                { value: '30', label: '30 req/min' },
                { value: '60', label: '60 req/min' },
                { value: '120', label: '120 req/min' },
                { value: '300', label: '300 req/min' },
                { value: 'unlimited', label: 'Unlimited' }
            ]
        });

        this.createSaveButton(settingsEl, () => this.saveIntegrationSettings());
    }

    renderNotificationSettings(contentEl) { const settingsEl = contentEl.createEl('div', { cls: 'settings-section' });

        settingsEl.createEl('h3', { text: 'Notification Settings' });

        // Email notifications
        const emailGroup = this.createSettingGroup(settingsEl, 'Email Notifications');

        this.createToggleSetting(emailGroup, { key: 'email_notifications',
            label: 'Enable Email Notifications',
            description: 'Send system notifications via email',
            value: this.config.email_notifications || false });

        this.createTextSetting(emailGroup, { key: 'smtp_server',
            label: 'SMTP Server',
            description: 'SMTP server for sending emails',
            value: this.config.smtp_server || '',
            placeholder: 'smtp.example.com'
        });

        this.createTextSetting(emailGroup, { key: 'from_email',
            label: 'From Email Address',
            description: 'Email address for system notifications',
            value: this.config.from_email || '',
            placeholder: 'noreply@example.com'
        });

        // Alert settings
        const alertGroup = this.createSettingGroup(settingsEl, 'System Alerts');

        this.createToggleSetting(alertGroup, { key: 'security_alerts',
            label: 'Security Alerts',
            description: 'Notify about security incidents',
            value: this.config.security_alerts !== false });

        this.createToggleSetting(alertGroup, { key: 'compliance_alerts',
            label: 'Compliance Alerts',
            description: 'Notify about compliance issues',
            value: this.config.compliance_alerts !== false });

        this.createToggleSetting(alertGroup, { key: 'system_alerts',
            label: 'System Alerts',
            description: 'Notify about system issues',
            value: this.config.system_alerts !== false });

        this.createSaveButton(settingsEl, () => this.saveNotificationSettings());
    }

    // Helper methods for creating setting controls
    createSettingGroup(containerEl, title) { const groupEl = containerEl.createEl('div', { cls: 'setting-group' });
        groupEl.createEl('h4', { text: title, cls: 'setting-group-title' });
        return groupEl;
    }

    createToggleSetting(containerEl, setting) { const settingEl = containerEl.createEl('div', { cls: 'setting-item toggle-setting' });

        const labelEl = settingEl.createEl('div', { cls: 'setting-label' });
        labelEl.createEl('span', { text: setting.label, cls: 'setting-name' });
        labelEl.createEl('p', { text: setting.description, cls: 'setting-description' });

        const controlEl = settingEl.createEl('div', { cls: 'setting-control' });
        const toggle = controlEl.createEl('input', { type: 'checkbox',
            cls: 'toggle-input'
        });
        toggle.checked = setting.value;
        toggle.dataset.key = setting.key;

        return settingEl;
    }

    createTextSetting(containerEl, setting) { const settingEl = containerEl.createEl('div', { cls: 'setting-item text-setting' });

        const labelEl = settingEl.createEl('div', { cls: 'setting-label' });
        labelEl.createEl('label', { text: setting.label, cls: 'setting-name' });
        labelEl.createEl('p', { text: setting.description, cls: 'setting-description' });

        const controlEl = settingEl.createEl('div', { cls: 'setting-control' });
        const input = controlEl.createEl('input', { type: 'text',
            cls: 'text-input',
            placeholder: setting.placeholder || ''
        });
        input.value = setting.value;
        input.dataset.key = setting.key;

        return settingEl;
    }

    createTextAreaSetting(containerEl, setting) { const settingEl = containerEl.createEl('div', { cls: 'setting-item textarea-setting' });

        const labelEl = settingEl.createEl('div', { cls: 'setting-label' });
        labelEl.createEl('label', { text: setting.label, cls: 'setting-name' });
        labelEl.createEl('p', { text: setting.description, cls: 'setting-description' });

        const controlEl = settingEl.createEl('div', { cls: 'setting-control' });
        const textarea = controlEl.createEl('textarea', { cls: 'textarea-input',
            placeholder: setting.placeholder || ''
        });
        textarea.value = setting.value;
        textarea.dataset.key = setting.key;

        return settingEl;
    }

    createNumberSetting(containerEl, setting) { const settingEl = containerEl.createEl('div', { cls: 'setting-item number-setting' });

        const labelEl = settingEl.createEl('div', { cls: 'setting-label' });
        labelEl.createEl('label', { text: setting.label, cls: 'setting-name' });
        labelEl.createEl('p', { text: setting.description, cls: 'setting-description' });

        const controlEl = settingEl.createEl('div', { cls: 'setting-control' });
        const input = controlEl.createEl('input', { type: 'number',
            cls: 'number-input'
        });
        input.value = setting.value;
        input.min = setting.min || 0;
        input.max = setting.max || 999999;
        input.dataset.key = setting.key;

        return settingEl;
    }

    createSelectSetting(containerEl, setting) { const settingEl = containerEl.createEl('div', { cls: 'setting-item select-setting' });

        const labelEl = settingEl.createEl('div', { cls: 'setting-label' });
        labelEl.createEl('label', { text: setting.label, cls: 'setting-name' });
        labelEl.createEl('p', { text: setting.description, cls: 'setting-description' });

        const controlEl = settingEl.createEl('div', { cls: 'setting-control' });
        const select = controlEl.createEl('select', { cls: 'select-input' });

        setting.options.forEach(option => { const optionEl = select.createEl('option', { value: option.value,
                text: option.label });
            if(option.value === setting.value) { optionEl.selected = true;
            }
        });

        select.dataset.key = setting.key;

        return settingEl;
    }

    createSaveButton(containerEl, saveCallback) { const buttonContainer = containerEl.createEl('div', { cls: 'setting-buttons' });

        const saveBtn = buttonContainer.createEl('button', { text: 'Save Settings',
            cls: 'btn btn-primary save-btn'
        });

        saveBtn.addEventListener('click', async() => { try { saveBtn.disabled = true;
                saveBtn.textContent = 'Saving...';

                await saveCallback();

                saveBtn.textContent = 'Saved!';
                setTimeout(() => { saveBtn.disabled = false;
                    saveBtn.textContent = 'Save Settings';
                }, 2000);

            } catch(error) { console.error('Save failed:', error);
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save Settings';
                this.showError(containerEl, 'Failed to save settings: ' + error.message);
            }
        });
    }

    // Save methods
    async saveGeneralSettings() { const settings = this.collectSettings('general');

        const response = await this.backendClient.request('/admin/config/general', { method: 'POST',
            data: settings });

        if(!response.ok) { throw new Error(response.message || 'Failed to save general settings');
        }

        // Update local config
        Object.assign(this.config, settings);
    }

    async saveSecuritySettings() { const settings = this.collectSettings('security');

        const response = await this.backendClient.request('/admin/config/security', { method: 'POST',
            data: settings });

        if(!response.ok) { throw new Error(response.message || 'Failed to save security settings');
        }

        Object.assign(this.config, settings);
    }

    async saveComplianceSettings() { const settings = this.collectSettings('compliance');

        const response = await this.backendClient.request('/admin/config/compliance', { method: 'POST',
            data: settings });

        if(!response.ok) { throw new Error(response.message || 'Failed to save compliance settings');
        }

        Object.assign(this.complianceConfig, settings);
    }

    async saveTenantSettings() { const settings = this.collectSettings('tenant');
        const tenantId = this.enterpriseAuth.getCurrentTenant().tenant_id;

        const response = await this.backendClient.request(`/tenant/${ tenantId }/config`, { method: 'POST',
            data: settings });

        if(!response.ok) { throw new Error(response.message || 'Failed to save tenant settings');
        }

        Object.assign(this.tenantConfig, settings);
    }

    async saveIntegrationSettings() { const settings = this.collectSettings('integration');

        const response = await this.backendClient.request('/admin/config/integrations', { method: 'POST',
            data: settings });

        if(!response.ok) { throw new Error(response.message || 'Failed to save integration settings');
        }

        Object.assign(this.config, settings);
    }

    async saveNotificationSettings() { const settings = this.collectSettings('notification');

        const response = await this.backendClient.request('/admin/config/notifications', { method: 'POST',
            data: settings });

        if(!response.ok) { throw new Error(response.message || 'Failed to save notification settings');
        }

        Object.assign(this.config, settings);
    }

    collectSettings(section) { const settings = {};
        const inputs = document.querySelectorAll(`[data-key]`);

        inputs.forEach(input => { const key = input.dataset.key;
            let value;

            if(input.type === 'checkbox') { value = input.checked;
            } else if(input.type === 'number') { value = parseInt(input.value) || 0;
            } else { value = input.value;
            }

            settings[key] = value;
        });

        return settings;
    }

    showError(containerEl, message) { let errorEl = containerEl.querySelector('.config-error');
        if(!errorEl) { errorEl = containerEl.createEl('div', { cls: 'config-error' });
        }

        errorEl.empty();
        errorEl.createEl('p', { text: message });

        setTimeout(() => { if(errorEl) errorEl.remove();
        }, 5000);
    }
}

module.exports = EnterpriseConfig;