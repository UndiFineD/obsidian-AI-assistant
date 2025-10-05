const { Plugin, Modal, Notice, PluginSettingTab, Setting } = require("obsidian");

const DEFAULT_SETTINGS = {
  backendUrl: "http://localhost:8000",
  features: { enableVoice: true, allowNetwork: false },
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
    try {
      const res = await fetch(this.plugin.settings.backendUrl + "/status", { method: "GET" });
      if (res.ok) {
        statusText = "Backend is online";
      } else {
        statusText = "Backend is offline";
        offline = true;
      }
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
          await fetch(this.plugin.settings.backendUrl + "/restart", { method: "POST" });
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
    // Optional: overlay config.json values if present
    const external = loadPluginConfigFile(this.app);
    if (external && typeof external === "object") {
      this.settings = Object.assign({}, this.settings, external);
      await this.saveSettings();
    }
    this.addRibbonIcon("bot", "AI Assistant", () => {
      new AIModal(this.app, this).open();
    });
    this.addSettingTab(new AIAssistantSettingTab(this.app, this));
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
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

    const controls = containerEl.createEl("div");
    const fetchBtn = controls.createEl("button", { text: "Fetch Backend Config" });
    fetchBtn.onclick = async () => {
      try {
        const res = await fetch(this.plugin.settings.backendUrl + "/api/config");
        if (res.ok) {
          const cfg = await res.json();
          new Notice("Config loaded: api_port=" + cfg.api_port);
        } else {
          new Notice("Failed to fetch backend config");
        }
      } catch (_) {
        new Notice("Failed to reach backend");
      }
    };
    const reloadBtn = controls.createEl("button", { text: "Reload Backend Config" });
    reloadBtn.onclick = async () => {
      try {
        const res = await fetch(this.plugin.settings.backendUrl + "/api/config/reload", { method: "POST" });
        if (res.ok) new Notice("Backend config reloaded");
        else new Notice("Reload failed");
      } catch (_) {
        new Notice("Failed to reach backend");
      }
    };

    const saveBtn = controls.createEl("button", { text: "Save to Backend" });
    saveBtn.onclick = async () => {
      try {
        const updates = {
          allow_network: !!(this.plugin.settings.features && this.plugin.settings.features.allowNetwork),
        };
        const res = await fetch(this.plugin.settings.backendUrl + "/api/config", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(updates),
        });
        if (!res.ok) {
          new Notice("Failed to save config to backend");
          return;
        }
        // Reload backend config to apply
        await fetch(this.plugin.settings.backendUrl + "/api/config/reload", { method: "POST" });
        new Notice("Backend settings saved and reloaded");
      } catch (_) {
        new Notice("Failed to reach backend");
      }
    };
  }
}

module.exports = ObsidianAIAssistant;