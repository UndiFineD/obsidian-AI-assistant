// Lightweight plugin test harness (Node.js)
// - Mocks Obsidian API via node_modules/obsidian (already added)
// - Loads .obsidian/plugins/obsidian-ai-assistant/main.js and runs onload()
// - Spins up a tiny local HTTP server to validate BackendClient.get

const http = require('http');
const path = require('path');

async function startMockBackend(port = 18080) {
    const server = http.createServer((req, res) => {
        if (req.url.startsWith('/status')) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ ok: true }));
        } else if (req.url.startsWith('/api/analytics')) {
            res.writeHead(200, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ qaHistory: [], modelUsage: {}, processedNotes: {} }));
        } else {
            res.writeHead(404, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'not found' }));
        }
    });
    await new Promise((resolve) => server.listen(port, resolve));
    return { server, url: `http://localhost:${port}` };
}

async function run() {
    process.env.DEBUG_PLUGIN_TESTS = '1';
    const { App } = require('obsidian');
    const app = new App();

    // Load plugin
    const PluginClass = require(path.join('..', 'plugin', 'main.js'));
    const plugin = new PluginClass(app);

    // Start mock backend
    const { server, url } = await startMockBackend();
    plugin.settings = { backendUrl: url, features: { enableVoice: false, allowNetwork: false } };

    console.log('Loading plugin...');
    await plugin.onload();
    console.log('Plugin loaded.');

    // Basic BackendClient check via settings tab helper usage paths is complex; call directly
    const BackendClient = require(path.join('..', 'plugin', 'backendClient.js'));
    const client = new BackendClient(url);
    const status = await client.get('/status');
    if (!status || !status.ok) throw new Error('BackendClient status check failed');
    console.log('BackendClient GET /status OK');

    // Cleanup
    await plugin.onunload?.();
    await new Promise((r) => server.close(r));
    console.log('Plugin test completed successfully');
}

run().catch((err) => {
    console.error('Plugin test failed:', err);
    process.exit(1);
});
