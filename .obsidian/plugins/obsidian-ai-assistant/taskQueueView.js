const { ItemView, WorkspaceLeaf, App, ButtonComponent, Setting, Notice } = require("obsidian");
const { TaskQueue, VIEW_TYPE_TASK_QUEUE } = require("./taskQueue");

class TaskQueueView extends ItemView { constructor(leaf, taskQueue, analytics) { super(leaf);
    this.taskQueue = taskQueue;
    this.analytics = analytics;
    this.searchInput = null;
    this.taskContainer = null;
    }

    getViewType() { return VIEW_TYPE_TASK_QUEUE;
    }

    getDisplayText() { return "Task Queue";
    }

    async onOpen() { const container = this.containerEl;
    container.empty();

    // --- Header ---
    const header = container.createEl("div", { cls: "task-queue-header" });
    header.createEl("h3", { text: "Task Queue" });

    // --- Search Input ---
    const searchDiv = container.createEl("div", { cls: "task-queue-search" });
    this.searchInput = searchDiv.createEl("input", { type: "text", placeholder: "Search tasks..." });
    this.searchInput.addEventListener("input", () => this.renderTasks());

    // --- Control Buttons ---
    const controlDiv = container.createEl("div", { cls: "task-queue-controls" });
    const startBtn = controlDiv.createEl("button", { text: "Start Queue" });
    startBtn.addEventListener("click", async() => { await this.taskQueue.startQueue();
        this.renderTasks();
    });

    const pauseBtn = controlDiv.createEl("button", { text: "Pause Queue" });
    pauseBtn.addEventListener("click", () => { this.taskQueue.pauseQueue();
        this.renderTasks();
    });

    // --- Task List Container ---
    this.taskContainer = container.createEl("div", { cls: "task-queue-list" });

    // Initial render
    this.renderTasks();
    }

    async onClose() {
        // Nothing special for now
    }

    renderTasks() { if(!this.taskContainer) return;
    this.taskContainer.empty();

    const keyword = this.searchInput?.value || "";
    if(keyword) this.taskQueue.filterQueue(keyword);

    const tasks = this.taskQueue.getTasks();

    if(tasks.length === 0) { this.taskContainer.createEl("div", { text: "No tasks in queue." });
        return;
    }

    tasks.forEach(task => { const taskEl = this.taskContainer.createEl("div", { cls: "task-queue-item" });

        taskEl.createEl("strong", { text: `[${ task.type.toUpperCase()}] ` });
        taskEl.createEl("span", { text: task.content });

        if(task.notePath) { taskEl.createEl("span", { text: ` (Note: ${ task.notePath })`, cls: "task-note-path" });
        }

        // Optional remove button
    const removeBtn = taskEl.createEl("button", { text: "74c" });
    removeBtn.addEventListener("click", () => { this.removeTask(task.id);
    });
    });
    }

    removeTask(taskId) {
        if(this.taskQueue.removeTask(taskId)) {
            new Notice("Task removed");
            this.renderTasks();
        }
    }
}

module.exports = { TaskQueueView };
