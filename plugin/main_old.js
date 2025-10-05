const { App, Modal, Notice, Plugin, PluginSettingTab, Setting } = require("obsidian");

// Default settings for the plugin
const DEFAULT_SETTINGS = {
  backendUrl: "http://localhost:8000",
  apiTimeout: 10000
};

// Simple modal for AI interaction
class AIModal extends Modal {
  constructor(app, plugin) {
    super(app);
    this.plugin = plugin;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.empty();

    contentEl.createEl("h2", { text: "AI Assistant" });

    const inputContainer = contentEl.createDiv();
    const textarea = inputContainer.createEl("textarea", {
      placeholder: "Ask your AI assistant a question...",
      attr: { rows: "4", style: "width: 100%; margin-bottom: 10px;" }
    });

    const buttonContainer = contentEl.createDiv();
    const askButton = buttonContainer.createEl("button", { text: "Ask AI" });
    const closeButton = buttonContainer.createEl("button", { text: "Close" });
    closeButton.style.marginLeft = "10px";

    askButton.onclick = async () => {
      const question = textarea.value.trim();
      if (!question) {
        new Notice("Please enter a question");
        return;
      }

      askButton.disabled = true;
      askButton.textContent = "Processing...";

      try {
        await this.plugin.askAI(question);
      } finally {
        askButton.disabled = false;
        askButton.textContent = "Ask AI";
        this.close();
      }
    };

    closeButton.onclick = () => this.close();
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}

// Main Plugin Class
class ObsidianAIAssistant extends Plugin {

  async onload() {
    console.log('Loading Obsidian AI Assistant Plugin');
    
    // Load settings
    await this.loadSettings();

    // Add ribbon icon
    this.addRibbonIcon('brain', 'AI Assistant', () => {
      new AIModal(this.app, this).open();
    });

    // Add command to command palette
    this.addCommand({
      id: 'open-ai-assistant',
      name: 'Open AI Assistant',
      callback: () => {
        new AIModal(this.app, this).open();
      }
    });

    // Add another command for quick ask
    this.addCommand({
      id: 'ask-ai-about-selection',
      name: 'Ask AI about selected text',
      editorCallback: async (editor) => {
        const selectedText = editor.getSelection();
        if (selectedText) {
          await this.askAI(`Explain this text: ${selectedText}`);
        } else {
          new Notice('No text selected');
        }
      }
    });

    // Add settings tab
    this.addSettingTab(new AIAssistantSettingTab(this.app, this));

    new Notice('AI Assistant Plugin loaded successfully!');
  }

  onunload() {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_TASK_QUEUE);
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_ANALYTICS);
  }

  // ----------------------------
  // View Activation
  // ----------------------------
  async activateTaskQueueView() {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_TASK_QUEUE);
    const leaf = this.app.workspace.getRightLeaf(false);
    await leaf.setViewState({ type: VIEW_TYPE_TASK_QUEUE, active: true });
    this.app.workspace.revealLeaf(
      this.app.workspace.getLeavesOfType(VIEW_TYPE_TASK_QUEUE)[0]
    );
  }

  async activateAnalyticsView() {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_ANALYTICS);
    const leaf = this.app.workspace.getRightLeaf(false);
    await leaf.setViewState({ type: VIEW_TYPE_ANALYTICS, active: true });
    this.app.workspace.revealLeaf(
      this.app.workspace.getLeavesOfType(VIEW_TYPE_ANALYTICS)[0]
    );
  }

  // ----------------------------
  // Analytics Tracking
  // ----------------------------
  trackQA(prompt, answer, model) {
    const entry = {
      timestamp: Date.now(),
      prompt,
      answer,
    };
    this.analytics.qaHistory.push(entry);
    this.analytics.modelUsage[model] = (this.analytics.modelUsage[model] || 0) + 1;
    this.saveAnalytics();
  }

  async saveAnalytics() {
    await this.saveData({ settings: this.settings, analytics: this.analytics });
  }

  // ----------------------------
  // Settings
  // ----------------------------
  async loadSettings() {
    const loaded = await this.loadData();
    this.settings = Object.assign({}, DEFAULT_SETTINGS, loaded.settings || {});
  }

  async saveSettings() {
    await this.saveData({ settings: this.settings, analytics: this.analytics });
  }
}

// ----------------------------
// Settings Tab
// ----------------------------
class AssistantSettingTab extends PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "Assistant Settings" });

    new Setting(containerEl)
      .setName("Backend URL")
      .setDesc("URL of backend server for AI assistant")
      .addText((text) =>
        text
          .setValue(this.plugin.settings.backendUrl)
          .onChange(async (v) => {
            this.plugin.settings.backendUrl = v;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Vault Path")
      .setDesc("Path to your vault for backend indexing")
      .addText((text) =>
        text
          .setValue(this.plugin.settings.vaultPath)
          .onChange(async (v) => {
            this.plugin.settings.vaultPath = v;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Prefer Fast Model")
      .setDesc("Use lightweight/fast model vs deeper model")
      .addToggle((toggle) =>
        toggle
          .setValue(this.plugin.settings.preferFastModel)
          .onChange(async (v) => {
            this.plugin.settings.preferFastModel = v;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Voice Mode")
      .setDesc("Offline (Vosk) or Online (Whisper/API) transcription")
      .addDropdown((dd) =>
        dd
          .addOption("offline", "Offline (Vosk)")
          .addOption("online", "Online")
          .setValue(this.plugin.settings.voiceMode)
          .onChange(async (v) => {
            this.plugin.settings.voiceMode = v;
            await this.plugin.saveSettings();
          })
      );
  }
}

module.exports = AssistantPlugin;