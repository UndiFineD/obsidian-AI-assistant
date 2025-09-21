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

import { TaskQueue } from './taskQueue';
import { VoiceInput } from './voiceInput';

import { 
	AnalyticsPane
	AnalyticsState, 
	AnalyticsView, 
	ANALYTICS_VIEW_TYPE, 
	QAEntry, 
	NoteAnalytics 
} from "./analyticsPane";


// ----------------------------
// Types
// ----------------------------
interface Task {
  id: string;
  file: string;
  prompt: string;
  priority: number;
  status: "pending" | "processing" | "done" | "rejected";
  suggestion?: string;
}

interface AssistantSettings {
  backendUrl: string;
  vaultPath: string;
  preferFastModel: boolean;
  defaultPriority: number;
}


const DEFAULT_SETTINGS: AssistantSettings = {
    backendUrl: "http://localhost:8000",
    vaultPath: "",
    preferFastModel: true,
	defaultPriority: 1
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
    });
  }

  batchProcess(ids: string[], fn: (task: Task) => void) {
    ids.forEach(id => {
      const t = this.tasks.find(t => t.id === id);
      if (t) fn(t);
    });
    this.notify();
  }

  onChange(listener: () => void) {
    this.listeners.push(listener);
  }

  notify() {
    this.listeners.forEach(l => l());
  }
}

// ----------------------------
// Task Queue View
// ----------------------------
const VIEW_TYPE_QUEUE = "assistant-queue-view";

class QueueView extends ItemView {
  queue: TaskQueue;

  constructor(leaf: WorkspaceLeaf, queue: TaskQueue) {
    super(leaf);
    this.queue = queue;
    this.queue.onChange(() => this.redraw());
  }

  getViewType() {
    return VIEW_TYPE_QUEUE;
  }

  getDisplayText() {
    return "Assistant Task Queue";
  }

  async onOpen() {
    this.redraw();
  }

  redraw() {
    const container = this.containerEl.children[1];
    container.empty();

    const searchBox = container.createEl("input", { type: "text", placeholder: "Search tasks…" });
    const listEl = container.createEl("div", { cls: "task-list" });

    const renderTasks = () => {
      listEl.empty();
      const tasks = this.queue.filterTasks(searchBox.value);
      for (const task of tasks) {
        const item = listEl.createEl("div", { cls: "task-item" });
        item.createEl("span", { text: `[${task.priority}] ${task.prompt}` });

        if (task.suggestion) {
          const preview = item.createEl("blockquote", { text: task.suggestion });
          const acceptBtn = item.createEl("button", { text: "Accept" });
          const rejectBtn = item.createEl("button", { text: "Reject" });

          acceptBtn.onclick = () => {
            this.queue.updateTask(task.id, { status: "done" });
            new Notice("Suggestion accepted");
          };
          rejectBtn.onclick = () => {
            this.queue.updateTask(task.id, { status: "rejected" });
            new Notice("Suggestion rejected");
          };
        }
      }
    };

    renderTasks();
    searchBox.oninput = renderTasks;
  }
}

// ----------------------------
// Plugin
// ----------------------------
export default class AssistantPlugin extends Plugin {
	settings: AssistantSettings;
	queue: TaskQueue = new TaskQueue();
	analytics: AnalyticsState = { 
		processedNotes: {}, 
		qaHistory: [], 
		modelUsage: {} 
	};

	async onload() {
		console.log("Loading Obsidian AI Assistant…");
		await this.loadSettings();
		const saved = await this.loadData();
		if (saved?.analytics) this.analytics = saved.analytics;

		// Ribbon buttons
		this.addRibbonIcon("bot", "Ask Assistant", () => {
			this.promptUser();
		});

		this.addRibbonIcon("mic", "Voice Input", () => {
			new Notice("Voice input not implemented yet");
		});

		this.addRibbonIcon("play", "Process Queue", () => {
			this.processQueue();
		});

		// Queue view
		this.registerView(
			VIEW_TYPE_QUEUE,
			(leaf) => new QueueView(leaf, this.queue)
		);

		this.addCommand({
			id: "open-queue-view",
			name: "Open Task Queue",
			callback: () => {
				this.activateQueueView();
			}
		});

		// Settings tab
		this.addSettingTab(new AssistantSettingTab(this.app, this));
	}

	onunload() {
		this.app.workspace.detachLeavesOfType(VIEW_TYPE_QUEUE);
	}

	async activateQueueView() {
		this.app.workspace.detachLeavesOfType(VIEW_TYPE_QUEUE);
		await this.app.workspace.getRightLeaf(false).setViewState({
			type: VIEW_TYPE_QUEUE,
			active: true,
		});
		this.app.workspace.revealLeaf(
			this.app.workspace.getLeavesOfType(VIEW_TYPE_QUEUE)[0]
		);
	}

	async promptUser() {
		const modal = new PromptModal(this.app, async (prompt) => {
			const id = crypto.randomUUID();
			this.queue.addTask({
				id,
				file: "ad-hoc",
				prompt,
				priority: this.settings.defaultPriority,
				status: "pending",
			});

			new Notice("Task added to queue");
			await this.queryBackend(id, prompt);
		});
		modal.open();
	}

  async queryBackend(id: string, prompt: string) {
    try {
      const resp = await fetch(`${this.settings.backendUrl}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
      });
      const data = await resp.json();
      this.queue.updateTask(id, { status: "done", suggestion: data.answer });
    } catch (e) {
      new Notice("Backend request failed");
    }
  }

  async processQueue() {
    const pending = this.queue.tasks.filter(t => t.status === "pending");
    for (const task of pending) {
      this.queue.updateTask(task.id, { status: "processing" });
      await this.queryBackend(task.id, task.prompt);
    }
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }
}

// ----------------------------
// Prompt Modal
// ----------------------------
class PromptModal extends Modal {
  onSubmit: (prompt: string) => void;

  constructor(app: App, onSubmit: (prompt: string) => void) {
    super(app);
    this.onSubmit = onSubmit;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.createEl("h2", { text: "Ask the Assistant" });
    const input = contentEl.createEl("textarea");
    input.rows = 4;

    contentEl.createEl("button", { text: "Submit" }, (btn) =>
      btn.onclick = () => {
        this.onSubmit(input.value);
        this.close();
      }
    );
  }

  onClose() {
    this.contentEl.empty();
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
    containerEl.createEl("h2", { text: "AI Assistant Settings" });

    new Setting(containerEl)
      .setName("Backend URL")
      .setDesc("FastAPI backend endpoint")
      .addText((text) =>
        text
          .setValue(this.plugin.settings.backendUrl)
          .onChange(async (value) => {
            this.plugin.settings.backendUrl = value;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Vault Path")
      .setDesc("Path to vault (for backend indexing)")
      .addText((text) =>
        text
          .setValue(this.plugin.settings.vaultPath)
          .onChange(async (value) => {
            this.plugin.settings.vaultPath = value;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Prefer Fast Model")
      .setDesc("Use fast (LLaMA) over deep (GPT4All)")
      .addToggle((toggle) =>
        toggle
          .setValue(this.plugin.settings.preferFastModel)
          .onChange(async (value) => {
            this.plugin.settings.preferFastModel = value;
            await this.plugin.saveSettings();
          })
      );

    new Setting(containerEl)
      .setName("Default Task Priority")
      .setDesc("Priority for new tasks")
      .addText((text) =>
        text
          .setValue(String(this.plugin.settings.defaultPriority))
          .onChange(async (value) => {
            this.plugin.settings.defaultPriority = parseInt(value) || 1;
            await this.plugin.saveSettings();
          })
      );
  }
}


export default class ObsidianLLMPlugin extends Plugin {
    settings: AssistantSettings;
    taskQueue: TaskQueue;
    voiceInput: VoiceInput;

    async onload() {
        await this.loadSettings();

        // Ribbon Buttons
        this.addRibbonIcon('dice', 'Ask Question', async () => {
            const question = await this.promptUser("Enter your question:");
            if (question) this.taskQueue.addTask({type: 'ask', content: question});
        });

        this.addRibbonIcon('play', 'Start Queue', async () => {
            this.taskQueue.startQueue();
        });

        this.addRibbonIcon('stop', 'Pause Queue', async () => {
            this.taskQueue.pauseQueue();
        });

        // Task Queue Pane
        this.taskQueue = new TaskQueue(this.settings.backendUrl, this.app);
        this.voiceInput = new VoiceInput(this.taskQueue);

        // Settings Tab
        this.addSettingTab(new LLMSettingTab(this.app, this));
		
		// Inside onload()
		this.addRibbonIcon('chart-bar', 'Show Analytics', async () => {
			const leaf = this.app.workspace.getLeaf(true);
			await leaf.setViewState({
				type: ANALYTICS_VIEW_TYPE, active: true
			});
		});
		this.registerView(
			ANALYTICS_VIEW_TYPE,
			(leaf) => new AnalyticsPane(leaf)
		);
    }

    async promptUser(promptText: string): Promise<string | null> {
        return new Promise((resolve) => {
            const result = window.prompt(promptText);
            resolve(result);
        });
    }

    async loadSettings() {
        this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() {
        await this.saveData(this.settings);
    }
}

class LLMSettingTab extends PluginSettingTab {
    plugin: ObsidianLLMPlugin;

    constructor(app: App, plugin: ObsidianLLMPlugin) {
        super(app, plugin);
        this.plugin = plugin;
    }

    display(): void {
        const { containerEl } = this;
        containerEl.empty();

        containerEl.createEl('h2', { text: 'LLM Plugin Settings' });

        new Setting(containerEl)
            .setName('Backend URL')
            .setDesc('URL for your FastAPI backend')
            .addText(text => text
                .setPlaceholder('http://localhost:8000')
                .setValue(this.plugin.settings.backendUrl)
                .onChange(async (value) => {
                    this.plugin.settings.backendUrl = value;
                    await this.plugin.saveSettings();
                })
            );

        new Setting(containerEl)
            .setName('Vault Path')
            .setDesc('Path to your vault for scanning')
            .addText(text => text
                .setPlaceholder('/path/to/vault')
                .setValue(this.plugin.settings.vaultPath)
                .onChange(async (value) => {
                    this.plugin.settings.vaultPath = value;
                    await this.plugin.saveSettings();
                })
            );

        new Setting(containerEl)
            .setName('Prefer Fast LLM')
            .setDesc('Use LLaMA for fast queries (otherwise GPT4All)')
            .addToggle(toggle => toggle
                .setValue(this.plugin.settings.preferFast)
                .onChange(async (value) => {
                    this.plugin.settings.preferFast = value;
                    await this.plugin.saveSettings();
                })
            );
    }
}
