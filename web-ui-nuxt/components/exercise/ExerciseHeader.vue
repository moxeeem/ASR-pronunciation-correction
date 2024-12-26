<template>
  <div class="mb-8">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ title }}</h1>
    <p class="mt-2 text-gray-600 dark:text-gray-400">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description: string
}>()
</script>