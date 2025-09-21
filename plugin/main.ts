import {
	App,
	Modal,
	Notice,
	Plugin,
	PluginSettingTab,
	Setting,
	TFile,
	ItemView,
	WorkspaceLeaf
} from "obsidian";

import { TaskQueue, VIEW_TYPE_TASK_QUEUE, TaskQueueView } from "./taskQueue";

import { 
	AnalyticsPane
	AnalyticsState, 
	AnalyticsView, 
	ANALYTICS_VIEW_TYPE, 
	QAEntry, 
	NoteAnalytics 
} from "./analyticsPane";

import { VoiceRecorder } from "./voice";

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
// Task Queue Manager
// ----------------------------
class TaskQueue {
  tasks: Task[] = [];
  listeners: (() => void)[] = [];

  addTask(task: Task) {
    this.tasks.push(task);
    this.notify();
  }

  updateTask(id: string, updates: Partial<Task>) {
    const t = this.tasks.find(t => t.id === id);
    if (t) Object.assign(t, updates);
    this.notify();
  }

  filterTasks(query: string, status?: string) {
    return this.tasks.filter(t => {
      const matchesQuery = query
        ? t.prompt.toLowerCase().includes(query.toLowerCase())
        : true;
      const matchesStatus = status ? t.status === status : true;
      return matchesQuery && matchesStatus;
	  
// ----------------------------
// Assistant Plugin
// ----------------------------	  
export default class AssistantPlugin extends Plugin {
  settings: AssistantSettings;
  queue: TaskQueue;
  analytics: AnalyticsState;
  voice: VoiceRecorder;

  async onload() {
    await this.loadSettings();
    this.queue = new TaskQueue(this.settings.backendUrl, this);
    this.analytics = (await this.loadData()).analytics || { processedNotes: {}, qaHistory: [], modelUsage: {} };
    this.voice = new VoiceRecorder();

    // Register the task queue view
    this.registerView(
      VIEW_TYPE_TASK_QUEUE,
      (leaf: WorkspaceLeaf) => new TaskQueueView(leaf, this.queue, this.analytics)
    );
    this.addCommand({
      id: "open-task-queue-view",
      name: "Open Task Queue View",
      callback: () => this.activateTaskQueueView(),
    });
    this.addRibbonIcon("list-checks", "Task Queue", () => this.activateTaskQueueView());

    // Register the analytics dashboard view
    this.registerView(
      VIEW_TYPE_ANALYTICS,
      (leaf: WorkspaceLeaf) => new AnalyticsView(leaf, this.analytics)
    );
    this.addCommand({
      id: "open-analytics-dashboard",
      name: "Open Analytics Dashboard",
      callback: () => this.activateAnalyticsView(),
    });
    this.addRibbonIcon("bar-chart", "Analytics Dashboard", () => this.activateAnalyticsView());

    // Voice Input Ribbon
    this.addRibbonIcon("mic", "Voice Ask", async () => {
      await this.voice.startRecording();
      new Notice("🎙️ Voice recording started. Click the stop icon in ribbon to finish.");

      // Add a temporary stop icon/button
      const stopIcon = this.addRibbonIcon("square", "Stop Recording", async () => {
        const audioBlob = await this.voice.stopRecording();
        const transcription = await this.voice.sendToBackend(audioBlob, this.settings.backendUrl, this.settings.voiceMode);

        if (transcription && transcription.trim().length > 0) {
          new Notice(`📝 Transcribed: ${transcription}`);
          // Send to /api/ask
          try {
            const resp = await fetch(`${this.settings.backendUrl}/api/ask`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ question: transcription, prefer_fast: this.settings.preferFastModel }),
            });
            const data = await resp.json();
            this.trackQA(transcription, data.answer, this.settings.preferFastModel ? "fast" : "deep");
            new Notice("Assistant answered. See output in console or note (depending on your setup).");
          } catch (err) {
            new Notice("Error sending voice transcription to backend: " + err);
          }
        } else {
          new Notice("Transcription was empty.");
        }

        // Remove stop icon to avoid accumulation
        stopIcon.remove();
      });
    });

    // Settings Tab
    this.addSettingTab(new AssistantSettingTab(this.app, this));

    this.log("AssistantPlugin loaded with settings:", this.settings);
  }

  onunload() {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_TASK_QUEUE);
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_ANALYTICS);
  }

  async activateTaskQueueView() {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_TASK_QUEUE);
    await this.app.workspace.getRightLeaf(false).setViewState({
      type: VIEW_TYPE_TASK_QUEUE,
      active: true,
    });
    this.app.workspace.revealLeaf(this.app.workspace.getLeavesOfType(VIEW_TYPE_TASK_QUEUE)[0]);
  }

  async activateAnalyticsView() {
    this.app.workspace.detachLeavesOfType(VIEW_TYPE_ANALYTICS);
    await this.app.workspace.getRightLeaf(false).setViewState({
      type: VIEW_TYPE_ANALYTICS,
      active: true,
    });
    this.app.workspace.revealLeaf(this.app.workspace.getLeavesOfType(VIEW_TYPE_ANALYTICS)[0]);
  }

  // Analytics tracking
  trackQA(prompt: string, answer: string, model: string) {
    const entry = {
      timestamp: Date.now(),
      prompt,
      answer
    };
    this.analytics.qaHistory.push(entry);
    this.analytics.modelUsage[model] = (this.analytics.modelUsage[model] || 0) + 1;
    await this.saveAnalytics();
  }

  async saveAnalytics() {
    await this.saveData({ settings: this.settings, analytics: this.analytics });
  }

  async loadSettings() {
    const loaded = await this.loadData();
    this.settings = Object.assign({}, DEFAULT_SETTINGS, loaded.settings || {});
  }

  async saveSettings() {
    await this.saveData({ settings: this.settings, analytics: this.analytics });
  }
}

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
      .addText(text =>
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
      .addText(text =>
        text
          .setValue(this.plugin.settings.vaultPath)
          .onChange(async (v) => {
            this.plugin.settings.vaultPath = v;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Prefer Fast Model")
      .setDesc("Use lightweight/fast model (e.g. LLaMA) vs deeper model (e.g. GPT4All)")
      .addToggle(toggle =>
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
      .addDropdown(dd =>
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
