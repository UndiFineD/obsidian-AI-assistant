const { Plugin, Modal, Notice, PluginSettingTab, Setting } = require("obsidian");

const DEFAULT_SETTINGS = {
  backendUrl: "http://localhost:8000"
};

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
  }
}

module.exports = ObsidianAIAssistant;