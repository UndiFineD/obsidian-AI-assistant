// Test: voiceInput.js
const { VoiceInput } = require('./voiceInput');

describe('voiceInput.js', () => {
  test('should export VoiceInput class', () => {
    expect(VoiceInput).toBeDefined();
    expect(typeof VoiceInput).toBe('function');
  });
});