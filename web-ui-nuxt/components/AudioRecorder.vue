<template>
  <div class="space-y-4">
    <!-- Transcription Display -->
    <TranscriptionDisplay 
      :expected-ipa-transcription="sentence.ipa_transcription"
      :expected-arpabet-transcription="sentence.arpabet_transcription"
      :user-transcription="currentResult?.transcription"
      :accuracy="currentResult?.accuracy"
    />

    <!-- Controls -->
    <div class="flex items-center gap-4">
      <button
        @click="handleRecording"
        :disabled="isProcessing || isCompleted"
        class="flex items-center gap-2 rounded-md px-4 py-2 text-white transition-all duration-200"
        :class="buttonClass"
      >
        <span v-if="isProcessing" class="animate-spin">⏳</span>
        {{ buttonText }}
      </button>

      <button
        @click="handleNext"
        :disabled="!canProceed"
        class="rounded-md bg-green-600 px-4 py-2 text-white transition-all duration-200 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        :class="{ 'animate-pulse': canProceed && !isCompleted }"
      >
        Next
      </button>

      <button
        @click="handleSkip"
        :disabled="isCompleted"
        class="rounded-md bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Skip
      </button>
    </div>

    <!-- Feedback Message -->
    <p 
      v-if="currentResult && !canProceed" 
      class="text-sm text-red-600 dark:text-red-400 mt-2"
    >
      Try to achieve at least 80% accuracy to proceed
    </p>

    <p v-if="error" class="mt-2 text-red-500">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import type { Sentence } from '~/types/exercise'

const props = defineProps<{
  sentence: Sentence
}>()

const emit = defineEmits(['score', 'next', 'skip'])

const recorder = useAudioRecorder()
const api = useTranscriptionApi()

const { isRecording, isProcessing, error } = recorder
const currentResult = ref(null)
const isCompleted = ref(false)

const buttonText = computed(() => {
  if (isProcessing.value) return 'Processing...'
  if (isCompleted.value) return 'Completed'
  return isRecording.value ? 'Stop Recording' : 'Start Recording'
})

const buttonClass = computed(() => ({
  'bg-red-500 hover:bg-red-600': isRecording.value,
  'bg-blue-500 hover:bg-blue-600': !isRecording.value && !isCompleted.value,
  'bg-green-500': isCompleted.value,
  'opacity-50 cursor-not-allowed': isProcessing.value || isCompleted.value
}))

const canProceed = computed(() => currentResult.value?.accuracy >= 0.8)

async function handleRecording() {
  if (isCompleted.value) return

  try {
    if (isRecording.value) {
      const blob = await recorder.stopRecording()
      
      if (blob) {
        const result = await api.transcribeSentence(blob, props.sentence.id)
        currentResult.value = result
        emit('score', result.accuracy)
        
        if (result.accuracy >= 0.8) {
          isCompleted.value = true
        }
      }
    } else {
      await recorder.startRecording()
    }
  } catch (err) {
    console.error('Recording handler error:', err)
  }
}

function handleNext() {
  if (!canProceed.value) return
  emit('next')
  resetState()
}

function handleSkip() {
  if (isCompleted.value) return
  emit('skip')
  resetState()
}

function resetState() {
  currentResult.value = null
  isCompleted.value = false
}

onUnmounted(() => {
  if (isRecording.value) {
    recorder.stopRecording().catch(console.error)
  }
})
</script>