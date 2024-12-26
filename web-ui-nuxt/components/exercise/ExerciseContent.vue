<template>
  <div class="mb-8 rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
    <!-- Sentence Content -->
    <div class="mb-6">
      <p class="text-xl text-gray-900 dark:text-white">{{ sentence.content }}</p>
    </div>
    
    <!-- Exercise Controls -->
    <ExerciseControls
      :sentence="sentence"
      :is-recording="isRecording"
      :is-processing="isProcessing"
      :result="result"
      @speak="$emit('speak')"
      @record="handleRecording"
      @next="handleNext"
      @skip="$emit('skip')"
    />
  </div>
</template>

<script setup lang="ts">
import type { Sentence } from '~/types/exercise'
import type { TranscriptionResult } from '~/types/api'
import { AudioRecorder } from '~/utils/audio/recorder'

const props = defineProps<{
  sentence: Sentence
}>()

const emit = defineEmits<{
  speak: []
  score: [score: number]
  next: []
  skip: []
}>()

const recorder = ref<AudioRecorder | null>(null)
const isRecording = ref(false)
const isProcessing = ref(false)
const result = ref<TranscriptionResult | null>(null)
const api = useTranscriptionApi()

async function handleRecording() {
  try {
    if (isRecording.value) {
      const blob = await recorder.value?.stop()
      
      if (blob) {
        isProcessing.value = true
        const transcriptionResult = await api.transcribeSentence(blob, props.sentence.id)
        result.value = transcriptionResult
        
        if (transcriptionResult.accuracy) {
          emit('score', transcriptionResult.accuracy)
        }
      }
      
      isRecording.value = false
    } else {
      recorder.value = new AudioRecorder()
      await recorder.value.start()
      isRecording.value = true
      result.value = null // Сбрасываем результат при новой записи
    }
  } catch (err) {
    console.error('Recording error:', err)
  } finally {
    isProcessing.value = false
  }
}

function handleNext() {
  emit('next')
  // Сбрасываем состояние после перехода к следующему предложению
  result.value = null
  isRecording.value = false
  isProcessing.value = false
}

onUnmounted(() => {
  if (isRecording.value && recorder.value) {
    recorder.value.stop().catch(console.error)
  }
})
</script>
