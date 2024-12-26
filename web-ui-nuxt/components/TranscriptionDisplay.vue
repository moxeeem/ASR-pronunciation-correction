<template>
  <div class="space-y-4 text-gray-700 dark:text-gray-300">
    <!-- Expected Transcription -->
    <div v-if="expectedIpaTranscription || expectedArpabetTranscription" class="space-y-2">
      <div v-if="expectedIpaTranscription" class="flex gap-4">
        <span class="w-24 text-sm font-medium">IPA:</span>
        <span class="font-mono">{{ expectedIpaTranscription }}</span>
      </div>
      <div v-if="expectedArpabetTranscription" class="flex gap-4">
        <span class="w-24 text-sm font-medium">ARPABET:</span>
        <span class="font-mono">{{ expectedArpabetTranscription }}</span>
      </div>
    </div>
    
    <!-- User's Pronunciation -->
    <div v-if="userTranscription" class="space-y-2">
      <div class="flex gap-4">
        <span class="w-24 text-sm font-medium">Your:</span>
        <span class="font-mono">{{ userTranscription }}</span>
      </div>
      
      <div class="flex gap-4">
        <span class="w-24 text-sm font-medium">Accuracy:</span>
        <span 
          class="font-semibold"
          :class="accuracyColorClass"
        >
          {{ Math.round(accuracy * 100) }}%
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  expectedIpaTranscription?: string
  expectedArpabetTranscription?: string
  userTranscription?: string
  accuracy?: number
}>()

const accuracyColorClass = computed(() => {
  if (!props.accuracy) return ''
  return props.accuracy >= 0.8 
    ? 'text-green-600 dark:text-green-400'
    : 'text-red-600 dark:text-red-400'
})
</script>