const { App, Modal, Notice, Plugin, PluginSettingTab, Setting } = require("obsidian");

// Default settings for the plugin
const DEFAULT_SETTINGS = { backendUrl: "http://localhost: 8000"
};

// Simple modal for AI interaction
class AIModal extends Modal { constructor(app, plugin) { super(app);
    this.plugin = plugin;
    }

    onOpen() { const { contentEl } = this;
    contentEl.empty();

    contentEl.createEl("h2", { text: "AI Assistant" });

    const inputContainer = contentEl.createDiv();
    const textarea = inputContainer.createEl("textarea", { placeholder: "Ask your AI assistant a question...",
        attr: { rows: "4", style: "width: 100%; margin-bottom: 10px;" }
    });

    const buttonContainer = contentEl.createDiv();
    const askButton = buttonContainer.createEl("button", { text: "Ask AI" });
    const closeButton = buttonContainer.createEl("button", { text: "Close" });
    closeButton.style.marginLeft = "10px";

    askButton.onclick = async() => { const question = textarea.value.trim();
        if(!question) { new Notice("Please enter a question");
        return;
        }

        askButton.disabled = true;
        askButton.textContent = "Processing...";

        try { await this.plugin.askAI(question);
        } finally { askButton.disabled = false;
        askButton.textContent = "Ask AI";
        this.close();
        }
    };

    closeButton.onclick = () => this.close();
    }

    onClose() { const { contentEl } = this;
    contentEl.empty();
    }
}

// Main Plugin Class
class ObsidianAIAssistant extends Plugin { async onload() { console.log('Loading Obsidian AI Assistant Plugin');

    // Load settings
    await this.loadSettings();

    // Add ribbon icon
    this.addRibbonIcon('brain', 'AI Assistant', () => { new AIModal(this.app, this).open();
    });

    // Add command to command palette
    this.addCommand({ id: 'open-ai-assistant',
        name: 'Open AI Assistant',
        callback: () => { new AIModal(this.app, this).open();
        }
    });

    // Add another command for quick ask
    this.addCommand({ id: 'ask-ai-about-selection',
        name: 'Ask AI about selected text',
        editorCallback: async(editor) => { const selectedText = editor.getSelection();
        if(selectedText) { await this.askAI(`Explain this text: ${ selectedText }`);
        } else { new Notice('No text selected');
        }
        }
    });

    // Add settings tab
    this.addSettingTab(new AIAssistantSettingTab(this.app, this));

    new Notice('AI Assistant Plugin loaded successfully!');
    }

    onunload() { console.log('Unloading Obsidian AI Assistant Plugin');
    }

    // Method to interact with AI backend
    async askAI(question) { try { new Notice('Asking AI...', 2000);

        const response = await fetch(`${ this.settings.backendUrl }/ask`, { method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: question })
        });

        if(!response.ok) { throw new Error(`HTTP ${ response.status }: ${ response.statusText }`);
        }

        const data = await response.json();

        if(data.response) {
        // Create a new note with the AI response
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const fileName = `AI Response ${ timestamp }.md`;

        const content = `# AI Response\n\n**Question:** ${ question }\n\n**Answer:** ${ data.response }\n\n---\n*Generated on: ${ new Date().toLocaleString()}*`;

        await this.app.vault.create(fileName, content);
        new Notice(`AI response saved to: ${ fileName }`);
        } else { new Notice('No response from AI backend');
        }

    } catch(error) { console.error('Error asking AI:', error);
        new Notice(`Error: ${ error.message }`);
    }
    }

    // Settings management
    async loadSettings() { this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
    }

    async saveSettings() { await this.saveData(this.settings);
    }
}

// Settings Tab
class AIAssistantSettingTab extends PluginSettingTab { constructor(app, plugin) { super(app, plugin);
    this.plugin = plugin;
    }

    display() { const { containerEl } = this;
    containerEl.empty();
    containerEl.createEl("h2", { text: "AI Assistant Settings" });

    new Setting(containerEl)
        .setName("Backend URL")
        .setDesc("URL of your AI backend server")
        .addText((text) =>
        text
            .setValue(this.plugin.settings.backendUrl)
            .onChange(async(value) => { this.plugin.settings.backendUrl = value;
            await this.plugin.saveSettings();
            })
        );
    }
}

module.exports = ObsidianAIAssistant;