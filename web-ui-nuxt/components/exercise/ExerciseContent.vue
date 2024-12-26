<template>
  <div class="mb-8 rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
    <div class="mb-6">
      <div class="flex items-center justify-between">
        <p class="text-xl text-gray-900 dark:text-white">{{ sentence.content }}</p>
        <button
          @click="$emit('speak')"
          class="flex items-center gap-2 rounded-md bg-blue-100 px-3 py-1.5 text-blue-600 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-900/50"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10 3.5a.5.5 0 0 1 .5.5v4.8l3.15-3.15a.5.5 0 0 1 .7.7l-4 4a.5.5 0 0 1-.7 0l-4-4a.5.5 0 1 1 .7-.7L9.5 8.8V4a.5.5 0 0 1 .5-.5z"/>
          </svg>
          <span class="text-sm font-medium">Listen</span>
        </button>
      </div>
    </div>
    
    <AudioRecorder
      :sentence="sentence"
      :key="sentence.id"
      @score="$emit('score', $event)"
      @next="$emit('next')"
      @skip="$emit('skip')"
    />
  </div>
</template>

<script setup lang="ts">
import type { Sentence } from '~/types/exercise'

defineProps<{
  sentence: Sentence
}>()

defineEmits<{
  speak: []
  score: [score: number]
  next: []
  skip: []
}>()
</script>