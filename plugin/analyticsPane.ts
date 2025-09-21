import { ItemView, WorkspaceLeaf, Notice } from "obsidian";

// --- Constants ---
export const VIEW_TYPE_ANALYTICS = "AI-analytics";

// --- Types ---
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

// --- Analytics View ---
export class AnalyticsView extends ItemView {
    state: AnalyticsState;

    constructor(leaf: WorkspaceLeaf, state: AnalyticsState) {
        super(leaf);
        this.state = state;
    }

    getViewType(): string {
        return VIEW_TYPE_ANALYTICS;
    }

    getDisplayText(): string {
        return "AI Analytics Dashboard";
    }

    async onOpen() {
        this.render();
    }

    async onClose() {
        // cleanup if necessary
    }

    // --- Render the analytics dashboard ---
    render() {
        const container = this.containerEl;
        container.empty();

        container.createEl("h2", { text: "Assistant Analytics" });

        // --- Global stats ---
        const processedCount = Object.keys(this.state.processedNotes).length;
        const qaCount = this.state.qaHistory.length;
        container.createEl("p", { text: `Processed notes: ${processedCount}` });
        container.createEl("p", { text: `QA interactions: ${qaCount}` });

        // --- Model usage ---
        container.createEl("h3", { text: "Model Usage" });
        const modelList = container.createEl("ul");
        Object.entries(this.state.modelUsage).forEach(([model, count]) => {
            modelList.createEl("li", { text: `${model}: ${count} calls` });
        });

        // --- Recent QA ---
        container.createEl("h3", { text: "Recent Q&A" });
        const qaList = container.createEl("ul");
        this.state.qaHistory.slice(-10).reverse().forEach(entry => {
            qaList.createEl("li", {
                text: `[${new Date(entry.timestamp).toLocaleString()}] ${entry.prompt} → ${entry.answer.slice(0, 50)}...`
            });
        });

        // --- Notes summaries ---
        container.createEl("h3", { text: "Notes Summary" });
        const notesDiv = container.createEl("div", { cls: "notes-summary" });

        Object.values(this.state.processedNotes).forEach(note => {
            const box = notesDiv.createEl("div", { cls: "note-box" });
            box.createEl("h4", { text: note.file });
            box.createEl("p", { text: `Processed: ${note.processed} times` });
            box.createEl("p", { text: note.summary || "No summary yet." });

            if (note.inVaultLinks.length > 0) {
                box.createEl("p", { text: `Links (vault): ${note.inVaultLinks.join(", ")}` });
            }
            if (note.externalLinks.length > 0) {
                box.createEl("p", { text: `Links (external): ${note.externalLinks.join(", ")}` });
            }
        });
    }

    // --- Update state and refresh ---
    updateState(newState: AnalyticsState) {
        this.state = newState;
        this.render();
    }
}
