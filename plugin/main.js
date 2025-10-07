const { Plugin, Modal, Notice, PluginSettingTab, Setting } = require("obsidian");
const AIRightPaneView = require("./rightPane.js");
const BackendClient = require("./backendClient.js");

// Enterprise components
let EnterpriseAuth, EnterpriseAdminDashboard, EnterpriseConfig;
let ENTERPRISE_AVAILABLE = false;

try {
  EnterpriseAuth = require("./enterpriseAuth.js");
  EnterpriseAdminDashboard = require("./adminDashboard.js");
  EnterpriseConfig = require("./enterpriseConfig.js");
  ENTERPRISE_AVAILABLE = true;
} catch (error) {
  console.log("Enterprise features not available:", error.message);
}

const DEFAULT_SETTINGS = {
  backendUrl: "http://localhost:8000",
  features: { enableVoice: true, allowNetwork: false },
  enterprise: {
    enabled: ENTERPRISE_AVAILABLE,
    ssoEnabled: false,
    multiTenant: false,
    complianceMode: false
  }
};

function loadPluginConfigFile(app) {
  try {
    // Resolve plugin folder from app.vault.adapter if available; fallback to relative path
    const base = app?.vault?.adapter?.basePath || "";
    // Try to load config.json adjacent to main.js if user copied the template
    const path = require("path");
    const fs = require("fs");
    const here = __dirname;
    const candidate = path.join(here, "config.json");
    if (fs.existsSync(candidate)) {
      const raw = fs.readFileSync(candidate, "utf-8");
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
    contentEl.createEl("h2", { text: "AI Assistant" });
    contentEl.createEl("p", { text: "Ask your AI assistant a question or use voice input." });
    // Backend status and reload button
    const statusDiv = contentEl.createEl("div", { attr: { style: "margin-bottom: 10px;" } });
    await this.checkBackendStatus(statusDiv);
    const textarea = contentEl.createEl("textarea", { placeholder: "Type your question here...", attr: { rows: "4", style: "width: 100%; margin-bottom: 10px;" } });
    const askButton = contentEl.createEl("button", { text: "Ask AI" });
    askButton.onclick = async () => {
      new Notice("Feature not implemented.");
    };
    const closeButton = contentEl.createEl("button", { text: "Close" });
    closeButton.onclick = () => this.close();
  }

  async checkBackendStatus(statusDiv) {
    statusDiv.empty();
    let statusText = "Checking backend...";
    let offline = false;
    
    const backendClient = new BackendClient(this.plugin.settings.backendUrl);
    
    try {
      await backendClient.get("/status");
      statusText = "Backend is online";
    } catch (e) {
      statusText = "Backend is offline";
      offline = true;
    }
    statusDiv.createEl("span", { text: statusText });
    if (offline) {
      const reloadBtn = statusDiv.createEl("button", { text: "Reload" });
      reloadBtn.onclick = async () => {
        reloadBtn.disabled = true;
        reloadBtn.textContent = "Restarting...";
        // Attempt to restart backend using /restart endpoint
        try {
          await backendClient.post("/restart", {});
          new Notice("Restart command sent to backend.");
        } catch (err) {
          new Notice("Failed to restart backend. Please restart manually.");
        }
        reloadBtn.disabled = false;
        reloadBtn.textContent = "Reload";
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
    
    // Optional: overlay config.json values if present
    const external = loadPluginConfigFile(this.app);
    if (external && typeof external === "object") {
      this.settings = Object.assign({}, this.settings, external);
      await this.saveSettings();
    }
    
    // Initialize enterprise features if available
    if (ENTERPRISE_AVAILABLE && this.settings.enterprise?.enabled) {
      await this.initializeEnterpriseFeatures();
    }
    
    this.addRibbonIcon("bot", "AI Assistant", () => {
      // Open right pane instead of modal
      const pane = new AIRightPaneView(this.app, this);
      pane.open();
    });
    
    // Add enterprise admin ribbon if user has admin role
    if (this.enterpriseAuth && this.enterpriseAuth.hasRole('admin')) {
      this.addRibbonIcon("shield", "Enterprise Admin", () => {
        this.openEnterpriseAdmin();
      });
    }
    
    this.addSettingTab(new AIAssistantSettingTab(this.app, this));
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
      
      console.log("Enterprise features initialized successfully");
      new Notice("Enterprise features enabled");
      
    } catch (error) {
      console.error("Failed to initialize enterprise features:", error);
      new Notice("Failed to initialize enterprise features: " + error.message);
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
          this.addRibbonIcon("shield", "Enterprise Admin", () => {
            this.openEnterpriseAdmin();
          });
        }
        
      } else {
        console.log("User logged out");
        new Notice("Logged out successfully");
        
        // Update UI for unauthenticated state
        this.refreshUIForAuth();
      }
    } catch (error) {
      console.error("Authentication change handler failed:", error);
    }
  }

  refreshUIForAuth() {
    // Refresh any open views to reflect authentication state
    const rightPane = this.app.workspace.getLeavesOfType('ai-right-pane')[0];
    if (rightPane && rightPane.view) {
      rightPane.view.refresh();
    }
  }

  openEnterpriseAdmin() {
    try {
      if (!this.enterpriseAuth || !this.enterpriseAuth.isAuthenticated()) {
        new Notice("Please sign in to access admin features");
        return;
      }
      
      if (!this.enterpriseAuth.hasRole('admin')) {
        new Notice("Admin access required");
        return;
      }
      
      // Create admin modal
      const modal = new EnterpriseAdminModal(this.app, this);
      modal.open();
      
    } catch (error) {
      console.error("Failed to open enterprise admin:", error);
      new Notice("Failed to open admin dashboard: " + error.message);
    }
  }

  async onunload() {
    // Clean up enterprise features
    if (this.enterpriseAuth) {
      this.enterpriseAuth.destroy();
    }
    
    if (this.enterpriseAdmin) {
      this.enterpriseAdmin.destroy();
    }
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }
}

class EnterpriseAdminModal extends Modal {
  constructor(app, plugin) {
    super(app);
    this.plugin = plugin;
  }

  async onOpen() {
    const { contentEl } = this;
    contentEl.empty();
    
    contentEl.createEl("h2", { text: "Enterprise Admin Dashboard" });
    
    try {
      if (this.plugin.enterpriseAdmin) {
        await this.plugin.enterpriseAdmin.createDashboard(contentEl);
      } else {
        contentEl.createEl("p", { text: "Enterprise admin not available" });
      }
    } catch (error) {
      console.error("Failed to create admin dashboard:", error);
      contentEl.createEl("p", { 
        text: "Failed to load admin dashboard: " + error.message,
        cls: "error-message"
      });
    }
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
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
    containerEl.createEl("h2", { text: "AI Assistant Settings" });
    new Setting(containerEl)
      .setName("Backend URL")
      .setDesc("URL of your AI backend server")
      .addText((text) =>
        text
          .setValue(this.plugin.settings.backendUrl)
          .onChange(async (value) => {
            this.plugin.settings.backendUrl = value;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Enable Voice")
      .setDesc("Show voice features in UI")
      .addToggle((tgl) =>
        tgl
          .setValue(!!(this.plugin.settings.features?.enableVoice))
          .onChange(async (v) => {
            this.plugin.settings.features = this.plugin.settings.features || {};
            this.plugin.settings.features.enableVoice = v;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Allow Network (backend)")
      .setDesc("Hint to backend to allow outbound network features")
      .addToggle((tgl) =>
        tgl
          .setValue(!!(this.plugin.settings.features?.allowNetwork))
          .onChange(async (v) => {
            this.plugin.settings.features = this.plugin.settings.features || {};
            this.plugin.settings.features.allowNetwork = v;
            await this.plugin.saveSettings();
          })
      );

    // Enterprise Settings Section
    if (ENTERPRISE_AVAILABLE) {
      containerEl.createEl("h3", { text: "Enterprise Features" });
      
      new Setting(containerEl)
        .setName("Enable Enterprise Features")
        .setDesc("Enable advanced enterprise functionality")
        .addToggle((tgl) =>
          tgl
            .setValue(!!(this.plugin.settings.enterprise?.enabled))
            .onChange(async (v) => {
              this.plugin.settings.enterprise = this.plugin.settings.enterprise || {};
              this.plugin.settings.enterprise.enabled = v;
              await this.plugin.saveSettings();
              
              if (v && !this.plugin.enterpriseAuth) {
                await this.plugin.initializeEnterpriseFeatures();
              }
            })
        );

      if (this.plugin.settings.enterprise?.enabled) {
        // Enterprise Authentication
        const authSection = containerEl.createEl("div", { cls: "enterprise-auth-section" });
        
        if (this.plugin.enterpriseAuth && this.plugin.enterpriseAuth.isAuthenticated()) {
          const user = this.plugin.enterpriseAuth.getCurrentUser();
          const tenant = this.plugin.enterpriseAuth.getCurrentTenant();
          
          authSection.createEl("h4", { text: "Authentication Status" });
          authSection.createEl("p", { text: `Signed in as: ${user.email}` });
          authSection.createEl("p", { text: `Organization: ${tenant.name}` });
          
          const logoutBtn = authSection.createEl("button", { 
            text: "Sign Out",
            cls: "mod-warning"
          });
          logoutBtn.onclick = async () => {
            await this.plugin.enterpriseAuth.logout();
            this.display(); // Refresh settings
          };
          
          // Admin dashboard button
          if (this.plugin.enterpriseAuth.hasRole('admin')) {
            const adminBtn = authSection.createEl("button", { 
              text: "Open Admin Dashboard",
              cls: "mod-cta"
            });
            adminBtn.onclick = () => {
              this.plugin.openEnterpriseAdmin();
            };
          }
          
          // Configuration button
          const configBtn = authSection.createEl("button", { 
            text: "Enterprise Configuration"
          });
          configBtn.onclick = () => {
            this.openEnterpriseConfig();
          };
          
        } else {
          authSection.createEl("h4", { text: "Enterprise Sign In" });
          authSection.createEl("p", { 
            text: "Sign in with your organization's SSO provider to access enterprise features."
          });
          
          const loginBtn = authSection.createEl("button", { 
            text: "Sign In",
            cls: "mod-cta"
          });
          loginBtn.onclick = () => {
            this.openEnterpriseLogin();
          };
        }
        
        // Enterprise status
        const statusSection = containerEl.createEl("div", { cls: "enterprise-status" });
        statusSection.createEl("h4", { text: "Enterprise Status" });
        
        this.displayEnterpriseStatus(statusSection);
      }
    } else {
      containerEl.createEl("h3", { text: "Enterprise Features" });
      containerEl.createEl("p", { 
        text: "Enterprise features are not available in this build.",
        cls: "mod-warning"
      });
    }

    const controls = containerEl.createEl("div");
    const backendClient = new BackendClient(this.plugin.settings.backendUrl);
    
    const fetchBtn = controls.createEl("button", { text: "Fetch Backend Config" });
    fetchBtn.onclick = async () => {
      try {
        const cfg = await backendClient.get("/api/config");
        new Notice("Config loaded: api_port=" + cfg.api_port);
      } catch (error) {
        new Notice("Failed to fetch backend config: " + error.message);
      }
    };
    
    const reloadBtn = controls.createEl("button", { text: "Reload Backend Config" });
    reloadBtn.onclick = async () => {
      try {
        await backendClient.post("/api/config/reload", {});
        new Notice("Backend config reloaded");
      } catch (error) {
        new Notice("Reload failed: " + error.message);
      }
    };

    const saveBtn = controls.createEl("button", { text: "Save to Backend" });
    saveBtn.onclick = async () => {
      try {
        const updates = {
          allow_network: !!(this.plugin.settings.features && this.plugin.settings.features.allowNetwork),
        };
        await backendClient.post("/api/config", updates);
        
        // Reload backend config to apply
        await backendClient.post("/api/config/reload", {});
        new Notice("Backend settings saved and reloaded");
      } catch (error) {
        new Notice("Failed to save/reload backend config: " + error.message);
      }
    };
  }

  openEnterpriseLogin() {
    try {
      const modal = new EnterpriseLoginModal(this.app, this.plugin);
      modal.open();
    } catch (error) {
      console.error("Failed to open enterprise login:", error);
      new Notice("Failed to open enterprise login: " + error.message);
    }
  }

  openEnterpriseConfig() {
    try {
      const modal = new EnterpriseConfigModal(this.app, this.plugin);
      modal.open();
    } catch (error) {
      console.error("Failed to open enterprise config:", error);
      new Notice("Failed to open enterprise configuration: " + error.message);
    }
  }

  async displayEnterpriseStatus(containerEl) {
    containerEl.empty();
    
    try {
      if (this.plugin.backendClient) {
        const response = await this.plugin.backendClient.request('/api/enterprise/status', {
          method: 'GET'
        });
        
        if (response.ok) {
          const status = response.data;
          
          if (status.enterprise_enabled) {
            containerEl.createEl("p", { 
              text: "✅ Enterprise backend available",
              cls: "mod-success"
            });
            
            const featuresEl = containerEl.createEl("div", { cls: "enterprise-features" });
            featuresEl.createEl("p", { text: "Available features:" });
            
            const featuresList = featuresEl.createEl("ul");
            Object.entries(status.features).forEach(([feature, enabled]) => {
              const item = featuresList.createEl("li");
              item.textContent = `${enabled ? '✅' : '❌'} ${feature.replace(/_/g, ' ').toUpperCase()}`;
            });
            
          } else {
            containerEl.createEl("p", { 
              text: "❌ Enterprise features not enabled on backend",
              cls: "mod-warning"
            });
          }
        } else {
          containerEl.createEl("p", { 
            text: "⚠️ Cannot connect to enterprise backend",
            cls: "mod-warning"
          });
        }
      }
    } catch (error) {
      containerEl.createEl("p", { 
        text: "❌ Enterprise backend unavailable",
        cls: "mod-warning"
      });
    }
  }
}

class EnterpriseLoginModal extends Modal {
  constructor(app, plugin) {
    super(app);
    this.plugin = plugin;
  }

  async onOpen() {
    const { contentEl } = this;
    contentEl.empty();
    
    contentEl.createEl("h2", { text: "Enterprise Sign In" });
    
    try {
      if (this.plugin.enterpriseAuth) {
        this.plugin.enterpriseAuth.createLoginInterface(contentEl);
      } else {
        contentEl.createEl("p", { text: "Enterprise authentication not available" });
      }
    } catch (error) {
      console.error("Failed to create login interface:", error);
      contentEl.createEl("p", { 
        text: "Failed to load login interface: " + error.message,
        cls: "error-message"
      });
    }
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}

class EnterpriseConfigModal extends Modal {
  constructor(app, plugin) {
    super(app);
    this.plugin = plugin;
  }

  async onOpen() {
    const { contentEl } = this;
    contentEl.empty();
    
    contentEl.createEl("h2", { text: "Enterprise Configuration" });
    
    try {
      if (this.plugin.enterpriseConfig) {
        this.plugin.enterpriseConfig.createConfigurationInterface(contentEl);
      } else {
        contentEl.createEl("p", { text: "Enterprise configuration not available" });
      }
    } catch (error) {
      console.error("Failed to create config interface:", error);
      contentEl.createEl("p", { 
        text: "Failed to load configuration interface: " + error.message,
        cls: "error-message"
      });
    }
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}

module.exports = ObsidianAIAssistant;