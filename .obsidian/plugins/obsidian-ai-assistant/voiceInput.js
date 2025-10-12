const { TaskQueue } = require('./taskQueue.js');

class VoiceInput {
    constructor(taskQueue) {
        this.taskQueue = taskQueue;
        this.recognition = null;

        if ('webkitSpeechRecognition' in window) {
            this.recognition = new window.webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.taskQueue.addTask({ type: 'ask', content: transcript });
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
            };
        } else {
            console.log('Speech recognition not supported in this browser');
        }
    }

    startListening() {
        if (this.recognition) {
            try {
                this.recognition.start();
            } catch (error) {
                console.error('Error starting speech recognition:', error);
            }
        }
    }

    stopListening() {
        if (this.recognition) {
            try {
                this.recognition.stop();
            } catch (error) {
                console.error('Error stopping speech recognition:', error);
            }
        }
    }
}

module.exports = { VoiceInput };
