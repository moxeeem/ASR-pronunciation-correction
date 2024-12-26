<template>
  <div class="space-y-6">
    <!-- Controls Group -->
    <div class="flex items-center gap-4">
      <!-- Listen Button -->
      <button
        @click="$emit('speak')"
        class="flex items-center gap-2 rounded-md bg-blue-100 px-4 py-2 text-blue-600 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-900/50"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clip-rule="evenodd"/>
        </svg>
        <span>Listen</span>
      </button>

      <!-- Record Button -->
      <button
        @click="handleRecording"
        :disabled="isProcessing"
        class="flex items-center gap-2 rounded-md px-4 py-2 text-white transition-all duration-200"
        :class="recordButtonClass"
      >
        <span v-if="isProcessing" class="animate-spin">⏳</span>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z"/>
        </svg>
        <span>{{ recordButtonText }}</span>
      </button>

      <!-- Skip Button -->
      <button
        @click="$emit('skip')"
        :disabled="isProcessing || isRecording || hasResult"
        class="flex items-center gap-2 rounded-md bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M4.555 5.168A1 1 0 003 6v8a1 1 0 001.555.832L10 11.202V14a1 1 0 001.555.832l6-4a1 1 0 000-1.664l-6-4A1 1 0 0010 6v2.798l-5.445-3.63z"/>
        </svg>
        <span>Skip</span>
      </button>

      <!-- Next Button -->
      <button
        v-if="canProceed"
        @click="handleNext"
        class="flex items-center gap-2 rounded-md bg-green-600 px-4 py-2 text-white transition-all duration-200 hover:bg-green-700"
      >
        <span>Next</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"/>
        </svg>
      </button>
    </div>

    <!-- Transcription Display -->
    <TranscriptionDisplay
      v-if="result"
      :expected-ipa-transcription="sentence.ipa_transcription"
      :expected-arpabet-transcription="sentence.arpabet_transcription"
      :user-transcription="result.transcription"
      :real-transcription="result.real_transcription"
      :accuracy="result.accuracy"
      :correct-letters="result.correct_letters"
    />

    <!-- Feedback Message -->
    <p 
      v-if="result && !canProceed" 
      class="text-sm text-red-600 dark:text-red-400"
    >
      Try to achieve at least 80% accuracy to proceed
    </p>
  </div>
</template>

<script setup lang="ts">
import type { Sentence } from '~/types/exercise'
import type { TranscriptionResult } from '~/types/api'

const props = defineProps<{
  sentence: Sentence
  isRecording: boolean
  isProcessing: boolean
  result: TranscriptionResult | null
}>()

const emit = defineEmits<{
  speak: []
  record: []
  next: []
  skip: []
}>()

const hasResult = computed(() => !!props.result)
const canProceed = computed(() => props.result && props.result.accuracy >= 0.8)

const recordButtonText = computed(() => {
  if (props.isProcessing) return 'Processing...'
  return props.isRecording ? 'Stop Recording' : 'Record'
})

const recordButtonClass = computed(() => ({
  'bg-red-500 hover:bg-red-600': props.isRecording,
  'bg-blue-500 hover:bg-blue-600': !props.isRecording,
  'opacity-50 cursor-not-allowed': props.isProcessing
}))

function handleRecording() {
  emit('record')
}

function handleNext() {
  emit('next')
}
</script>