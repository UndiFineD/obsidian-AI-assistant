// plugin/voice.ts
export class VoiceRecorder {
  mediaRecorder: MediaRecorder | null = null;
  chunks: Blob[] = [];

  async startRecording() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    this.mediaRecorder = new MediaRecorder(stream);

    this.chunks = [];
    this.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.chunks.push(e.data);
    };

    this.mediaRecorder.start();
    console.log("🎙️ Recording started");
  }

  async stopRecording(): Promise<Blob> {
    return new Promise((resolve) => {
      if (!this.mediaRecorder) return resolve(new Blob());

      this.mediaRecorder.onstop = () => {
        const blob = new Blob(this.chunks, { type: "audio/wav" });
        resolve(blob);
      };
      this.mediaRecorder.stop();
    });
  }

  async sendToBackend(blob: Blob, backendUrl: string): Promise<string> {
    const formData = new FormData();
    formData.append("file", blob, "voice.wav");

    const res = await fetch(`${backendUrl}/api/voice_transcribe`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    return data.transcription || "";
  }
}
