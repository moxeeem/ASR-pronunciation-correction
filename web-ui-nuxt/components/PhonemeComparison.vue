<template>
  <div class="space-y-4 rounded-md bg-white p-4 dark:bg-gray-900">
    <!-- User's Transcription -->
    <div class="space-y-2">
      <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Your Pronunciation</h4>
      <div class="flex flex-wrap gap-2 font-mono text-base leading-relaxed">
        <template v-for="(word, wordIndex) in userTranscriptionWords" :key="`user-${wordIndex}`">
          <span v-if="wordIndex > 0" class="select-none">&nbsp;</span>
          <span class="inline-flex gap-0.5">
            <span 
              v-for="(char, charIndex) in word.split('')" 
              :key="`user-${wordIndex}-${charIndex}`"
              class="transition-colors duration-200"
              :class="getCharacterClass(wordIndex, charIndex)"
              :title="getCharacterTitle(wordIndex, charIndex)"
            >{{ char }}</span>
          </span>
        </template>
      </div>
    </div>

    <!-- Real Transcription -->
    <div v-if="realTranscription" class="space-y-2">
      <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Real Pronunciation</h4>
      <div class="flex flex-wrap gap-2 font-mono text-base leading-relaxed">
        <template v-for="(word, wordIndex) in realTranscriptionWords" :key="`real-${wordIndex}`">
          <span v-if="wordIndex > 0" class="select-none">&nbsp;</span>
          <span class="inline-flex gap-0.5">
            <span 
              v-for="(char, charIndex) in word.split('')" 
              :key="`real-${wordIndex}-${charIndex}`"
              class="transition-colors duration-200"
              :class="getCharacterClass(wordIndex, charIndex)"
            >{{ char }}</span>
          </span>
        </template>
      </div>
    </div>
    
    <!-- Legend -->
    <div class="mt-3 flex gap-4 text-xs">
      <span class="flex items-center gap-1">
        <span class="inline-block h-2 w-2 rounded-full bg-gray-900 dark:bg-gray-100"></span>
        <span class="text-gray-600 dark:text-gray-400">Correct</span>
      </span>
      <span class="flex items-center gap-1">
        <span class="inline-block h-2 w-2 rounded-full bg-red-600 dark:bg-red-400"></span>
        <span class="text-gray-600 dark:text-gray-400">Incorrect</span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  userTranscription: string
  realTranscription: string
  correctLetters: string
}>()

const userTranscriptionWords = computed(() => 
  props.userTranscription?.split(' ') || []
)

const realTranscriptionWords = computed(() => 
  props.realTranscription?.split(' ') || []
)

const correctMasks = computed(() => 
  props.correctLetters?.split(' ') || []
)

function getCharacterClass(wordIndex: number, charIndex: number): string {
  const mask = correctMasks.value[wordIndex]
  if (!mask) return 'text-gray-400'
  
  const bit = mask[charIndex]
  if (!bit) return 'text-gray-400'
  
  return {
    '1': 'text-gray-900 dark:text-gray-100 font-medium',
    '0': 'text-red-600 dark:text-red-400'
  }[bit] || 'text-gray-400'
}

function getCharacterTitle(wordIndex: number, charIndex: number): string {
  const mask = correctMasks.value[wordIndex]
  if (!mask) return 'Not evaluated'
  
  const bit = mask[charIndex]
  if (!bit) return 'Not evaluated'
  
  return bit === '1' ? 'Correct pronunciation' : 'Incorrect pronunciation'
}
</script>