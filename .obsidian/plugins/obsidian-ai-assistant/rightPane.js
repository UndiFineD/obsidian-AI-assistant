// AI Assistant Right Pane Plugin UI
// Covers full right pane, includes backend status, reload, voice/text input, cancel, analytics, task queue, login, and config

const { Plugin, WorkspaceLeaf, Setting, Notice } = require("obsidian");
const BackendClient = require("./backendClient.js");

class AIRightPaneView {
    constructor(app, plugin) {
        this.app = app;
        this.plugin = plugin;
        this.container = null;
        this.isLoggedIn = false;
        this.authToken = null;
        this.currentUser = null;
        this.isVoiceRecording = false;
        this.cancelController = null;

        // Initialize backend client with auth token getter
        this.backendClient = new BackendClient(plugin.settings.backendUrl, () => this.authToken);

        // Integrate analytics, task queue, and voice
        const { TaskQueue } = require("./taskQueue.js");
        const { VoiceInput } = require("./voiceInput.js");
        const { VoiceRecorder } = require("./voice.js");
        this.taskQueue = new TaskQueue(plugin.settings.backendUrl, app, () => this.authToken);
        this.voiceInput = new VoiceInput(this.taskQueue);
        this.voiceRecorder = new VoiceRecorder(plugin.settings.backendUrl, () => this.authToken);
        this.analyticsState = {
            processedNotes: {},
            qaHistory: [],
            modelUsage: {},
            lastUpdated: new Date()
        };

        // Auto-refresh analytics every 30 seconds using backend client polling
        this.analyticsPollingId = null;
        this.startAnalyticsPolling();
    }

    async open() {
        // Create right pane container
        if(this.container) this.container.remove();
        this.container = this.app.workspace.getRightPaneContainer();
        this.container.empty();
        this.container.addClass("ai-assistant-pane");

        // Backend status
        const statusDiv = this.container.createEl("div", { cls: "ai-backend-status" });
        await this.renderBackendStatus(statusDiv);

        // Login section
        const loginDiv = this.container.createEl("div", { cls: "ai-login-section" });
        this.renderLogin(loginDiv);

        // Config section
        const configDiv = this.container.createEl("div", { cls: "ai-config-section" });
        this.renderConfig(configDiv);

        // Voice/text input
        const inputDiv = this.container.createEl("div", { cls: "ai-input-section" });
        this.renderInput(inputDiv);

        // Cancel button
        const cancelBtn = this.container.createEl("button", { text: "Cancel", cls: "ai-cancel-btn" });
        cancelBtn.onclick = () => this.cancelCurrentTask();

        // Analytics
        const analyticsDiv = this.container.createEl("div", { cls: "ai-analytics-section" });
        this.renderAnalytics(analyticsDiv);

        // Task queue
        const queueDiv = this.container.createEl("div", { cls: "ai-taskqueue-section" });
        this.renderTaskQueue(queueDiv);
    }

    async renderBackendStatus(div) { div.empty();
        let statusText = "Checking backend...";
        let offline = false;
        try { await this.backendClient.get("/status");
            statusText = "Backend is online";
        } catch(e) { statusText = "Backend is offline";
            offline = true;
        }
        div.createEl("span", { text: statusText });
        const reloadBtn = div.createEl("button", { text: offline ? "Check again" : "Reload config" });
        reloadBtn.onclick = async() => { reloadBtn.disabled = true;
            reloadBtn.textContent = offline ? "Checking..." : "Reloading...";
            try {
                if (offline) {
                    await this.backendClient.get("/status");
                } else {
                    await this.backendClient.post("/api/config/reload", {});
                    new Notice("Backend config reloaded.");
                }
            } catch(err) { new Notice(offline ? "Backend is offline. Please start the server." : "Failed to reload config.");
            }
            reloadBtn.disabled = false;
            reloadBtn.textContent = offline ? "Check again" : "Reload config";
            await this.renderBackendStatus(div);
        };
    }

    renderLogin(div) { div.empty();

        if(this.isLoggedIn) { div.createEl("span", { text: `Logged in as: ${ this.currentUser }` });
            const logoutBtn = div.createEl("button", { text: "Logout" });
            logoutBtn.onclick = async() => { await this.logout();
                this.renderLogin(div);
            };
        } else { div.createEl("label", { text: "User Login:" });
            const userInput = div.createEl("input", { type: "text", placeholder: "Username", cls: "ai-login-input" });
            const passInput = div.createEl("input", { type: "password", placeholder: "Password", cls: "ai-login-input" });
            const loginBtn = div.createEl("button", { text: "Login" });

            loginBtn.onclick = async() => { const username = userInput.value.trim();
                const password = passInput.value;

                if(!username || !password) { new Notice("Please enter both username and password.");
                    return;
                }

                loginBtn.disabled = true;
                loginBtn.textContent = "Logging in...";

                try { const success = await this.authenticate(username, password);
                    if(success) { this.renderLogin(div);
                        new Notice("Login successful!");
                        this.refreshAnalytics();
                    } else { new Notice("Login failed. Please check your credentials.");
                    }
                } catch(error) { new Notice(`Login error: ${ error.message }`);
                }

                loginBtn.disabled = false;
                loginBtn.textContent = "Login";
            };

            // Enter key to login
            passInput.addEventListener('keypress', (e) => { if(e.key === 'Enter') { loginBtn.click();
                }
            });
        }
    }

    async authenticate(username, password) { try { const data = await this.backendClient.post("/api/auth/login", { username, password });
            this.authToken = data.token;
            this.currentUser = username;
            this.isLoggedIn = true;

            // Start real-time polling after successful login
            this.startAnalyticsPolling();

            return true;
        } catch(error) { console.error("Authentication error:", error);
            new Notice("Authentication failed: " + error.message);
            return false;
        }
    }

    async logout() { try { if(this.authToken) { await this.backendClient.post("/api/auth/logout", {});
            }
        } catch(error) { console.error("Logout error:", error);
        }

        this.authToken = null;
        this.currentUser = null;
        this.isLoggedIn = false;

        // Stop real-time polling after logout
        this.stopAnalyticsPolling();

        new Notice("Logged out successfully.");
    }

    renderConfig(div) { div.empty();
        div.createEl("label", { text: "Backend Server:" });
        const serverInput = div.createEl("input", { type: "text", value: this.plugin.settings.backendUrl });
        serverInput.onchange = (e) => { this.plugin.settings.backendUrl = e.target.value;
            new Notice("Backend URL updated.");
        };
    }

    renderInput(div) { div.empty();
        div.createEl("label", { text: "Ask AI:" });
        const textInput = div.createEl("textarea", { placeholder: "Type your question...",
            cls: "ai-text-input",
            attr: { rows: "3" }
        });

        const buttonContainer = div.createEl("div", { cls: "ai-input-buttons" });

        const askBtn = buttonContainer.createEl("button", { text: "Ask", cls: "ai-ask-btn" });
        askBtn.onclick = async() => { const question = textInput.value.trim();
            if(question) { askBtn.disabled = true;
                askBtn.textContent = "Asking...";

                try { await this.askQuestion(question);
                    textInput.value = "";
                    this.renderTaskQueue(div.parentElement.querySelector('.ai-taskqueue-section'));
                } catch(error) { new Notice(`Error: ${ error.message }`);
                }

                askBtn.disabled = false;
                askBtn.textContent = "Ask";
            }
        };

        const voiceBtn = buttonContainer.createEl("button", { text: this.isVoiceRecording ? "Stop Recording" : "Voice",
            cls: this.isVoiceRecording ? "ai-voice-btn-active" : "ai-voice-btn"
        });
        voiceBtn.onclick = async() => { if(this.isVoiceRecording) { await this.stopVoiceRecording();
            } else { await this.startVoiceRecording();
            }

            // Update button appearance
            voiceBtn.textContent = this.isVoiceRecording ? "Stop Recording" : "Voice";
            voiceBtn.className = this.isVoiceRecording ? "ai-voice-btn-active" : "ai-voice-btn";
        };

        // Enter key to ask(Ctrl+Enter for new line)
        textInput.addEventListener('keypress', (e) => { if(e.key === 'Enter' && !e.ctrlKey) { e.preventDefault();
                askBtn.click();
            }
        });
    }

    async askQuestion(question) { const headers = { "Content-Type": "application/json" };
        if(this.authToken) { headers["Authorization"] = `Bearer ${ this.authToken }`;
        }

        this.cancelController = new AbortController();

        try { const data = await this.backendClient.post("/ask", { question: question,
                prefer_fast: true,
                include_sources: true }, this.cancelController.signal);

            // Add to analytics
            this.analyticsState.qaHistory.push({ timestamp: new Date().toISOString(),
                prompt: question,
                answer: data.answer,
                model: data.model_used || "unknown",
                response_time: data.response_time || 0 });

            // Update model usage
            const model = data.model_used || "unknown";
            this.analyticsState.modelUsage[model] = (this.analyticsState.modelUsage[model] || 0) + 1;

            // Add to task queue for tracking
            this.taskQueue.addTask({ type: "ask", content: question, status: "completed" });

            new Notice("Question answered successfully!");
            return data;
        } catch(error) { if(error.name === 'AbortError') { new Notice("Question cancelled.");
            } else { new Notice("Error asking question: " + error.message);
                throw error;
            }
        } finally { this.cancelController = null;
        }
    }

    async startVoiceRecording() { try { this.isVoiceRecording = true;
            await this.voiceRecorder.startRecording();
            new Notice("🎙️ Recording started. Speak now...");
        } catch(error) { this.isVoiceRecording = false;
            new Notice(`Voice recording error: ${ error.message }`);
        }
    }

    async stopVoiceRecording() { try { const audioBlob = await this.voiceRecorder.stopRecording();
            this.isVoiceRecording = false;

            if(audioBlob.size > 0) { new Notice("🎙️ Processing voice input...");

                const transcription = await this.voiceRecorder.sendToBackend(audioBlob,
                    this.plugin.settings.backendUrl,
                    "offline"
                );

                if(transcription) {
                    // Fill the text input with transcription
                    const textInput = this.container.querySelector('.ai-text-input');
                    if(textInput) { textInput.value = transcription;
                    }
                    new Notice(`Voice transcribed: "${ transcription }"`);
                } else { new Notice("No speech detected.");
                }
            }
        } catch(error) { this.isVoiceRecording = false;
            new Notice(`Voice processing error: ${ error.message }`);
        }
    }

    cancelCurrentTask() { let cancelled = false;

        // Cancel current API request
        if(this.cancelController) { this.cancelController.abort();
            this.cancelController = null;
            cancelled = true;
        }

        // Stop voice recording
        if(this.isVoiceRecording) { this.stopVoiceRecording();
            cancelled = true;
        }

        // Pause task queue
        if(this.taskQueue.isRunning) { this.taskQueue.pauseQueue();
            cancelled = true;
        }

        if(cancelled) { new Notice("Current operations cancelled.");
        } else { new Notice("No active operations to cancel.");
        }
    }

    renderAnalytics(div) { div.empty();
        const header = div.createEl("div", { cls: "analytics-header" });
        header.createEl("h3", { text: "Analytics" });

        const refreshBtn = header.createEl("button", { text: "Refresh", cls: "analytics-refresh-btn" });
        refreshBtn.onclick = () => this.refreshAnalytics();

        // Summary stats
        const statsDiv = div.createEl("div", { cls: "analytics-stats" });
        statsDiv.createEl("p", { text: `📄 Processed notes: ${ Object.keys(this.analyticsState.processedNotes).length }` });
        statsDiv.createEl("p", { text: `💬 QA interactions: ${ this.analyticsState.qaHistory.length }` });
        statsDiv.createEl("p", { text: `🤖 Models used: ${ Object.keys(this.analyticsState.modelUsage).length }` });

        if(this.analyticsState.lastUpdated) { statsDiv.createEl("p", { text: `🔄 Last updated: ${ this.analyticsState.lastUpdated.toLocaleTimeString()}`,
            cls: "analytics-timestamp"
            });
        }

        // Model usage breakdown
        if(Object.keys(this.analyticsState.modelUsage).length > 0) { div.createEl("h4", { text: "Model Usage" });
            const modelDiv = div.createEl("div", { cls: "model-usage" });
            Object.entries(this.analyticsState.modelUsage).forEach(([model, count]) => { const modelItem = modelDiv.createEl("div", { cls: "model-item" });
                modelItem.createEl("span", { text: `${ model }: ` });
                modelItem.createEl("strong", { text: `${ count } calls` });
            });
        }

        // Recent QA history
        if(this.analyticsState.qaHistory.length > 0) { div.createEl("h4", { text: "Recent Questions" });
            const historyDiv = div.createEl("div", { cls: "qa-history" });

            const recentQuestions = this.analyticsState.qaHistory.slice(-5).reverse();
            recentQuestions.forEach(entry => { const entryDiv = historyDiv.createEl("div", { cls: "qa-entry" });
                const timestamp = new Date(entry.timestamp).toLocaleTimeString();
                entryDiv.createEl("div", { text: `[${ timestamp }] ${ entry.prompt.substring(0, 50)}${ entry.prompt.length > 50 ? '...' : ''}`,
                    cls: "qa-question"
                });
                if(entry.response_time) { entryDiv.createEl("div", { text: `⚡ ${ entry.response_time }ms | Model: ${ entry.model }`,
                    cls: "qa-meta"
                    });
                }
            });
        }
    }

    async refreshAnalytics() {
        // Poll lightweight performance metrics from backend when logged in
        if(!this.isLoggedIn) return;

        try {
            const resp = await this.backendClient.get("/api/performance/metrics");
            // Merge metrics snapshot and timestamp
            this.analyticsState = {
                ...this.analyticsState,
                metrics: resp?.metrics || {},
                lastUpdated: new Date()
            };
            const analyticsDiv = this.container?.querySelector('.ai-analytics-section');
            if(analyticsDiv) { this.renderAnalytics(analyticsDiv); }
        } catch(error) {
            console.error("Failed to refresh analytics:", error);
        }
    }

    startAnalyticsPolling() {
        if(!this.isLoggedIn || this.analyticsPollingId) return;

        this.analyticsPollingId = this.backendClient.startPolling(
            "/api/performance/metrics",
            30000,
            (data) => {
                this.analyticsState = {
                    ...this.analyticsState,
                    metrics: data?.metrics || {},
                    lastUpdated: new Date()
                };
                const analyticsDiv = this.container?.querySelector('.ai-analytics-section');
                if(analyticsDiv) { this.renderAnalytics(analyticsDiv); }
            },
            (error) => {
                console.error("Analytics polling error:", error);
                if(error.message.includes('401') || error.message.includes('403')) {
                    this.stopAnalyticsPolling();
                }
            }
        );
    }

    stopAnalyticsPolling() { if(this.analyticsPollingId) { this.backendClient.stopPolling(this.analyticsPollingId);
            this.analyticsPollingId = null;
        }
    }

    renderTaskQueue(div) { div.empty();
        const header = div.createEl("div", { cls: "taskqueue-header" });
        header.createEl("h3", { text: "Task Queue" });

        const controls = header.createEl("div", { cls: "taskqueue-controls" });

        const startBtn = controls.createEl("button", { text: "Start", cls: "queue-start-btn" });
        startBtn.onclick = async() => { await this.taskQueue.startQueue();
            this.renderTaskQueue(div);
        };

        const pauseBtn = controls.createEl("button", { text: "Pause", cls: "queue-pause-btn" });
        pauseBtn.onclick = () => { this.taskQueue.pauseQueue();
            this.renderTaskQueue(div);
        };

        const clearBtn = controls.createEl("button", { text: "Clear", cls: "queue-clear-btn" });
        clearBtn.onclick = () => { this.taskQueue.queue = [];
            this.taskQueue.filteredQueue = [];
            new Notice("Task queue cleared.");
            this.renderTaskQueue(div);
        };

        // Queue status
        const statusDiv = div.createEl("div", { cls: "queue-status" });
        const queueLength = this.taskQueue.getTasks().length;
        const isRunning = this.taskQueue.isRunning;

        statusDiv.createEl("p", { text: `Status: ${ isRunning ? '🟢 Running' : '🔴 Stopped'} | Tasks: ${ queueLength }`,
            cls: "queue-status-text"
        });

        // Task list
        const tasks = this.taskQueue.getTasks();
        if(tasks.length === 0) { div.createEl("p", { text: "No tasks in queue.", cls: "empty-queue" });
            return;
        }

        const taskList = div.createEl("div", { cls: "task-list" });
        tasks.slice(0, 10).forEach((task, index) => { const taskEl = taskList.createEl("div", { cls: `ai-task-item ${ task.status || 'pending'}`
            });

            const taskHeader = taskEl.createEl("div", { cls: "task-header" });
            taskHeader.createEl("strong", { text: `[${ task.type.toUpperCase()}] ` });

            if(task.priority && task.priority > 1) { taskHeader.createEl("span", { text: `⭐${ task.priority } `, cls: "task-priority" });
            }

            const removeBtn = taskHeader.createEl("button", { text: "✕", cls: "task-remove-btn" });
            removeBtn.onclick = () => { this.taskQueue.queue.splice(index, 1);
                this.taskQueue.filteredQueue = [...this.taskQueue.queue];
                this.renderTaskQueue(div);
                new Notice("Task removed.");
            };

            taskEl.createEl("div", { text: task.content, cls: "task-content" });

            if(task.notePath) { taskEl.createEl("div", { text: `📝 Note: ${ task.notePath }`,
                cls: "ai-task-note-path"
            });
            }

            if(task.timestamp) { taskEl.createEl("div", { text: `⏰ ${ new Date(task.timestamp).toLocaleTimeString()}`,
                cls: "task-timestamp"
            });
            }
        });

        if(tasks.length > 10) { div.createEl("p", { text: `... and ${ tasks.length - 10 } more tasks`,
            cls: "task-overflow"
            });
        }
    }

    // Cleanup method for proper resource management
    destroy() {
        // Stop real-time polling
        this.stopAnalyticsPolling();

        if(this.cancelController) { this.cancelController.abort();
            this.cancelController = null;
        }

        if(this.isVoiceRecording) { this.stopVoiceRecording().catch(console.error);
        }

        if(this.taskQueue) { this.taskQueue.pauseQueue();
        }
    }
}

module.exports = AIRightPaneView;
