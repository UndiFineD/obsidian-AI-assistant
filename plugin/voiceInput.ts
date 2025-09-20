import { TaskQueue } from './taskQueue';

export class VoiceInput {
    private taskQueue: TaskQueue;
    private recognition: any;

    constructor(taskQueue: TaskQueue) {
        this.taskQueue = taskQueue;
        if ('webkitSpeechRecognition' in window) {
            this.recognition = new (window as any).webkitSpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onresult = (event: any) => {
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

