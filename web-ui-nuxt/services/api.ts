import { TranscriptionResponse } from '~/types/api'

const config = useRuntimeConfig()

export async function transcribeSentence(audio: Blob, sentenceId: string): Promise<TranscriptionResponse> {
  const formData = new FormData()
  formData.append('audio', audio, 'recording.wav')
  formData.append('sentence_id', sentenceId)

  const response = await fetch(`${config.public.backendApiUrl}/api/transcribe_sentence`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error('Failed to transcribe sentence')
  }

  return response.json()
}