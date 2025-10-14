const { ItemView, Modal, Notice } = require('obsidian');
const { TaskQueue, VIEW_TYPE_TASK_QUEUE } = require('./taskQueue');

class EnhancedTaskQueueView extends ItemView {
    constructor(leaf, taskQueue, analytics) {
        super(leaf);
        this.taskQueue = taskQueue;
        this.analytics = analytics;
        this.searchInput = null;
        this.taskContainer = null;
        this.autoRefresh = null;
    }

    getViewType() {
        return VIEW_TYPE_TASK_QUEUE;
    }

    getDisplayText() {
        return 'Advanced Task Queue';
    }

    async onOpen() {
        const container = this.containerEl;
        container.empty();

        // --- Header ---
        const header = container.createEl('div', { cls: 'task-queue-header' });
        header.createEl('h3', { text: 'Advanced Task Queue Manager' });

        // --- Search Input ---
        const searchDiv = container.createEl('div', { cls: 'task-queue-search' });
        this.searchInput = searchDiv.createEl('input', {
            type: 'text',
            placeholder: 'Search tasks by content, type, or tags...',
            cls: 'search-input'
        });
        this.searchInput.addEventListener('input', () => this.renderTasks());

        // --- Filter Controls ---
    const filterDiv = container.createEl('div', { cls: 'task-queue-filters' });

        const statusFilter = filterDiv.createEl('select', { cls: 'status-filter' });
        statusFilter.createEl('option', { value: '', text: 'All Status' });
        statusFilter.createEl('option', { value: 'pending', text: '⏳ Pending' });
        statusFilter.createEl('option', { value: 'processing', text: '⚡ Processing' });
        statusFilter.createEl('option', { value: 'completed', text: '✅ Completed' });
        statusFilter.createEl('option', { value: 'failed', text: '❌ Failed' });
        statusFilter.createEl('option', { value: 'waiting', text: '⏸️ Waiting' });
        
        const priorityFilter = filterDiv.createEl('select', { cls: 'priority-filter' });
        priorityFilter.createEl('option', { value: '', text: 'All Priorities' });
        priorityFilter.createEl('option', { value: '1', text: '🔵 Low (1)' });
        priorityFilter.createEl('option', { value: '2', text: '🟡 Medium (2)' });
        priorityFilter.createEl('option', { value: '3', text: '🟠 High (3)' });
        priorityFilter.createEl('option', { value: '4', text: '🔴 Critical (4)' });
        
        statusFilter.addEventListener('change', () => this.renderTasks());
        priorityFilter.addEventListener('change', () => this.renderTasks());

        // --- Control Buttons ---
    const controlDiv = container.createEl('div', { cls: 'task-queue-controls' });

        const startBtn = controlDiv.createEl('button', {
            text: '▶️ Start Queue',
            cls: 'mod-cta control-btn'
        });
        startBtn.addEventListener('click', async () => {
            startBtn.disabled = true;
            startBtn.setText('Starting...');
            try {
                await this.taskQueue.startQueue();
            } finally {
                startBtn.disabled = false;
                startBtn.setText('▶️ Start Queue');
                this.renderTasks();
            }
        });

        const pauseBtn = controlDiv.createEl('button', {
            text: '⏸️ Pause',
            cls: 'control-btn'
        });
        pauseBtn.addEventListener('click', () => {
            this.taskQueue.pauseQueue();
            this.renderTasks();
        });

        const clearBtn = controlDiv.createEl('button', {
            text: '🧹 Clear Completed',
            cls: 'control-btn'
        });
        clearBtn.addEventListener('click', () => {
            this.taskQueue.clearCompleted();
            this.renderTasks();
        });

        const retryBtn = controlDiv.createEl('button', {
            text: '🔄 Retry Failed',
            cls: 'control-btn'
        });
        retryBtn.addEventListener('click', async () => {
            await this.taskQueue.retryFailedTasks();
            this.renderTasks();
        });

        // --- Bulk Operations ---
        const bulkDiv = container.createEl('div', { cls: 'task-queue-bulk' });

        const addTaskBtn = bulkDiv.createEl('button', {
            text: '➕ Add Task',
            cls: 'mod-cta bulk-btn'
        });
        addTaskBtn.addEventListener('click', () => this.showAddTaskDialog());

        const importBtn = bulkDiv.createEl('button', {
            text: '📥 Import',
            cls: 'bulk-btn'
        });
        importBtn.addEventListener('click', () => this.showImportDialog());
        
        const exportBtn = bulkDiv.createEl('button', {
            text: '📤 Export',
            cls: 'bulk-btn'
        });
        exportBtn.addEventListener('click', () => this.exportTasks());

        // --- Auto-refresh toggle ---
    const settingsDiv = container.createEl('div', { cls: 'task-queue-settings' });
        const autoRefreshToggle = settingsDiv.createEl('label', { cls: 'auto-refresh-toggle' });
        const checkbox = autoRefreshToggle.createEl('input', { type: 'checkbox' });
        autoRefreshToggle.createEl('span', { text: 'Auto-refresh (5s)' });

        checkbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startAutoRefresh();
            } else {
                this.stopAutoRefresh();
            }
        });

        // --- Task List Container ---
        this.taskContainer = container.createEl('div', { cls: 'task-queue-list' });

        // Initial render
        this.renderTasks();
    }

    async onClose() {
        this.stopAutoRefresh();
    }

    startAutoRefresh() {
        this.stopAutoRefresh();
        this.autoRefresh = setInterval(() => {
            this.renderTasks();
        }, 5000);
    }

    stopAutoRefresh() {
        if (this.autoRefresh) {
            clearInterval(this.autoRefresh);
            this.autoRefresh = null;
        }
    }

    renderTasks() {
        if (!this.taskContainer) return;
        this.taskContainer.empty();

        // Apply filters
        const keyword = this.searchInput?.value || '';
        const statusFilter = this.containerEl.querySelector('.status-filter')?.value || '';
        const priorityFilter = this.containerEl.querySelector('.priority-filter')?.value || '';
        
        this.taskQueue.filterQueue(keyword, statusFilter, priorityFilter ? parseInt(priorityFilter) : null);

        const tasks = this.taskQueue.getTasks();
        const stats = this.taskQueue.getStats();

        // --- Statistics Bar ---
        const statsEl = this.taskContainer.createEl('div', { cls: 'task-queue-stats' });
        statsEl.innerHTML = `
            <div class="stat-item">
                <span class="stat-label">Total:</span>
                <span class="stat-value">${stats.total}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">✅ Completed:</span>
                <span class="stat-value success">${stats.completed}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">❌ Failed:</span>
                <span class="stat-value error">${stats.failed}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">⚡ Processing:</span>
                <span class="stat-value processing">${stats.processing}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Success Rate:</span>
                <span class="stat-value">${stats.successRate}%</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Avg Duration:</span>
                <span class="stat-value">${stats.avgDuration}ms</span>
            </div>
        `;

        if (tasks.length === 0) {
            this.taskContainer.createEl('div', { 
                text: 'No tasks match current filters.', 
                cls: 'task-queue-empty' 
            });
            return;
        }

        // --- Task List ---
        tasks.forEach((task) => {
            const taskEl = this.taskContainer.createEl('div', { 
                cls: `task-queue-item task-${task.status || 'pending'}` 
            });

            // Task header with status indicator
            const headerEl = taskEl.createEl('div', { cls: 'task-header' });
            
            const statusIndicator = headerEl.createEl('span', { 
                cls: `task-status-indicator status-${task.status || 'pending'}`,
                text: this.getStatusIcon(task.status)
            });
            
            const typeEl = headerEl.createEl('strong', { 
                text: `[${task.type.toUpperCase()}]`,
                cls: 'task-type'
            });
            
            const priorityEl = headerEl.createEl('span', { 
                text: this.getPriorityIcon(task.priority || 1),
                cls: `task-priority priority-${task.priority || 1}`
            });

            // Task content
            const contentEl = taskEl.createEl('div', { cls: 'task-content' });
            contentEl.createEl('span', { text: task.content });

            if (task.notePath) {
                contentEl.createEl('span', {
                    text: ` 📝 ${task.notePath}`,
                    cls: 'task-note-path',
                });
            }

            // Task metadata
            if (task.tags && task.tags.length > 0) {
                const tagsEl = taskEl.createEl('div', { cls: 'task-tags' });
                task.tags.forEach(tag => {
                    tagsEl.createEl('span', { 
                        text: `🏷️ ${tag}`, 
                        cls: 'task-tag' 
                    });
                });
            }

            // Task timing info
            if (task.createdAt || task.duration) {
                const timingEl = taskEl.createEl('div', { cls: 'task-timing' });
                if (task.createdAt) {
                    timingEl.createEl('span', { 
                        text: `🕐 Created: ${new Date(task.createdAt).toLocaleString()}`,
                        cls: 'task-created'
                    });
                }
                if (task.duration) {
                    timingEl.createEl('span', { 
                        text: `⏱️ Duration: ${task.duration}ms`,
                        cls: 'task-duration'
                    });
                }
                if (task.retryCount && task.retryCount > 0) {
                    timingEl.createEl('span', { 
                        text: `🔄 Retries: ${task.retryCount}/${task.maxRetries || 3}`,
                        cls: 'task-retries'
                    });
                }
            }

            // Error display
            if (task.error) {
                const errorEl = taskEl.createEl('div', { 
                    cls: 'task-error',
                    text: `❌ Error: ${task.error}`
                });
            }

            // Dependencies display
            if (task.dependencies && task.dependencies.length > 0) {
                const depsEl = taskEl.createEl('div', { 
                    cls: 'task-dependencies',
                    text: `🔗 Dependencies: ${task.dependencies.length}`
                });
            }

            // Task actions
            const actionsEl = taskEl.createEl('div', { cls: 'task-actions' });
            
            if (task.status === 'failed') {
                const retryBtn = actionsEl.createEl('button', { 
                    text: '🔄 Retry', 
                    cls: 'task-action-btn retry-btn'
                });
                retryBtn.addEventListener('click', () => {
                    task.status = 'pending';
                    task.error = null;
                    this.renderTasks();
                });
            }

            const removeBtn = actionsEl.createEl('button', { 
                text: '🗑️', 
                cls: 'task-action-btn remove-btn',
                attr: { title: 'Remove task' }
            });
            removeBtn.addEventListener('click', () => {
                this.removeTask(task.id);
            });

            if (task.result) {
                const showResultBtn = actionsEl.createEl('button', { 
                    text: '👁️', 
                    cls: 'task-action-btn result-btn',
                    attr: { title: 'View result' }
                });
                showResultBtn.addEventListener('click', () => {
                    this.showTaskResult(task);
                });
            }

            const editBtn = actionsEl.createEl('button', { 
                text: '✏️', 
                cls: 'task-action-btn edit-btn',
                attr: { title: 'Edit task' }
            });
            editBtn.addEventListener('click', () => {
                this.showEditTaskDialog(task);
            });
        });
    }

    getStatusIcon(status) {
        const icons = {
            'pending': '⏳',
            'processing': '⚡',
            'completed': '✅',
            'failed': '❌',
            'waiting': '⏸️'
        };
        return icons[status] || '⏳';
    }

    getPriorityIcon(priority) {
        const icons = {
            1: '🔵 P1',
            2: '🟡 P2', 
            3: '🟠 P3',
            4: '🔴 P4'
        };
        return icons[priority] || '🔵 P1';
    }

    removeTask(taskId) {
        if (this.taskQueue.removeTask(taskId)) {
            new Notice('Task removed');
            this.renderTasks();
        }
    }

    showAddTaskDialog() {
        const modal = new Modal(this.app);
        modal.titleEl.setText('Add New Task');

        const contentEl = modal.contentEl;
        
        // Task type
        contentEl.createEl('label', { text: 'Task Type:' });
        const typeSelect = contentEl.createEl('select', { cls: 'task-type-select' });
        ['ask', 'reindex', 'web', 'transcribe', 'format', 'link', 'batch_ask'].forEach(type => {
            typeSelect.createEl('option', { value: type, text: type.toUpperCase() });
        });

        // Content
        contentEl.createEl('label', { text: 'Content:' });
        const contentInput = contentEl.createEl('textarea', {
            cls: 'task-content-input',
            attr: { rows: '3', placeholder: 'Enter task content...' }
        });

        // Priority
        contentEl.createEl('label', { text: 'Priority:' });
        const prioritySelect = contentEl.createEl('select', { cls: 'task-priority-select' });
        [1, 2, 3, 4].forEach(p => {
            prioritySelect.createEl('option', { 
                value: p.toString(), 
                text: `${this.getPriorityIcon(p)}` 
            });
        });

        // Tags
        contentEl.createEl('label', { text: 'Tags (comma-separated):' });
        const tagsInput = contentEl.createEl('input', {
            type: 'text',
            cls: 'task-tags-input',
            attr: { placeholder: 'tag1, tag2, tag3' }
        });

        // Buttons
        const buttonDiv = contentEl.createEl('div', { cls: 'modal-button-container' });
        
        const addBtn = buttonDiv.createEl('button', { 
            text: 'Add Task', 
            cls: 'mod-cta' 
        });
        addBtn.addEventListener('click', () => {
            const taskData = {
                type: typeSelect.value,
                content: contentInput.value.trim(),
                priority: parseInt(prioritySelect.value),
                tags: tagsInput.value.split(',').map(t => t.trim()).filter(t => t),
                createdAt: new Date().toISOString()
            };

            if (taskData.content) {
                this.taskQueue.addTask(taskData);
                this.renderTasks();
                modal.close();
            }
        });

        const cancelBtn = buttonDiv.createEl('button', { text: 'Cancel' });
        cancelBtn.addEventListener('click', () => modal.close());

        modal.open();
    }

    showEditTaskDialog(task) {
        const modal = new Modal(this.app);
        modal.titleEl.setText('Edit Task');

        const contentEl = modal.contentEl;
        
        // Content
        contentEl.createEl('label', { text: 'Content:' });
        const contentInput = contentEl.createEl('textarea', {
            cls: 'task-content-input',
            attr: { rows: '3' }
        });
        contentInput.value = task.content;

        // Priority
        contentEl.createEl('label', { text: 'Priority:' });
        const prioritySelect = contentEl.createEl('select', { cls: 'task-priority-select' });
        [1, 2, 3, 4].forEach(p => {
            const option = prioritySelect.createEl('option', { 
                value: p.toString(), 
                text: `${this.getPriorityIcon(p)}` 
            });
            if (p === (task.priority || 1)) {
                option.selected = true;
            }
        });

        // Tags
        contentEl.createEl('label', { text: 'Tags (comma-separated):' });
        const tagsInput = contentEl.createEl('input', {
            type: 'text',
            cls: 'task-tags-input'
        });
        tagsInput.value = (task.tags || []).join(', ');

        // Buttons
        const buttonDiv = contentEl.createEl('div', { cls: 'modal-button-container' });
        
        const saveBtn = buttonDiv.createEl('button', { 
            text: 'Save Changes', 
            cls: 'mod-cta' 
        });
        saveBtn.addEventListener('click', () => {
            const updates = {
                content: contentInput.value.trim(),
                priority: parseInt(prioritySelect.value),
                tags: tagsInput.value.split(',').map(t => t.trim()).filter(t => t)
            };

            if (this.taskQueue.updateTask(task.id, updates)) {
                this.renderTasks();
                modal.close();
                new Notice('Task updated');
            }
        });

        const cancelBtn = buttonDiv.createEl('button', { text: 'Cancel' });
        cancelBtn.addEventListener('click', () => modal.close());

        modal.open();
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
            <p><strong>Status:</strong> ${this.getStatusIcon(task.status)} ${task.status}</p>
            <p><strong>Priority:</strong> ${this.getPriorityIcon(task.priority || 1)}</p>
            <p><strong>Duration:</strong> ${task.duration || 'N/A'}ms</p>
            <p><strong>Created:</strong> ${task.createdAt ? new Date(task.createdAt).toLocaleString() : 'N/A'}</p>
            ${task.tags && task.tags.length > 0 ? `<p><strong>Tags:</strong> ${task.tags.join(', ')}</p>` : ''}
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

module.exports = { EnhancedTaskQueueView };