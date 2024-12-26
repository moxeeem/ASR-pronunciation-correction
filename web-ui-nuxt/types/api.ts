
export interface TranscriptionResult {
  real_transcription: string;
  transcription: string;
  correct_letters: string;
  accuracy: number;
}

export interface TranscriptionResponse {
  result: TranscriptionResult;
}
