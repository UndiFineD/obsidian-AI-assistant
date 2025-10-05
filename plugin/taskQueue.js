const { App, Notice } = require("obsidian");

const VIEW_TYPE_TASK_QUEUE = "task-queue-view";

// ----------------------------
// Core Task Queue
// ----------------------------
class TaskQueue {
  constructor(backendUrl, app) {
    this.app = app;
    this.backendUrl = backendUrl;
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
    new Notice("Queue paused");
  }

  async startQueue(batchSize = 3) {
    if (this.isRunning) return;
    this.isRunning = true;

    while (this.filteredQueue.length > 0 && this.isRunning) {
      const batch = this.filteredQueue.splice(0, batchSize);
      await Promise.all(batch.map(task => this.processTask(task)));
    }

    new Notice("Queue finished");
    this.isRunning = false;
  }

  sortQueue() {
    this.queue.sort((a, b) => (b.priority || 1) - (a.priority || 1));
  }

  filterQueue(keyword) {
    this.filteredQueue = this.queue.filter(task =>
      task.content.toLowerCase().includes(keyword.toLowerCase()) ||
      (task.notePath && task.notePath.toLowerCase().includes(keyword.toLowerCase()))
    );
  }

  async processTask(task) {
    switch (task.type) {
      case "ask":
        await this.askQuestion(task.content);
        break;
      case "format":
        if (task.notePath) await this.formatNote(task.notePath, task.content);
        break;
      case "link":
        if (task.notePath) await this.linkNote(task.notePath, task.content);
        break;
    }
  }

  async askQuestion(question) {
    try {
      const response = await fetch(`${this.backendUrl}/api/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, prefer_fast: true }),
      });
      const data = await response.json();
      new Notice(`Answer received: ${data.answer.substring(0, 100)}...`);
    } catch (e) {
      new Notice(`Error asking question: ${e}`);
    }
  }

  async formatNote(notePath, content) {
    try {
      const response = await fetch(`${this.backendUrl}/api/format_note`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ note_path: notePath, content }),
      });
      const data = await response.json();
      new Notice(`Note formatted: ${notePath}`);
    } catch (e) {
      new Notice(`Error formatting note: ${e}`);
    }
  }

  async linkNote(notePath, content) {
    try {
      const response = await fetch(`${this.backendUrl}/api/link_notes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ note_path: notePath, content }),
      });
      const data = await response.json();
      new Notice(`Linked notes: ${data.related_notes.join(", ")}`);
    } catch (e) {
      new Notice(`Error linking note: ${e}`);
    }
  }

  // Expose queue for UI
  getTasks() {
    return [...this.queue];
  }
}

module.exports = { TaskQueue, VIEW_TYPE_TASK_QUEUE };