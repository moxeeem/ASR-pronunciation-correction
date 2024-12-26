<template>
  <div class="rounded-lg bg-gray-50 p-6 dark:bg-gray-800/50">
    <!-- Expected Transcription -->
    <div v-if="expectedIpaTranscription || expectedArpabetTranscription" class="mb-6 space-y-3">
      <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Expected Pronunciation</h3>
      
      <div class="space-y-2">
        <div v-if="expectedIpaTranscription" class="flex items-baseline gap-4">
          <span class="w-20 text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">IPA</span>
          <span class="font-mono text-sm text-gray-700 dark:text-gray-300">{{ expectedIpaTranscription }}</span>
        </div>
        <div v-if="expectedArpabetTranscription" class="flex items-baseline gap-4">
          <span class="w-20 text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">ARPABET</span>
          <span class="font-mono text-sm text-gray-700 dark:text-gray-300">{{ expectedArpabetTranscription }}</span>
        </div>
      </div>
    </div>
    
    <!-- User's Pronunciation -->
    <div v-if="userTranscription" class="space-y-4">
      <div class="space-y-3">
        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Pronunciation Comparison</h3>
        
        <!-- Phoneme Comparison -->
        <PhonemeComparison
          v-if="correctLetters"
          :user-transcription="userTranscription"
          :real-transcription="realTranscription"
          :correct-letters="correctLetters"
        />
      </div>
      
      <!-- Accuracy Score -->
      <div class="mt-4 flex items-center justify-between rounded-md bg-gray-100 px-4 py-3 dark:bg-gray-800">
        <span class="text-sm font-medium text-gray-600 dark:text-gray-400">Accuracy Score</span>
        <div class="flex items-center gap-2">
          <span 
            class="text-lg font-semibold"
            :class="accuracyColorClass"
          >
            {{ Math.round(accuracy * 100) }}%
          </span>
          <span 
            class="text-2xl"
            :class="accuracyColorClass"
          >
            {{ accuracyEmoji }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>


<script setup lang="ts">
// Remove duplicate defineProps and use withDefaults directly
const props = withDefaults(defineProps<{
  expectedIpaTranscription?: string | null
  expectedArpabetTranscription?: string | null
  userTranscription: string
  realTranscription: string
  accuracy: number
  correctLetters: string
}>(), {
  expectedIpaTranscription: null,
  expectedArpabetTranscription: null
})


const accuracyColorClass = computed(() => {
  if (!props.accuracy) return ''
  if (props.accuracy >= 0.9) return 'text-green-600 dark:text-green-400'
  if (props.accuracy >= 0.8) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-red-600 dark:text-red-400'
})

const accuracyEmoji = computed(() => {
  if (!props.accuracy) return ''
  if (props.accuracy >= 0.9) return '🎯'
  if (props.accuracy >= 0.8) return '👍'
  return '🤧'
})
</script>
