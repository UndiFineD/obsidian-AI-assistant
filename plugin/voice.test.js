// Test: voice.js
const { VoiceRecorder } = require('./voice');

describe('voice.js', () => {
  test('should export VoiceRecorder class', () => {
    expect(VoiceRecorder).toBeDefined();
    expect(typeof VoiceRecorder).toBe('function');
  });
});