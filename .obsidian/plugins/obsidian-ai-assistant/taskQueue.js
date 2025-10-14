const { App, Notice } = require('obsidian');
const BackendClient = require('./backendClient.js');
const VIEW_TYPE_TASK_QUEUE = 'task-queue-view';

// ----------------------------
// Core Task Queue
// ----------------------------
class TaskQueue {
    constructor(backendUrl, app, getAuthToken = null) {
        this.app = app;
        this.backendUrl = backendUrl;
        this.backendClient = new BackendClient(backendUrl, getAuthToken);
        this.queue = [];
        this.isRunning = false;
        this.filteredQueue = [];
    }

    addTask(task) {
        if (!task.priority) task.priority = 1;
        if (!task.id) task.id = crypto.randomUUID();

        this.queue.push(task);
        this.sortQueue();
        this.filteredQueue = [...this.queue];
        new Notice(`Task added. Queue length: ${this.queue.length}`);
    }

    pauseQueue() {
        this.isRunning = false;
        new Notice('Queue paused');
    }

    async startQueue(batchSize = 3) {
        if (this.isRunning) return;
        this.isRunning = true;

        while (this.filteredQueue.length > 0 && this.isRunning) {
            const batch = this.filteredQueue.splice(0, batchSize);
            await Promise.all(batch.map((task) => this.processTask(task)));
        }

        new Notice('Queue finished');
        this.isRunning = false;
    }

    sortQueue() {
        this.queue.sort((a, b) => (b.priority || 1) - (a.priority || 1));
    }

    filterQueue(keyword, status = null, priority = null) {
        if (!keyword && !status && !priority) {
            this.filteredQueue = [...this.queue];
            return;
        }
        this.filteredQueue = this.queue.filter((task) => {
            let matches = true;
            if (keyword) {
                matches = matches && (
                    task.content.toLowerCase().includes(keyword.toLowerCase()) ||
                    task.type.toLowerCase().includes(keyword.toLowerCase()) ||
                    (task.notePath && task.notePath.toLowerCase().includes(keyword.toLowerCase())) ||
                    (task.tags && task.tags.some(tag => tag.toLowerCase().includes(keyword.toLowerCase())))
                );
            }
            if (status) {
                matches = matches && (task.status === status);
            }
            if (priority) {
                matches = matches && (task.priority === priority);
            }
            return matches;
        });
    }

    // Advanced task management methods
    addBulkTasks(tasks) {
        const addedTasks = [];
        tasks.forEach(taskData => {
            const task = {
                id: crypto.randomUUID(),
                priority: taskData.priority || 1,
                type: taskData.type,
                content: taskData.content,
                context: taskData.context,
                notePath: taskData.notePath,
                tags: taskData.tags || [],
                dependencies: taskData.dependencies || [],
                retryCount: 0,
                maxRetries: taskData.maxRetries || 3,
                timeout: taskData.timeout || 30000,
                createdAt: new Date().toISOString(),
                ...taskData
            };
            this.queue.push(task);
            addedTasks.push(task);
        });
        this.sortQueue();
        this.filteredQueue = [...this.queue];
        new Notice(`Added ${addedTasks.length} tasks. Queue length: ${this.queue.length}`);
        return addedTasks;
    }

    updateTask(taskId, updates) {
        const task = this.queue.find(t => t.id === taskId);
        if (task) {
            Object.assign(task, updates);
            this.sortQueue();
            return true;
        }
        return false;
    }

    getTasksByStatus(status) {
        return this.queue.filter(task => task.status === status);
    }

    getTasksByPriority(priority) {
        return this.queue.filter(task => task.priority === priority);
    }

    clearCompleted() {
        const completedCount = this.queue.filter(t => t.status === 'completed').length;
        this.queue = this.queue.filter(task => task.status !== 'completed');
        this.filteredQueue = this.filteredQueue.filter(task => task.status !== 'completed');
        new Notice(`Cleared ${completedCount} completed tasks`);
        return completedCount;
    }

    async retryFailedTasks() {
        const failedTasks = this.queue.filter(task => task.status === 'failed' && (task.retryCount || 0) < (task.maxRetries || 3));
        for (const task of failedTasks) {
            task.status = 'pending';
            task.retryCount = (task.retryCount || 0) + 1;
            task.error = null;
        }
        new Notice(`Retrying ${failedTasks.length} failed tasks`);
        return failedTasks.length;
    }

    exportTasks() {
        const exportData = {
            exportedAt: new Date().toISOString(),
            tasks: this.queue.map(task => ({
                ...task,
                result: task.result ? '[RESULT_DATA]' : null // Exclude large result data
            }))
        };
        return JSON.stringify(exportData, null, 2);
    }

    importTasks(jsonData) {
        try {
            const data = JSON.parse(jsonData);
            if (data.tasks && Array.isArray(data.tasks)) {
                const importedTasks = data.tasks.map(task => ({
                    ...task,
                    id: crypto.randomUUID(), // Generate new IDs
                    status: 'pending', // Reset status
                    result: null,
                    error: null,
                    retryCount: 0
                }));
                this.queue.push(...importedTasks);
                this.sortQueue();
                this.filteredQueue = [...this.queue];
                new Notice(`Imported ${importedTasks.length} tasks`);
                return importedTasks.length;
            }
        } catch (error) {
            new Notice(`Import failed: ${error.message}`);
            return 0;
        }
    }

    async processTask(task) {
        try {
            task.status = 'processing';
            task.startedAt = new Date().toISOString();
            // Check dependencies
            const pendingDependencies = task.dependencies?.filter(depId => {
                const depTask = this.queue.find(t => t.id === depId);
                return depTask && depTask.status !== 'completed';
            });
            if (pendingDependencies && pendingDependencies.length > 0) {
                task.status = 'waiting';
                task.error = `Waiting for ${pendingDependencies.length} dependencies`;
                return;
            }
            let result;
            const timeoutPromise = new Promise((_, reject) => setTimeout(() => reject(new Error('Task timeout')), task.timeout || 30000));
            const taskPromise = this.executeTask(task);
            result = await Promise.race([taskPromise, timeoutPromise]);
            task.status = 'completed';
            task.result = result;
            task.completedAt = new Date().toISOString();
            task.duration = new Date(task.completedAt) - new Date(task.startedAt);
            new Notice(`Task completed: ${task.type} (${task.duration}ms)`);
        } catch (error) {
            task.status = 'failed';
            task.error = error.message;
            task.failedAt = new Date().toISOString();
            const retryCount = task.retryCount || 0;
            const maxRetries = task.maxRetries || 3;
            if (retryCount < maxRetries) {
                new Notice(`Task failed: ${task.type} - Will retry (${retryCount + 1}/${maxRetries})`);
            } else {
                new Notice(`Task failed permanently: ${task.type} - ${error.message}`);
            }
        }
    }

    async executeTask(task) {
        switch (task.type) {
            case 'ask':
                return await this.askQuestion(task.content);
            case 'format':
                if (task.notePath) return await this.formatNote(task.notePath, task.content);
                break;
            case 'link':
                if (task.notePath) return await this.linkNote(task.notePath, task.content);
                break;
            case 'reindex':
                return await this.backendClient.post('/reindex');
            case 'web':
                return await this.backendClient.post('/web', {
                    url: task.content,
                    prompt: task.context || 'Summarize this webpage',
                });
            case 'transcribe':
                return await this.backendClient.post('/transcribe', {
                    audio: task.content,
                    model: task.model || 'vosk'
                });
            case 'batch_ask':
                const results = [];
                for (const prompt of task.prompts || []) {
                    const result = await this.askQuestion(prompt);
                    results.push(result);
                }
                return results;
            default:
                throw new Error(`Unknown task type: ${task.type}`);
        }
    }

    async askQuestion(question) {
        try {
            const data = await this.backendClient.post('/ask', { question, prefer_fast: true });
            new Notice(`Answer received: ${data.answer.substring(0, 100)}...`);
        } catch (e) {
            new Notice(`Error asking question: ${e.message}`);
        }
    }

    async formatNote(notePath, content) {
        try {
            await this.backendClient.post('/api/format_note', { note_path: notePath, content });
            new Notice(`Note formatted: ${notePath}`);
        } catch (e) {
            new Notice(`Error formatting note: ${e.message}`);
        }
    }

    async linkNote(notePath, content) {
        try {
            const data = await this.backendClient.post('/api/link_notes', {
                note_path: notePath,
                content,
            });
            new Notice(`Linked notes: ${data.related_notes?.join(', ') || 'none'}`);
        } catch (e) {
            new Notice(`Error linking note: ${e.message}`);
        }
    }

    // Remove a task by id
    removeTask(id) {
        const idx = this.queue.findIndex((t) => t.id === id);
        if (idx !== -1) {
            this.queue.splice(idx, 1);
            this.filteredQueue = [...this.queue];
            return true;
        }
        return false;
    }

    // Expose queue for UI
    getTasks() {
        return this.filteredQueue && this.filteredQueue.length
            ? [...this.filteredQueue]
            : [...this.queue];
    }

    getStats() {
        const completed = this.queue.filter((t) => t.status === 'completed').length;
        const failed = this.queue.filter((t) => t.status === 'failed').length;
        const processing = this.queue.filter((t) => t.status === 'processing').length;
        const waiting = this.queue.filter((t) => t.status === 'waiting').length;
        const pending = this.queue.filter((t) => !t.status || t.status === 'pending').length;
        const totalDuration = this.queue
            .filter(t => t.duration)
            .reduce((sum, t) => sum + t.duration, 0);
        const avgDuration = completed > 0 ? totalDuration / completed : 0;
        return {
            total: this.queue.length,
            completed,
            failed,
            processing,
            waiting,
            pending,
            avgDuration: Math.round(avgDuration),
            successRate: this.queue.length > 0 ? (completed / this.queue.length * 100).toFixed(1) : 0
        };
    }
}

module.exports = { TaskQueue, VIEW_TYPE_TASK_QUEUE };
