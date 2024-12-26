import { ref } from 'vue'
import { AudioRecorder } from '~/utils/audio/recorder'

export function useAudioRecorder() {
  const recorder = ref<AudioRecorder | null>(null)
  const isRecording = ref(false)
  const isProcessing = ref(false)
  const error = ref<string | null>(null)

  async function startRecording() {
    try {
      error.value = null
      recorder.value = new AudioRecorder()
      await recorder.value.start()
      isRecording.value = true
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to start recording'
      console.error('Start recording error:', err)
      error.value = message
      isRecording.value = false
    }
  }

  async function stopRecording(): Promise<Blob | null> {
    if (!recorder.value) {
      console.log('No recorder instance')
      return null
    }

    try {
      isProcessing.value = true
      const blob = await recorder.value.stop()
      console.log('Recording stopped, blob size:', blob.size)
      return blob
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to stop recording'
      console.error('Stop recording error:', err)
      error.value = message
      return null
    } finally {
      isRecording.value = false
      isProcessing.value = false
      recorder.value = null
    }
  }

  return {
    isRecording: readonly(isRecording),
    isProcessing: readonly(isProcessing),
    error: readonly(error),
    startRecording,
    stopRecording
  }
}