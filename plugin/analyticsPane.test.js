// Test: analyticsPane.js
const { AnalyticsView, VIEW_TYPE_ANALYTICS } = require('./analyticsPane');

describe('analyticsPane.js', () => {
  test('should export AnalyticsView class', () => {
    expect(AnalyticsView).toBeDefined();
    expect(typeof AnalyticsView).toBe('function');
  });

  test('should export VIEW_TYPE_ANALYTICS constant', () => {
    expect(VIEW_TYPE_ANALYTICS).toBeDefined();
    expect(VIEW_TYPE_ANALYTICS).toBe('AI-analytics');
  });
});