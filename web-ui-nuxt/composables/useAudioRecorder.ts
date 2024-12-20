import { ref, computed } from 'vue'
import { blobToWav } from '~/utils/audio'

export function useAudioRecorder() {
  const isRecording = ref(false)
  const isProcessing = ref(false)
  const error = ref<string | null>(null)
  const mediaRecorder = ref<MediaRecorder | null>(null)
  const audioChunks = ref<Blob[]>([])
  const stream = ref<MediaStream | null>(null)

  const buttonText = computed(() => {
    if (isProcessing.value) return 'Processing...'
    if (isRecording.value) return 'Stop Recording'
    return 'Record Pronunciation'
  })

  async function startRecording() {
    try {
      error.value = null
      stream.value = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000
        }
      })
      
      mediaRecorder.value = new MediaRecorder(stream.value)
      audioChunks.value = []

      mediaRecorder.value.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.value.push(event.data)
        }
      }

      mediaRecorder.value.start(100)
      isRecording.value = true
    } catch (err) {
      error.value = 'Unable to access microphone. Please ensure you have granted permission.'
      throw error.value
    }
  }

  async function stopRecording(): Promise<Blob | null> {
    return new Promise((resolve) => {
      if (!mediaRecorder.value || mediaRecorder.value.state !== 'recording') {
        resolve(null)
        return
      }

      mediaRecorder.value.onstop = async () => {
        try {
          const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
          const wavBlob = await blobToWav(audioBlob)
          resolve(wavBlob)
        } catch (err) {
          error.value = 'Failed to process audio recording'
          resolve(null)
        } finally {
          cleanup()
        }
      }

      mediaRecorder.value.stop()
      isRecording.value = false
    })
  }

  function cleanup() {
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop())
      stream.value = null
    }
    mediaRecorder.value = null
    audioChunks.value = []
  }

  onUnmounted(cleanup)

  return {
    isRecording,
    isProcessing,
    error,
    buttonText,
    startRecording,
    stopRecording
  }
}