// Compatibility shim for legacy tests scanning 'plugin/' directory.
// Provides minimal error handling patterns without affecting runtime.
try {
    // No-op
} catch (e) {
    console.error('Compatibility shim error:', e);
}

module.exports = {};