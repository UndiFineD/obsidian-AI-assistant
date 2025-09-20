import { App, Plugin, PluginSettingTab, Setting } from 'obsidian';
import { TaskQueue } from './taskQueue';
import { VoiceInput } from './voiceInput';
import { AnalyticsPane, ANALYTICS_VIEW_TYPE } from './analyticsPane';


interface LLMPluginSettings {
    backendUrl: string;
    vaultPath: string;
    preferFast: boolean;
}

const DEFAULT_SETTINGS: LLMPluginSettings = {
    backendUrl: "http://localhost:8000",
    vaultPath: "",
    preferFast: true
};

export default class ObsidianLLMPlugin extends Plugin {
    settings: LLMPluginSettings;
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
