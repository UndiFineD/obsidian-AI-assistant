import { ItemView, WorkspaceLeaf, Workspace, Notice } from 'obsidian';

export const ANALYTICS_VIEW_TYPE = "AI-analytics";

export class AnalyticsPane extends ItemView {
    constructor(leaf: WorkspaceLeaf) {
        super(leaf);
    }

    getViewType(): string {
        return ANALYTICS_VIEW_TYPE;
    }

    getDisplayText(): string {
        return "AI Analytics";
    }

	async onOpen() {
		this.redraw();
	}
    
    async onClose() {
        // Cleanup if needed
    }
	
	export interface QAEntry {
		timestamp: number;
		prompt: string;
		answer: string;
	}
	
	export interface NoteAnalytics {
		file: string;
		processed: number;
		summary: string;
		inVaultLinks: string[];
		externalLinks: string[];
	}
	
	export interface AnalyticsState {
		processedNotes: Record<string, NoteAnalytics>;
		qaHistory: QAEntry[];
		modelUsage: Record<string, number>;
	}

	export class AnalyticsView extends ItemView {
		state: AnalyticsState;

		constructor(leaf: WorkspaceLeaf, state: AnalyticsState) {
			super(leaf);
			this.state = state;
		}

		getViewType() {
			return VIEW_TYPE_ANALYTICS;
		}

		getDisplayText() {
			return "AI Analytics Dashboard";
		}
	}
	
	redraw() {
		const container = this.containerEl.children[1];
		container.empty();

		container.createEl("h2", { text: "Assistant Analytics" });

		// Global stats
		const processedCount = Object.values(this.state.processedNotes).length;
		const qaCount = this.state.qaHistory.length;

		container.createEl("p", { text: `Processed notes: ${processedCount}` });
		container.createEl("p", { text: `QA interactions: ${qaCount}` });

		// Model usage stats
		container.createEl("h3", { text: "Model Usage" });
		const modelList = container.createEl("ul");
		Object.entries(this.state.modelUsage).forEach(([model, count]) => {
			modelList.createEl("li", { text: `${model}: ${count} calls` });
		});

		// QA history preview
		container.createEl("h3", { text: "Recent Q&A" });
		const qaList = container.createEl("ul");
		this.state.qaHistory.slice(-10).forEach((entry) => {
			qaList.createEl("li", {
				text: `[${new Date(entry.timestamp).toLocaleString()}] ${entry.prompt} → ${entry.answer.slice(0, 50)}...`
			});
		});

		// Per-note summaries
		container.createEl("h3", { text: "Notes Summary" });
		const notesDiv = container.createEl("div", { cls: "notes-summary" });
		for (const note of Object.values(this.state.processedNotes)) {
			const box = notesDiv.createEl("div", { cls: "note-box" });
			box.createEl("h4", { text: note.file });
			box.createEl("p", { text: `Processed: ${note.processed} times` });
			box.createEl("p", { text: note.summary || "No summary yet." });

			if (note.inVaultLinks.length) {
				box.createEl("p", { text: `Links (vault): ${note.inVaultLinks.join(", ")}` });
			}
			if (note.externalLinks.length) {
				box.createEl("p", { text: `Links (external): ${note.externalLinks.join(", ")}` });
			}
		}
	}
}
