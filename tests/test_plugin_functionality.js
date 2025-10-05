// Test the plugin's core functionality
const fs = require('fs');
const path = require('path');

// Read the main plugin file
const pluginPath = path.join(__dirname, 'plugin', 'main.js');
const pluginContent = fs.readFileSync(pluginPath, 'utf8');

console.log('🧪 Testing Obsidian AI Assistant Plugin');
console.log('========================================');

// Test 1: Check if plugin exports the correct class
console.log('\n✅ Test 1: Plugin Structure');
if (pluginContent.includes('class ObsidianAIAssistantPlugin extends Plugin')) {
    console.log('   ✓ Plugin class properly extends Obsidian Plugin');
} else {
    console.log('   ✗ Plugin class structure issue');
}

// Test 2: Check for required methods
const requiredMethods = ['onload', 'onunload', 'addRibbonIcon'];
console.log('\n✅ Test 2: Required Methods');
requiredMethods.forEach(method => {
    if (pluginContent.includes(method)) {
        console.log(`   ✓ ${method} method found`);
    } else {
        console.log(`   ✗ ${method} method missing`);
    }
});

// Test 3: Check for AI functionality
console.log('\n✅ Test 3: AI Features');
const aiFeatures = [
    'AIModal',
    'checkBackendStatus',
    'startVoiceRecording',
    'stopVoiceRecording',
    'sendToBackend'
];
aiFeatures.forEach(feature => {
    if (pluginContent.includes(feature)) {
        console.log(`   ✓ ${feature} functionality found`);
    } else {
        console.log(`   ✗ ${feature} functionality missing`);
    }
});

// Test 4: Check for UI elements
console.log('\n✅ Test 4: UI Components');
const uiElements = [
    'ai-status-dot',
    'ai-mic-button',
    'ai-question-input',
    'ai-ask-button'
];
uiElements.forEach(element => {
    if (pluginContent.includes(element)) {
        console.log(`   ✓ ${element} UI element found`);
    } else {
        console.log(`   ✗ ${element} UI element missing`);
    }
});

// Test 5: Check manifest.json
console.log('\n✅ Test 5: Plugin Manifest');
try {
    const manifestPath = path.join(__dirname, 'plugin', 'manifest.json');
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    
    if (manifest.id === 'obsidian-ai-assistant') {
        console.log('   ✓ Plugin ID correct');
    }
    if (manifest.name === 'Obsidian AI Assistant') {
        console.log('   ✓ Plugin name correct');
    }
    if (manifest.version) {
        console.log(`   ✓ Version: ${manifest.version}`);
    }
} catch (error) {
    console.log('   ✗ Manifest file error:', error.message);
}

// Test 6: Check CSS styles
console.log('\n✅ Test 6: Styling');
try {
    const stylesPath = path.join(__dirname, 'plugin', 'styles.css');
    const styles = fs.readFileSync(stylesPath, 'utf8');
    
    const cssClasses = ['.ai-status-dot', '.ai-mic-button', '.ai-modal'];
    cssClasses.forEach(cssClass => {
        if (styles.includes(cssClass)) {
            console.log(`   ✓ ${cssClass} styling found`);
        } else {
            console.log(`   ✗ ${cssClass} styling missing`);
        }
    });
} catch (error) {
    console.log('   ✗ Styles file error:', error.message);
}

console.log('\n🎉 Plugin testing complete!');
console.log('📋 Next steps:');
console.log('   1. Open Obsidian');
console.log('   2. Go to Settings > Community plugins');
console.log('   3. Enable "Obsidian AI Assistant"');
console.log('   4. Look for the AI Assistant icon in the ribbon');
console.log('   5. Test the status indicator and microphone button');