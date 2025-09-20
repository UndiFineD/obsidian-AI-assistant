import { App, Notice } from 'obsidian';

interface QueueTask {
    type: 'ask' | 'format' | 'link';
    content: string;
    notePath?: string;
    priority?: number; // Higher number = higher priority
}

export class TaskQueue {
    private backendUrl: string;
    private app: App;
    private queue: QueueTask[] = [];
    private isRunning: boolean = false;
    private filteredQueue: QueueTask[] = [];

    constructor(backendUrl: string, app: App) {
        this.backendUrl = backendUrl;
        this.app = app;
    }

    addTask(task: QueueTask) {
        if (!task.priority) task.priority = 1;
        this.queue.push(task);
        this.sortQueue();
        this.filteredQueue = [...this.queue];
        new Notice(`Task added. Queue length: ${this.queue.length}`);
    }

    pauseQueue() {
        this.isRunning = false;
        new Notice('Queue paused');
    }

    async startQueue(batchSize: number = 3) {
        if (this.isRunning) return;
        this.isRunning = true;

        while (this.filteredQueue.length > 0 && this.isRunning) {
            const batch = this.filteredQueue.splice(0, batchSize);
            await Promise.all(batch.map(task => this.processTask(task)));
        }
        new Notice('Queue finished');
    }

    sortQueue() {
        this.queue.sort((a, b) => (b.priority || 1) - (a.priority || 1));
    }

    filterQueue(keyword: string) {
        this.filteredQueue = this.queue.filter(task =>
            task.content.toLowerCase().includes(keyword.toLowerCase()) ||
            (task.notePath && task.notePath.toLowerCase().includes(keyword.toLowerCase()))
        );
    }

    async processTask(task: QueueTask) {
        switch(task.type) {
            case 'ask':
                await this.askQuestion(task.content);
                break;
            case 'format':
                if (task.notePath) await this.formatNote(task.notePath);
                break;
            case 'link':
                if (task.notePath) await this.linkNote(task.notePath);
                break;
        }
    }

    async askQuestion(question: string) {
        try {
            const response = await fetch(`${this.backendUrl}/api/ask`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ question, prefer_fast: true })
            });
            const data = await response.json();
            new Notice(`Answer received: ${data.answer.substring(0, 100)}...`);
        } catch(e) {
            new Notice(`Error asking question: ${e}`);
        }
    }

    async formatNote(notePath: string) {
        try {
            const response = await fetch(`${this.backendUrl}/api/format_note`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ note_path: notePath, content: "" })
            });
            const data = await response.json();
            new Notice(`Note formatted: ${notePath}`);
        } catch(e) {
            new Notice(`Error formatting note: ${e}`);
        }
    }

    async linkNote(notePath: string) {
        try {
            const response = await fetch(`${this.backendUrl}/api/link_notes`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ note_path: notePath, content: "" })
            });
            const data = await response.json();
            new Notice(`Linked notes: ${data.related_notes.join(", ")}`);
        } catch(e) {
            new Notice(`Error linking note: ${e}`);
        }
    }
	// In your TaskQueuePane class
	const searchInput = containerEl.createEl('input', { type: 'text', placeholder: 'Search queue...' });
	searchInput.addEventListener('input', (e) => {
		const keyword = (e.target as HTMLInputElement).value;
		this.taskQueue.filterQueue(keyword);
	});

}
