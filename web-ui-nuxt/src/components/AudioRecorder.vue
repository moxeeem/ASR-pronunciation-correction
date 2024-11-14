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

    <div v-if="lastScore !== null" class="flex flex-col gap-2">
      <div class="flex items-center gap-4">
        <div class="flex-1">
          <div class="h-2 rounded-full bg-gray-200 dark:bg-gray-700">
            <div
              class="h-2 rounded-full transition-all duration-500"
              :class="scoreBarColorClass"
              :style="{ width: `${lastScore * 100}%` }"
            ></div>
          </div>
        </div>
        <span class="min-w-[4rem] text-sm font-medium" :class="scoreTextColorClass">
          {{ Math.round(lastScore * 100) }}%
        </span>
      </div>

      <p class="text-sm" :class="scoreTextColorClass">
        {{ scoreMessage }}
      </p>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  sentence: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['score'])

const isRecording = ref(false)
const isProcessing = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const lastScore = ref(null)

const buttonText = computed(() => {
  if (isProcessing.value) return 'Processing...'
  if (isRecording.value) return 'Stop Recording'
  return 'Record Pronunciation'
})

const scoreBarColorClass = computed(() => {
  if (lastScore.value === null) return ''
  return lastScore.value >= 0.85
    ? 'bg-green-600 dark:bg-green-500'
    : 'bg-orange-600 dark:bg-orange-500'
})

const scoreTextColorClass = computed(() => {
  if (lastScore.value === null) return ''
  return lastScore.value >= 0.85
    ? 'text-green-600 dark:text-green-400'
    : 'text-orange-600 dark:text-orange-400'
})

const scoreMessage = computed(() => {
  if (lastScore.value === null) return ''
  return lastScore.value >= 0.85
    ? 'Great pronunciation! You can proceed to the next sentence.'
    : 'Keep practicing! Try to match the pronunciation more closely.'
})

watch(() => props.sentence, () => {
  // Reset score when sentence changes
  lastScore.value = null
}, { deep: true })

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []

    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }

    mediaRecorder.value.onstop = async () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/wav' })
      await analyzePronunciation(audioBlob)
      
      // Stop all tracks to release the microphone
      stream.getTracks().forEach(track => track.stop())
    }

    mediaRecorder.value.start()
    isRecording.value = true
  } catch (error) {
    console.error('Error accessing microphone:', error)
    alert('Unable to access microphone. Please ensure you have granted permission.')
  }
}

function stopRecording() {
  if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
    mediaRecorder.value.stop()
    isRecording.value = false
  }
}

async function analyzePronunciation(audioBlob) {
  try {
    isProcessing.value = true
    
    const formData = new FormData()
    formData.append('audio', audioBlob)
    formData.append('text', props.sentence.content)
    formData.append('ipa', props.sentence.ipa_transcription)
    formData.append('arpabet', props.sentence.arpabet_transcription)

    const response = await fetch('/api/transcribe', {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      throw new Error('Failed to analyze pronunciation')
    }

    const { score } = await response.json()
    lastScore.value = score
    emit('score', score)
  } catch (error) {
    console.error('Error analyzing pronunciation:', error)
    alert('Error analyzing pronunciation. Please try again.')
  } finally {
    isProcessing.value = false
  }
}

function toggleRecording() {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

// Clean up on component unmount
onUnmounted(() => {
  if (mediaRecorder.value && mediaRecorder.value.state === 'recording') {
    stopRecording()
  }
})
</script>