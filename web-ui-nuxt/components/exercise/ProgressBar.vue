
<template>
  <div class="mb-8">
    <div class="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
      <span>Progress: {{ current }} / {{ total }}</span>
      <div class="flex gap-4">
        <span class="text-green-600">Completed: {{ completed }}</span>
        <span class="text-yellow-600">Skipped: {{ skipped }}</span>
        <span>{{ Math.round(percentage) }}%</span>
      </div>
    </div>
    <div class="mt-2 h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
      <div
        class="h-2 rounded-full bg-blue-600 transition-all duration-300 dark:bg-blue-500"
        :style="{ width: `${percentage}%` }"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  current: number
  total: number
  percentage: number
  completed: number
  skipped: number
}>()
</script>
