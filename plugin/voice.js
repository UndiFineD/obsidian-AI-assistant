// plugin/voice.js
const BackendClient = require("./backendClient.js");

class VoiceRecorder { constructor(backendUrl, getAuthToken = null) { this.mediaRecorder = null;
    this.chunks = [];
    this.backendClient = backendUrl ? new BackendClient(backendUrl, getAuthToken) : null;
    }

    async startRecording() { const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.mediaRecorder = new MediaRecorder(stream);

    this.chunks = [];
    this.mediaRecorder.ondataavailable = (e) => { if(e.data.size > 0) this.chunks.push(e.data);
    };

    this.mediaRecorder.start();
    console.log("🎙️ Recording started");
    }

    async stopRecording() { return new Promise((resolve) => { if(!this.mediaRecorder) return resolve(new Blob());

        this.mediaRecorder.onstop = () => { const blob = new Blob(this.chunks, { type: "audio/wav" });
        resolve(blob);
        };
        this.mediaRecorder.stop();
    });
    }

    async sendToBackend(blob, backendUrl, voiceMode) {
    // Convert blob to base64 for JSON API
    const arrayBuffer = await blob.arrayBuffer();
    const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));

    const client = this.backendClient || new BackendClient(backendUrl);
    const data = await client.post("/transcribe", { audio_data: base64,
        format: "wav",
        language: "en"
    });

    return data.transcription || "";
    }
}

module.exports = { VoiceRecorder };