export interface TranscriptionResponse {
  result: {
    real_transcription: string;
    transcription: string;
    correct_letters: string;
    accuracy: number;
  }
}