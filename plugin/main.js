const { App, Modal, Notice, Plugin, PluginSettingTab, Setting } = require("obsidian");

// Default settings for the plugin
const DEFAULT_SETTINGS = {
  backendUrl: "http://localhost:8000"
};

// Simple modal for AI interaction
class AIModal extends Modal {
  constructor(app, plugin) {
    super(app);
    this.plugin = plugin;
  }

  onOpen() {
    const { contentEl } = this;
    contentEl.empty();

    // Header with title and status indicator
    const headerContainer = contentEl.createDiv({ cls: "ai-header-container" });
    
    headerContainer.createEl("h2", { text: "AI Assistant" });
    
    // Status indicator
    const statusContainer = headerContainer.createDiv({ cls: "ai-status-container" });
    
    const statusDot = statusContainer.createEl("div", { cls: "ai-status-dot checking" });
    
    const statusText = statusContainer.createEl("span", { 
      text: "Checking...", 
      cls: "ai-status-text",
      attr: { style: "color: var(--text-muted);" }
    });
    
    // Refresh status button
    const refreshBtn = statusContainer.createEl("button", {
      text: "🔄",
      attr: { 
        style: "background: none; border: none; cursor: pointer; font-size: 14px; padding: 2px; opacity: 0.7;",
        title: "Refresh backend status"
      }
    });
    
    refreshBtn.onclick = () => this.checkBackendStatus(statusDot, statusText, askButton, micButton);

    const inputContainer = contentEl.createDiv();
    const textarea = inputContainer.createEl("textarea", {
      placeholder: "Ask your AI assistant a question...",
      attr: { rows: "4", style: "width: 100%; margin-bottom: 10px;" }
    });

    const buttonContainer = contentEl.createDiv();
    const askButton = buttonContainer.createEl("button", { text: "Ask AI" });
    const micButton = buttonContainer.createEl("button", { 
      text: "🎤", 
      cls: "ai-mic-button",
      attr: { 
        title: "Voice input - Hold to record"
      }
    });
    const closeButton = buttonContainer.createEl("button", { text: "Close" });
    closeButton.style.marginLeft = "10px";

    // Check backend status
    this.checkBackendStatus(statusDot, statusText, askButton, micButton);

    // Voice input functionality - Push to talk
    let isRecording = false;
    let mediaRecorder = null;
    let recordedChunks = [];

    // Push-to-talk: Start recording on mousedown/touchstart
    micButton.addEventListener('mousedown', async (e) => {
      e.preventDefault();
      if (!isRecording && !micButton.disabled) {
        await this.startVoiceRecording(micButton, textarea);
        isRecording = true;
      }
    });

    micButton.addEventListener('touchstart', async (e) => {
      e.preventDefault();
      if (!isRecording && !micButton.disabled) {
        await this.startVoiceRecording(micButton, textarea);
        isRecording = true;
      }
    });

    // Stop recording on mouseup/touchend/mouseleave
    const stopRecording = async () => {
      if (isRecording) {
        await this.stopVoiceRecording(micButton, textarea);
        isRecording = false;
      }
    };

    micButton.addEventListener('mouseup', stopRecording);
    micButton.addEventListener('mouseleave', stopRecording);
    micButton.addEventListener('touchend', stopRecording);
    micButton.addEventListener('touchcancel', stopRecording);

    // Prevent context menu on right click
    micButton.addEventListener('contextmenu', (e) => e.preventDefault());

    askButton.onclick = async () => {
      const question = textarea.value.trim();
      if (!question) {
        new Notice("Please enter a question");
        return;
      }

      askButton.disabled = true;
      askButton.textContent = "Processing...";

      try {
        await this.plugin.askAI(question);
      } finally {
        askButton.disabled = false;
        askButton.textContent = "Ask AI";
        this.close();
      }
    };

    closeButton.onclick = () => this.close();
  }

  async startVoiceRecording(micButton, textarea) {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);
      this.recordedChunks = [];

      this.mediaRecorder.addEventListener('dataavailable', event => {
        if (event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      });

      this.mediaRecorder.start();
      this.isRecording = true;

      // Update button appearance for push-to-talk
      micButton.textContent = "🔴";
      micButton.title = "Recording... Release to stop";
      micButton.addClass("recording");
      micButton.addClass("pressed");

      new Notice("🎤 Recording... Release button to stop", 2000);

    } catch (error) {
      console.error('Error starting voice recording:', error);
      
      // More specific error handling
      let errorMessage = 'Microphone access issue: ';
      if (error.name === 'NotAllowedError') {
        errorMessage = '🎤 Microphone permission denied. Please:\n' +
                      '1. Click the microphone icon in your browser address bar\n' +
                      '2. Allow microphone access for this site\n' +
                      '3. Refresh the page and try again';
      } else if (error.name === 'NotFoundError') {
        errorMessage = '🎤 No microphone found. Please check your microphone is connected and try again.';
      } else if (error.name === 'NotSupportedError') {
        errorMessage = '🎤 Microphone not supported in this browser. Try Chrome, Firefox, or Edge.';
      } else if (error.name === 'NotReadableError') {
        errorMessage = '🎤 Microphone is being used by another application. Please close other apps using the mic.';
      } else {
        errorMessage = `🎤 Microphone error: ${error.message}. Check browser permissions and microphone settings.`;
      }
      
      new Notice(errorMessage, 8000);
      this.isRecording = false;
      
      // Reset button state on error
      micButton.textContent = "🎤";
      micButton.title = "Voice input - Hold to record";
      micButton.removeClass("recording");
      micButton.removeClass("pressed");
    }
  }

  async stopVoiceRecording(micButton, textarea) {
    if (!this.mediaRecorder || !this.isRecording) return;

    return new Promise((resolve) => {
      this.mediaRecorder.addEventListener('stop', async () => {
        const audioBlob = new Blob(this.recordedChunks, { type: 'audio/webm' });
        
        // Reset button appearance
        micButton.textContent = "🎤";
        micButton.title = "Voice input - Hold to record";
        micButton.removeClass("recording");
        micButton.removeClass("pressed");

        // Stop all audio tracks
        this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        
        new Notice("🎤 Recording stopped. Processing audio...", 2000);

        // For now, just indicate that we would process the audio
        // In a full implementation, this would send to speech-to-text service
        new Notice("Voice processing would happen here. For now, type your question manually.", 5000);
        
        // Focus back to textarea
        textarea.focus();
        
        resolve();
      });

      this.mediaRecorder.stop();
      this.isRecording = false;
    });
  }

  async checkBackendStatus(statusDot, statusText, askButton, micButton) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
      
      const response = await fetch(`${this.plugin.settings.backendUrl}/status`, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        // Server is online - green status
        statusDot.className = "ai-status-dot online";
        statusText.textContent = "Backend Online";
        statusText.style.color = "#22c55e";
        askButton.disabled = false;
        if (micButton) {
          micButton.disabled = false;
          micButton.title = "Voice input - Click to start recording";
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
      
    } catch (error) {
      // Server is offline - red status
      statusDot.className = "ai-status-dot offline";
      statusText.textContent = "Backend Offline";
      statusText.style.color = "#ef4444";
      askButton.disabled = true;
      askButton.title = "Backend server is not running. Start the server first.";
      if (micButton) {
        micButton.disabled = true;
        micButton.title = "Voice input unavailable - Backend server not running";
      }
    }
  }

  onClose() {
    const { contentEl } = this;
    contentEl.empty();
  }
}

// Main Plugin Class
class ObsidianAIAssistant extends Plugin {

  async onload() {
    console.log('Loading Obsidian AI Assistant Plugin');
    
    // Load settings
    await this.loadSettings();

    // Add ribbon icon
    this.addRibbonIcon('brain', 'AI Assistant', () => {
      new AIModal(this.app, this).open();
    });

    // Add command to command palette
    this.addCommand({
      id: 'open-ai-assistant',
      name: 'Open AI Assistant',
      callback: () => {
        new AIModal(this.app, this).open();
      }
    });

    // Add another command for quick ask
    this.addCommand({
      id: 'ask-ai-about-selection',
      name: 'Ask AI about selected text',
      editorCallback: async (editor) => {
        const selectedText = editor.getSelection();
        if (selectedText) {
          await this.askAI(`Explain this text: ${selectedText}`);
        } else {
          new Notice('No text selected');
        }
      }
    });

    // Add settings tab
    this.addSettingTab(new AIAssistantSettingTab(this.app, this));

    new Notice('AI Assistant Plugin loaded successfully!');
  }

  onunload() {
    console.log('Unloading Obsidian AI Assistant Plugin');
  }

  // Method to interact with AI backend
  async askAI(question) {
    try {
      new Notice('Asking AI...', 2000);

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

      const response = await fetch(`${this.settings.backendUrl}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          question: question,
          model_name: "qwen2.5-0.5b-instruct",
          max_tokens: 512
        }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.response) {
        // Create a new note with the AI response
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const fileName = `AI Response ${timestamp}.md`;
        
        const content = `# AI Response\n\n**Question:** ${question}\n\n**Answer:** ${data.response}\n\n---\n*Generated on: ${new Date().toLocaleString()}*`;
        
        await this.app.vault.create(fileName, content);
        new Notice(`AI response saved to: ${fileName}`);
      } else {
        new Notice('No response from AI backend');
      }

    } catch (error) {
      console.error('Error asking AI:', error);
      
      // Better error messages
      if (error.name === 'AbortError') {
        new Notice('Request timed out. Check if backend server is running.', 5000);
      } else if (error.message.includes('Failed to fetch') || error.message.includes('refused')) {
        new Notice(`Backend server not available. Please start the server at ${this.settings.backendUrl}`, 5000);
      } else {
        new Notice(`Error: ${error.message}`, 5000);
      }
    }
  }

  // Settings management
  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }
}

// Settings Tab
class AIAssistantSettingTab extends PluginSettingTab {
  constructor(app, plugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display() {
    const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "AI Assistant Settings" });

    new Setting(containerEl)
      .setName("Backend URL")
      .setDesc("URL of your AI backend server")
      .addText((text) =>
        text
          .setValue(this.plugin.settings.backendUrl)
          .onChange(async (value) => {
            this.plugin.settings.backendUrl = value;
            await this.plugin.saveSettings();
          })
      );
  }
}

module.exports = ObsidianAIAssistant;