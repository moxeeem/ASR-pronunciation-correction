export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private chunks: Blob[] = [];
  private stream: MediaStream | null = null;

  async start(): Promise<void> {
    console.log('Starting recording...');
    
    try {
      // Запрашиваем доступ к микрофону с базовыми настройками
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      
      console.log('Got media stream:', this.stream);
      
      // Создаем MediaRecorder
      this.mediaRecorder = new MediaRecorder(this.stream);
      this.chunks = [];
      
      // Настраиваем обработчики событий
      this.mediaRecorder.ondataavailable = (event) => {
        console.log('Data available:', event.data.size);
        if (event.data.size > 0) {
          this.chunks.push(event.data);
        }
      };

      // Начинаем запись
      this.mediaRecorder.start();
      console.log('Recording started');
      
    } catch (error) {
      console.error('Error starting recording:', error);
      this.cleanup();
      throw error;
    }
  }

  async stop(): Promise<Blob> {
    console.log('Stopping recording...');
    
    if (!this.mediaRecorder) {
      throw new Error('No recording in progress');
    }

    return new Promise((resolve, reject) => {
      this.mediaRecorder!.onstop = () => {
        console.log('Recording stopped, chunks:', this.chunks.length);
        try {
          const blob = new Blob(this.chunks, { type: 'audio/webm' });
          console.log('Created blob:', blob.size);
          this.cleanup();
          resolve(blob);
        } catch (error) {
          console.error('Error creating blob:', error);
          reject(error);
        }
      };

      try {
        this.mediaRecorder!.stop();
      } catch (error) {
        console.error('Error stopping recorder:', error);
        reject(error);
      }
    });
  }

  private cleanup(): void {
    console.log('Cleaning up recorder');
    if (this.stream) {
      this.stream.getTracks().forEach(track => {
        track.stop();
        console.log('Track stopped:', track.kind);
      });
    }
    this.stream = null;
    this.mediaRecorder = null;
    this.chunks = [];
  }
}