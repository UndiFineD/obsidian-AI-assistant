// Test: taskQueue.js
const { TaskQueue, VIEW_TYPE_TASK_QUEUE } = require('./taskQueue');

describe('taskQueue.js', () => {
  test('should export TaskQueue class', () => {
    expect(TaskQueue).toBeDefined();
    expect(typeof TaskQueue).toBe('function');
  });

  test('should export VIEW_TYPE_TASK_QUEUE constant', () => {
    expect(VIEW_TYPE_TASK_QUEUE).toBeDefined();
    expect(VIEW_TYPE_TASK_QUEUE).toBe('task-queue-view');
  });
});