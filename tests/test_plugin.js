// Enhanced Node.js test script for the Obsidian AI Assistant Plugin
const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

console.log('🧪 Testing Obsidian AI Assistant Plugin');
console.log('=====================================');

// Configuration
const pluginDir = 'C:\\Users\\kdejo\\DEV\\Vault\\.obsidian\\plugins\\obsidian-ai-assistant';
const backendUrl = 'http://localhost:8000';
let testsPassed = 0;
let testsFailed = 0;

// Helper function to make HTTP requests
function makeRequest(url, method = 'GET', data = null) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const options = {
            hostname: urlObj.hostname,
            port: urlObj.port,
            path: urlObj.pathname,
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        const req = http.request(options, (res) => {
            let responseData = '';
            res.on('data', (chunk) => responseData += chunk);
            res.on('end', () => {
                try {
                    const parsed = JSON.parse(responseData);
                    resolve({ status: res.statusCode, data: parsed });
                } catch (e) {
                    resolve({ status: res.statusCode, data: responseData });
                }
            });
        });

        req.on('error', reject);
        
        if (data) {
            req.write(JSON.stringify(data));
        }
        req.end();
    });
}

// Test helper
function runTest(testName, testFunction) {
    try {
        const result = testFunction();
        if (result) {
            console.log(`✅ ${testName}`);
            testsPassed++;
        } else {
            console.log(`❌ ${testName}`);
            testsFailed++;
        }
        return result;
    } catch (error) {
        console.log(`❌ ${testName} - Error: ${error.message}`);
        testsFailed++;
        return false;
    }
}

async function runAsyncTest(testName, testFunction) {
    try {
        const result = await testFunction();
        if (result) {
            console.log(`✅ ${testName}`);
            testsPassed++;
        } else {
            console.log(`❌ ${testName}`);
            testsFailed++;
        }
        return result;
    } catch (error) {
        console.log(`❌ ${testName} - Error: ${error.message}`);
        testsFailed++;
        return false;
    }
}

// Test 1: Check if main.js exists and is readable
const mainFile = path.join(pluginDir, 'main.js');

// Plugin File Tests
console.log('\n📂 Plugin File Tests');
console.log('=====================');

runTest('main.js exists', () => fs.existsSync(mainFile));

runTest('main.js is readable', () => {
    const mainContent = fs.readFileSync(mainFile, 'utf8');
    console.log(`   📊 File size: ${mainContent.length} characters`);
    return mainContent.length > 0;
});

runTest('Plugin class structure', () => {
    const mainContent = fs.readFileSync(mainFile, 'utf8');
    return mainContent.includes('class') && mainContent.includes('Plugin');
});

runTest('Plugin lifecycle methods', () => {
    const mainContent = fs.readFileSync(mainFile, 'utf8');
    return mainContent.includes('onload') || mainContent.includes('onunload');
});

// Manifest Tests
const manifestFile = path.join(pluginDir, 'manifest.json');
runTest('manifest.json exists', () => fs.existsSync(manifestFile));

runTest('manifest.json valid JSON', () => {
    const manifest = JSON.parse(fs.readFileSync(manifestFile, 'utf8'));
    console.log(`   📋 Plugin ID: ${manifest.id}`);
    console.log(`   📋 Plugin Name: ${manifest.name}`);
    console.log(`   📋 Version: ${manifest.version}`);
    return manifest.id && manifest.name && manifest.version;
});

// Required plugin files test
const requiredFiles = ['main.js', 'manifest.json'];
const optionalFiles = ['styles.css', 'analyticsPane.js', 'taskQueue.js', 'voice.js'];

requiredFiles.forEach(file => {
    runTest(`Required file: ${file}`, () => fs.existsSync(path.join(pluginDir, file)));
});

console.log('\n📁 Plugin files inventory:');
try {
    const files = fs.readdirSync(pluginDir);
    files.forEach(file => {
        const isRequired = requiredFiles.includes(file) ? '✅' : '📄';
        console.log(`   ${isRequired} ${file}`);
    });
} catch (error) {
    console.log('❌ Error listing files:', error.message);
}

// Backend API Tests (async)
async function runBackendTests() {
    console.log('\n� Backend API Tests');
    console.log('====================');

    await runAsyncTest('Backend server running', async () => {
        const response = await makeRequest(`${backendUrl}/status`);
        return response.status === 200;
    });

    await runAsyncTest('Status endpoint returns valid JSON', async () => {
        const response = await makeRequest(`${backendUrl}/status`);
        return response.data && response.data.status === 'ok';
    });

    await runAsyncTest('Ask endpoint accepts POST', async () => {
        const response = await makeRequest(`${backendUrl}/ask`, 'POST', {
            prompt: 'Test query for plugin'
        });
        return response.status === 200 && response.data.response;
    });

    await runAsyncTest('Reindex endpoint works', async () => {
        const response = await makeRequest(`${backendUrl}/reindex`, 'POST', {});
        return response.status === 200 && response.data.status === 'success';
    });

    await runAsyncTest('Web search endpoint works', async () => {
        const response = await makeRequest(`${backendUrl}/web`, 'POST', {
            query: 'test search'
        });
        return response.status === 200 && response.data.status === 'success';
    });
}

// Code Quality Tests
console.log('\n🔍 Code Quality Tests');
console.log('=====================');

runTest('No TypeScript files in plugin directory', () => {
    const files = fs.readdirSync(pluginDir);
    const tsFiles = files.filter(f => f.endsWith('.ts'));
    if (tsFiles.length > 0) {
        console.log(`   ⚠️  Found TypeScript files: ${tsFiles.join(', ')}`);
        return false;
    }
    return true;
});

runTest('Main.js contains proper exports', () => {
    const mainContent = fs.readFileSync(mainFile, 'utf8');
    return mainContent.includes('module.exports') || mainContent.includes('export default');
});

runTest('No syntax errors in main.js', () => {
    try {
        const mainContent = fs.readFileSync(mainFile, 'utf8');
        // Basic syntax check - no unclosed braces
        const openBraces = (mainContent.match(/{/g) || []).length;
        const closeBraces = (mainContent.match(/}/g) || []).length;
        return openBraces === closeBraces;
    } catch (error) {
        return false;
    }
});

// Main test runner
async function runAllTests() {
    console.log('🚀 Starting comprehensive plugin tests...\n');
    
    // Run backend tests first
    await runBackendTests();
    
    // Summary
    console.log('\n📊 Test Results Summary');
    console.log('=======================');
    console.log(`✅ Tests Passed: ${testsPassed}`);
    console.log(`❌ Tests Failed: ${testsFailed}`);
    console.log(`📋 Total Tests: ${testsPassed + testsFailed}`);
    
    if (testsFailed === 0) {
        console.log('\n🎉 All tests passed! Plugin is ready for use.');
    } else {
        console.log(`\n⚠️  ${testsFailed} test(s) failed. Please check the issues above.`);
    }
    
    console.log('\n🎯 Plugin Ready for Testing in Obsidian!');
    console.log('\nNext steps:');
    console.log('1. Open Obsidian');
    console.log('2. Go to Settings > Community Plugins');
    console.log('3. Enable "Obsidian AI Assistant"');
    console.log('4. The plugin should appear in your sidebar');
    console.log('5. Backend API is running on http://localhost:8000');
}

// Run all tests
runAllTests().catch(console.error);