import { ItemView, WorkspaceLeaf, App, ButtonComponent, Setting } from "obsidian";
import { TaskQueue, QueueTask, VIEW_TYPE_TASK_QUEUE } from "./taskQueue";

export class TaskQueueView extends ItemView {
  private taskQueue: TaskQueue;
  private searchInput: HTMLInputElement;
  private taskContainer: HTMLDivElement;

  constructor(leaf: WorkspaceLeaf, taskQueue: TaskQueue) {
    super(leaf);
    this.taskQueue = taskQueue;
  }

  getViewType(): string {
    return VIEW_TYPE_TASK_QUEUE;
  }

  getDisplayText(): string {
    return "Task Queue";
  }

  async onOpen() {
    const container = this.containerEl;
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
    startBtn.addEventListener("click", async () => {
      await this.taskQueue.startQueue();
      this.renderTasks();
    });

    const pauseBtn = controlDiv.createEl("button", { text: "Pause Queue" });
    pauseBtn.addEventListener("click", () => {
      this.taskQueue.pauseQueue();
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

  private renderTasks() {
    if (!this.taskContainer) return;
    this.taskContainer.empty();

    const keyword = this.searchInput?.value || "";
    if (keyword) this.taskQueue.filterQueue(keyword);

    const tasks = this.taskQueue.getTasks();

    if (tasks.length === 0) {
      this.taskContainer.createEl("div", { text: "No tasks in queue." });
      return;
    }

    tasks.forEach(task => {
      const taskEl = this.taskContainer.createEl("div", { cls: "task-queue-item" });

      taskEl.createEl("strong", { text: `[${task.type.toUpperCase()}] ` });
      taskEl.createEl("span", { text: task.content });

      if (task.notePath) {
        taskEl.createEl("span", { text: ` (Note: ${task.notePath})`, cls: "task-note-path" });
      }

      // Optional remove button
      const removeBtn = taskEl.createEl("button", { text: "❌" });
      removeBtn.addEventListener("click", () => {
        this.removeTask(task.id);
      });
    });
  }

  private removeTask(taskId: string) {
    // Remove task from queue
    const currentTasks = this.taskQueue.getTasks();
    const index = currentTasks.findIndex(t => t.id === taskId);
    if (index !== -1) {
      currentTasks.splice(index, 1);
      new Notice("Task removed");
      this.renderTasks();
    }
  }
}

