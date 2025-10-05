module.exports = {
  testEnvironment: 'node',
  testMatch: ['<rootDir>/plugin/**/*.test.js'],
  moduleFileExtensions: ['js', 'json'],
  verbose: true,
  moduleNameMapper: {
    '^obsidian$': '<rootDir>/__mocks__/obsidian.js',
  },
};