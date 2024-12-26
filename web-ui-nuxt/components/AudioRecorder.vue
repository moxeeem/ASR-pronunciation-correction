<template>
  <div class="space-y-4">
    <!-- Controls -->
    <div class="flex items-center gap-4">
      <button
        @click="handleRecording"
        :disabled="isProcessing"
        class="flex items-center gap-2 rounded-md px-4 py-2 text-white transition-all duration-200"
        :class="buttonClass"
      >
        <span v-if="isProcessing" class="animate-spin">⏳</span>
        {{ buttonText }}
      </button>

      <button
        @click="handleSkip"
        :disabled="isProcessing || isRecording"
        class="rounded-md bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
      >
        Skip
      </button>
    </div>

    <!-- Transcription Results -->
    <TranscriptionDisplay
      v-if="currentResult"
      :expected-ipa-transcription="sentence.ipa_transcription"
      :expected-arpabet-transcription="sentence.arpabet_transcription"
      :user-transcription="currentResult.transcription"
      :real-transcription="currentResult.real_transcription"
      :accuracy="currentResult.accuracy"
      :correct-letters="currentResult.correct_letters"
    />

    <!-- Next Button -->
    <div v-if="canProceed" class="mt-4">
      <button
        @click="handleNext"
        class="rounded-md bg-green-600 px-4 py-2 text-white transition-all duration-200 hover:bg-green-700 animate-pulse"
      >
        Next
      </button>
    </div>

    <!-- Feedback Message -->
    <p 
      v-else-if="currentResult" 
      class="text-sm text-red-600 dark:text-red-400"
    >
      Try to achieve at least 80% accuracy to proceed
    </p>

    <p v-if="error" class="mt-2 text-red-500">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Sentence } from '~/types/exercise'
import type { TranscriptionResult } from '~/types/api'
import { AudioRecorder } from '~/utils/audio/recorder'

const props = defineProps<{
  sentence: Sentence
}>()

const emit = defineEmits<{
  score: [score: number]
  next: []
  skip: []
  'recording-result': [result: TranscriptionResult | null]
}>()

const recorder = ref<AudioRecorder | null>(null)
const isRecording = ref(false)
const isProcessing = ref(false)
const error = ref<string | null>(null)
const currentResult = ref<TranscriptionResult | null>(null)

const api = useTranscriptionApi()

// Computed properties
const buttonText = computed(() => {
  if (isProcessing.value) return 'Processing...'
  return isRecording.value ? 'Stop Recording' : 'Start Recording'
})

const buttonClass = computed(() => ({
  'bg-red-500 hover:bg-red-600': isRecording.value,
  'bg-blue-500 hover:bg-blue-600': !isRecording.value,
  'opacity-50 cursor-not-allowed': isProcessing.value
}))

const canProceed = computed(() => 
  currentResult.value && currentResult.value.accuracy >= 0.8
)

// Methods
async function handleRecording() {
  try {
    if (isRecording.value) {
      console.log('Stopping recording...')
      const blob = await recorder.value?.stop()
      
      if (blob) {
        isProcessing.value = true
        console.log('Got audio blob, size:', blob.size)
        const result = await api.transcribeSentence(blob, props.sentence.id)
        console.log('Transcription result:', result)
        
        currentResult.value = result
        emit('recording-result', result)
        
        if (result.accuracy) {
          emit('score', result.accuracy)
        }
      }
      
      isRecording.value = false
    } else {
      console.log('Starting recording...')
      recorder.value = new AudioRecorder()
      await recorder.value.start()
      isRecording.value = true
      currentResult.value = null
      emit('recording-result', null)
    }
  } catch (err) {
    console.error('Recording handler error:', err)
    error.value = err instanceof Error ? err.message : 'Recording failed'
    isRecording.value = false
  } finally {
    isProcessing.value = false
  }
}

function handleNext() {
  if (canProceed.value) {
    emit('next')
  }
}

function handleSkip() {
  emit('skip')
}

// Cleanup
onUnmounted(() => {
  if (isRecording.value && recorder.value) {
    recorder.value.stop().catch(console.error)
  }
})
</script>
