const { App, Notice } = require("obsidian");
const BackendClient = require("./backendClient.js");

const VIEW_TYPE_TASK_QUEUE = "task-queue-view";

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
      const data = await this.backendClient.post("/ask", { question, prefer_fast: true });
      new Notice(`Answer received: ${data.answer.substring(0, 100)}...`);
    } catch (e) {
      new Notice(`Error asking question: ${e.message}`);
    }
  }

  async formatNote(notePath, content) {
    try {
      await this.backendClient.post("/api/format_note", { note_path: notePath, content });
      new Notice(`Note formatted: ${notePath}`);
    } catch (e) {
      new Notice(`Error formatting note: ${e.message}`);
    }
  }

  async linkNote(notePath, content) {
    try {
      const data = await this.backendClient.post("/api/link_notes", { note_path: notePath, content });
      new Notice(`Linked notes: ${data.related_notes?.join(", ") || "none"}`);
    } catch (e) {
      new Notice(`Error linking note: ${e.message}`);
    }
  }

  // Expose queue for UI
  getTasks() {
    return [...this.queue];
  }
}

module.exports = { TaskQueue, VIEW_TYPE_TASK_QUEUE };