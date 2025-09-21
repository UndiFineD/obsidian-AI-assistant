import {
  App,
  Modal,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  TFile,
  WorkspaceLeaf
} from "obsidian";

import { TaskQueue, VIEW_TYPE_TASK_QUEUE, TaskQueueView } from "./taskQueue";
import { AnalyticsView, AnalyticsState, VIEW_TYPE_ANALYTICS } from "./analyticsPane";
import { VoiceRecorder } from "./voice";

// ----------------------------
// Plugin Settings
// ----------------------------
interface AssistantSettings {
  backendUrl: string;
  vaultPath: string;
  preferFastModel: boolean;
  voiceMode: "offline" | "online";
}

const DEFAULT_SETTINGS: AssistantSettings = {
  backendUrl: "http://localhost:8000",
  vaultPath: "",
  preferFastModel: true,
  voiceMode: "offline",
};

// ----------------------------
// Main Plugin Class
// ----------------------------
export default class AssistantPlugin extends Plugin {
  settings: AssistantSettings;
  queue: TaskQueue;
  analytics: AnalyticsState;
  voice: VoiceRecorder;

  async onload() {
    await this.loadSettings();

    // Initialize Task Queue
    this.queue = new TaskQueue(this.settings.backendUrl, this.app);

    // Initialize Analytics State
    this.analytics = {
      processedNotes: {},
      qaHistory: [],
      modelUsage: {},
    };

    // Initialize Voice Recorder
    this.voice = new VoiceRecorder();

    // ----------------------------
    // Register Task Queue View
    // ----------------------------
    this.registerView(VIEW_TYPE_TASK_QUEUE, (leaf: WorkspaceLeaf) =>
      new TaskQueueView(leaf, this.queue, this.analytics)
    );

    this.addCommand({
      id: "open-task-queue-view",
      name: "Open Task Queue View",
      callback: () => this.activateTaskQueueView(),
    });

    this.addRibbonIcon("list-checks", "Task Queue", () => this.activateTaskQueueView());

    // ----------------------------
    // Register Analytics View
    // ----------------------------
    this.registerView(VIEW_TYPE_ANALYTICS, (leaf: WorkspaceLeaf) =>
      new AnalyticsView(leaf, this.analytics)
    );

    this.addCommand({
      id: "open-analytics-dashboard",
      name: "Open Analytics Dashboard",
      callback: () => this.activateAnalyticsView(),
    });

    this.addRibbonIcon("bar-chart", "Analytics Dashboard", () => this.activateAnalyticsView());

    // ----------------------------
    // Voice Input Ribbon
    // ----------------------------
    this.addRibbonIcon("mic", "Voice Ask", async () => {
      await this.voice.startRecording();
      new Notice("🎙️ Voice recording started. Click stop to finish.");

      // Temporary stop icon
      const stopIcon = this.addRibbonIcon("square", "Stop Recording", async () => {
        const audioBlob = await this.voice.stopRecording();
        const transcription = await this.voice.sendToBackend(
          audioBlob,
          this.settings.backendUrl,
          this.settings.voiceMode
        );

        if (transcription && transcription.trim().length > 0) {
          new Notice(`📝 Transcribed: ${transcription}`);

          try {
            const resp = await fetch(`${this.settings.backendUrl}/api/ask`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                question: transcription,
                prefer_fast: this.settings.preferFastModel,
              }),
            });
            const data = await resp.json();

            this.trackQA(
              transcription,
              data.answer,
              this.settings.preferFastModel ? "fast" : "deep"
            );

            new Notice("Assistant answered. See analytics dashboard for details.");
          } catch (err) {
            new Notice("Error sending transcription to backend: " + err);
          }
        } else {
          new Notice("Transcription was empty.");
        }

        stopIcon.remove();
      });
    });

    // ----------------------------
    // Settings Tab
    // ----------------------------
    this.addSettingTab(new AssistantSettingTab(this.app, this));
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
  trackQA(prompt: string, answer: string, model: string) {
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
  plugin: AssistantPlugin;

  constructor(app: App, plugin: AssistantPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
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
            this.plugin.settings.voiceMode = v as "offline" | "online";
            await this.plugin.saveSettings();
          })
      );
  }
}
