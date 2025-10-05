const { TaskQueue } = require('./taskQueue');

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
                this.taskQueue.addTask({type: 'ask', content: transcript});
            };
        }
    }

    startListening() {
        if (this.recognition) this.recognition.start();
    }

    stopListening() {
        if (this.recognition) this.recognition.stop();
    }
}

module.exports = { VoiceInput };