import { ref } from 'vue'

interface TranscriptionResult {
  real_transcription: string
  transcription: string
  correct_letters: string
  accuracy: number
}

interface TranscriptionResponse {
  result: TranscriptionResult
}

export function useTranscriptionApi() {
  const config = useRuntimeConfig()
  const error = ref<string | null>(null)
  const isLoading = ref(false)

  async function transcribeSentence(audio: Blob, sentenceId: string): Promise<TranscriptionResult> {
    error.value = null
    isLoading.value = true

    try {
      console.log('Creating form data...')
      const formData = new FormData()
      formData.append('audio', audio, 'recording.wav')
      formData.append('sentence_id', sentenceId)

      console.log('Sending request to:', `${config.public.backendApiUrl}/api/transcribe_sentence`)
      const response = await fetch(`${config.public.backendApiUrl}/api/transcribe_sentence`, {
        method: 'POST',
        body: formData
      })

      console.log('Response status:', response.status)
      if (!response.ok) {
        const errorText = await response.text()
        console.error('API error response:', errorText)
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: TranscriptionResponse = await response.json()
      console.log('API response data:', data)
      
      if (!data?.result) {
        throw new Error('Invalid response format')
      }

      return data.result
    } catch (e) {
      console.error('Transcription error:', e)
      error.value = e instanceof Error ? e.message : 'Failed to transcribe audio'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return {
    transcribeSentence,
    error,
    isLoading
  }
}