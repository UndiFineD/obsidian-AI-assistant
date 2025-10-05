// Test: main.js basic loading
const AssistantPlugin = require('./main');

describe('main.js', () => {
  test('should export AssistantPlugin class', () => {
    expect(AssistantPlugin).toBeDefined();
    expect(typeof AssistantPlugin).toBe('function');
  });
});