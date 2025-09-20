import { ItemView, WorkspaceLeaf, Workspace, Notice } from 'obsidian';

export const ANALYTICS_VIEW_TYPE = "llm-analytics";

export class AnalyticsPane extends ItemView {
    constructor(leaf: WorkspaceLeaf) {
        super(leaf);
    }

    getViewType(): string {
        return ANALYTICS_VIEW_TYPE;
    }

    getDisplayText(): string {
        return "LLM Analytics";
    }

    async onOpen() {
        const container = this.containerEl.children[1];
        container.empty();
        container.createEl('h3', { text: 'Semantic Coverage & QA History' });

        // Placeholder - in practice, fetch analytics data from backend/session memory
        container.createEl('p', { text: 'Total notes processed: 123' });
        container.createEl('p', { text: 'Top topics: AI, Obsidian, LLM' });
        container.createEl('p', { text: 'Recent questions:' });

        const questions = ["What is RAG?", "Summarize note X", "Link note Y"];
        const ul = container.createEl('ul');
        questions.forEach(q => {
            ul.createEl('li', { text: q });
        });
    }

    async onClose() {
        // Cleanup if needed
    }
}
