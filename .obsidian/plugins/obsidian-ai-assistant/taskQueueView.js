const { ItemView, WorkspaceLeaf, App, ButtonComponent, Setting, Notice } = require('obsidian');
const { TaskQueue, VIEW_TYPE_TASK_QUEUE } = require('./taskQueue');

class TaskQueueView extends ItemView {
    constructor(leaf, taskQueue, analytics) {
        super(leaf);
        this.taskQueue = taskQueue;
        this.analytics = analytics;
        this.searchInput = null;
        this.taskContainer = null;
    }

    getViewType() {
        return VIEW_TYPE_TASK_QUEUE;
    }

    getDisplayText() {
        return 'Task Queue';
    }

    async onOpen() {
        const container = this.containerEl;
        container.empty();
        // --- Header ---
        const header = container.createEl('div', { cls: 'task-queue-header' });
        header.createEl('h3', { text: 'Task Queue' });
        // --- Search Input ---
        const searchDiv = container.createEl('div', { cls: 'task-queue-search' });
        this.searchInput = searchDiv.createEl('input', {
            type: 'text',
            placeholder: 'Search tasks...',
        });
        this.searchInput.addEventListener('input', () => this.renderTasks());
        // --- Filter Controls ---
        const filterDiv = container.createEl('div', { cls: 'task-queue-filters' });
        const statusFilter = filterDiv.createEl('select', { cls: 'status-filter' });
        statusFilter.createEl('option', { value: '', text: 'All Status' });
        statusFilter.createEl('option', { value: 'pending', text: 'Pending' });
        statusFilter.createEl('option', { value: 'processing', text: 'Processing' });
        statusFilter.createEl('option', { value: 'completed', text: 'Completed' });
        statusFilter.createEl('option', { value: 'failed', text: 'Failed' });
        statusFilter.createEl('option', { value: 'waiting', text: 'Waiting' });
        const priorityFilter = filterDiv.createEl('select', { cls: 'priority-filter' });
        priorityFilter.createEl('option', { value: '', text: 'All Priorities' });
        priorityFilter.createEl('option', { value: '1', text: 'Low (1)' });
        priorityFilter.createEl('option', { value: '2', text: 'Medium (2)' });
        priorityFilter.createEl('option', { value: '3', text: 'High (3)' });
        priorityFilter.createEl('option', { value: '4', text: 'Critical (4)' });
        statusFilter.addEventListener('change', () => this.renderTasks());
        priorityFilter.addEventListener('change', () => this.renderTasks());
        // --- Control Buttons ---
        const controlDiv = container.createEl('div', { cls: 'task-queue-controls' });
        const startBtn = controlDiv.createEl('button', { text: 'Start Queue', cls: 'mod-cta' });
        startBtn.addEventListener('click', async () => {
            await this.taskQueue.startQueue();
            this.renderTasks();
        });
        const pauseBtn = controlDiv.createEl('button', { text: 'Pause Queue' });
        pauseBtn.addEventListener('click', () => {
            this.taskQueue.pauseQueue();
            this.renderTasks();
        });
        const clearBtn = controlDiv.createEl('button', { text: 'Clear Completed' });
        clearBtn.addEventListener('click', () => {
            this.taskQueue.clearCompleted();
            this.renderTasks();
        });
        const retryBtn = controlDiv.createEl('button', { text: 'Retry Failed' });
        retryBtn.addEventListener('click', async () => {
            await this.taskQueue.retryFailedTasks();
            this.renderTasks();
        });

        // --- Bulk Operations ---
        const bulkDiv = container.createEl('div', { cls: 'task-queue-bulk' });
        const importBtn = bulkDiv.createEl('button', { text: 'Import Tasks' });
        const exportBtn = bulkDiv.createEl('button', { text: 'Export Tasks' });
        importBtn.addEventListener('click', () => this.showImportDialog());
        exportBtn.addEventListener('click', () => this.exportTasks());
        // --- Task List Container ---
        this.taskContainer = container.createEl('div', { cls: 'task-queue-list' });
        // Initial render
        this.renderTasks();
    }

    async onClose() {
        // Nothing special for now
    }

    renderTasks() {
        if (!this.taskContainer) return;
        this.taskContainer.empty();
        const keyword = this.searchInput?.value || '';
        if (keyword) this.taskQueue.filterQueue(keyword);
        const tasks = this.taskQueue.getTasks();
        if (tasks.length === 0) {
            this.taskContainer.createEl('div', { text: 'No tasks in queue.' });
            return;
        }
        tasks.forEach((task) => {
            const taskEl = this.taskContainer.createEl('div', { cls: 'task-queue-item' });
            taskEl.createEl('strong', { text: `[${task.type.toUpperCase()}] ` });
            taskEl.createEl('span', { text: task.content });
            if (task.notePath) {
                taskEl.createEl('span', {
                    text: ` (Note: ${task.notePath})`,
                    cls: 'task-note-path',
                });
            }
            // Optional remove button
            const removeBtn = taskEl.createEl('button', { text: '74c' });
            removeBtn.addEventListener('click', () => {
                this.removeTask(task.id);
            });
        });
    }

    removeTask(taskId) {
        if (this.taskQueue.removeTask(taskId)) {
            new Notice('Task removed');
            this.renderTasks();
        }
    }

    showImportDialog() {
        const modal = new Modal(this.app);
        modal.titleEl.setText('Import Tasks');
        const contentEl = modal.contentEl;
        contentEl.createEl('p', { text: 'Paste JSON data to import tasks:' });
        const textArea = contentEl.createEl('textarea', {
            cls: 'import-textarea',
            attr: {
                rows: '10',
                cols: '50',
                placeholder: 'Paste JSON data here...'
            }
        });

        const buttonDiv = contentEl.createEl('div', { cls: 'modal-button-container' });
        const importBtn = buttonDiv.createEl('button', {
            text: 'Import',
            cls: 'mod-cta'
        });
        importBtn.addEventListener('click', () => {
            const jsonData = textArea.value.trim();
            if (jsonData) {
                const count = this.taskQueue.importTasks(jsonData);
                if (count > 0) {
                    this.renderTasks();
                    modal.close();
                }
            }
        });
        const cancelBtn = buttonDiv.createEl('button', { text: 'Cancel' });
        cancelBtn.addEventListener('click', () => modal.close());
        modal.open();
    }

    exportTasks() {
        const jsonData = this.taskQueue.exportTasks();
        const blob = new Blob([jsonData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `tasks-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        new Notice('Tasks exported successfully');
    }

    showTaskResult(task) {
        const modal = new Modal(this.app);
        modal.titleEl.setText(`Task Result: ${task.type}`);
        const contentEl = modal.contentEl;
        contentEl.createEl('h4', { text: 'Task Details' });
        const detailsEl = contentEl.createEl('div', { cls: 'task-result-details' });
        detailsEl.innerHTML = `
            <p><strong>Type:</strong> ${task.type}</p>
            <p><strong>Content:</strong> ${task.content}</p>
            <p><strong>Status:</strong> ${task.status}</p>
            <p><strong>Duration:</strong> ${task.duration || 'N/A'}ms</p>
            <p><strong>Created:</strong> ${task.createdAt ? new Date(task.createdAt).toLocaleString() : 'N/A'}</p>
        `;
        if (task.result) {
            contentEl.createEl('h4', { text: 'Result' });
            const resultEl = contentEl.createEl('pre', {
                cls: 'task-result-content',
                text: typeof task.result === 'string'
                    ? task.result
                    : JSON.stringify(task.result, null, 2)
            });
        }
        const closeBtn = contentEl.createEl('button', {
            text: 'Close',
            cls: 'mod-cta'
        });
        closeBtn.addEventListener('click', () => modal.close());
        modal.open();
    }
}

// Import Modal class for dialogs
const { Modal } = require('obsidian');

module.exports = { TaskQueueView };
