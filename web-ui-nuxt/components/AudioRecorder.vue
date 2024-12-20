<template>
  <div class="flex flex-col gap-4">
    <div class="flex items-center gap-4">
      <button
        @click="toggleRecording"
        :class="[
          'flex items-center gap-2 rounded-md px-4 py-2 text-white transition-colors',
          isRecording
            ? 'bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600'
            : 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600'
        ]"
        :disabled="isProcessing"
      >
        <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            v-if="isRecording"
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z M5 12h14"
          />
          <path
            v-else
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
          />
        </svg>
        {{ buttonText }}
      </button>

      <span v-if="isRecording" class="text-sm text-red-600 dark:text-red-400 animate-pulse">
        Recording...
      </span>
      <span v-else-if="isProcessing" class="text-sm text-blue-600 dark:text-blue-400 animate-pulse">
        Analyzing...
      </span>
    </div>

    <div v-if="error" class="text-sm text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <!-- Debug info -->
    <div v-if="lastResult" class="text-sm text-gray-600 dark:text-gray-400">
      <div>Your pronunciation: {{ lastResult.transcription }}</div>
      <div>Expected: {{ lastResult.real_transcription }}</div>
      <div>Accuracy: {{ Math.round(lastResult.accuracy * 100) }}%</div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  sentence: {
    id: string
    content: string
    ipa_transcription: string
  }
}>()

const emit = defineEmits<{
  score: [score: number]
}>()

const recorder = useAudioRecorder()
const api = useTranscriptionApi()

const isRecording = computed(() => recorder.isRecording.value)
const isProcessing = computed(() => recorder.isProcessing.value)
const buttonText = computed(() => recorder.buttonText.value)
const error = computed(() => recorder.error.value || api.error.value)
const lastResult = ref(null)

async function toggleRecording() {
  try {
    if (isRecording.value) {
      recorder.isProcessing.value = true
      const audioBlob = await recorder.stopRecording()
      
      if (audioBlob) {
        console.log('Sending audio for analysis...')
        const result = await api.transcribeSentence(audioBlob, props.sentence.id)
        console.log('Received result:', result)
        
        lastResult.value = result
        emit('score', result.accuracy)
      }
    } else {
      await recorder.startRecording()
    }
  } catch (err) {
    console.error('Recording error:', err)
    error.value = err instanceof Error ? err.message : 'An error occurred during recording'
  } finally {
    recorder.isProcessing.value = false
  }
}

// Cleanup on component unmount
onUnmounted(() => {
  if (isRecording.value) {
    recorder.stopRecording()
  }
})
</script>