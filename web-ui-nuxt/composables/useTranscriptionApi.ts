import { ref, readonly } from 'vue'
import type { TranscriptionResult } from '~/types/api'
import { prepareAudioForUpload } from '~/utils/audio/upload'

export function useTranscriptionApi() {
  const config = useRuntimeConfig()
  const error = ref<string | null>(null)
  const isLoading = ref(false)

  async function transcribeSentence(audio: Blob, sentenceId: string): Promise<TranscriptionResult> {
    error.value = null
    isLoading.value = true

    try {
      // Подготавливаем FormData с аудио
      const formData = await prepareAudioForUpload(audio)
      formData.append('sentence_id', sentenceId)

      // Логируем для отладки
      console.log('Sending request to:', `${config.public.backendApiUrl}/api/transcribe_sentence`)
      console.log('FormData entries:', [...formData.entries()].map(([key]) => key))

      const response = await fetch(`${config.public.backendApiUrl}/api/transcribe_sentence`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      })

      if (!response.ok) {
        const errorText = await response.text()
        console.error('Server error response:', errorText)
        throw new Error(`Server error: ${response.status} - ${errorText}`)
      }

      const data = await response.json()
      console.log('Server response:', data)

      if (!data?.result) {
        throw new Error('Invalid response format')
      }

      return data.result
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to transcribe audio'
      error.value = message
      console.error('Transcription error:', err)
      throw new Error(message)
    } finally {
      isLoading.value = false
    }
  }

  return {
    transcribeSentence,
    error: readonly(error),
    isLoading: readonly(isLoading)
  }
}