<template>
  <section class="mt-12">
    <h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">Completed Exercises</h2>
    <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="exercise in completedExercises"
        :key="exercise.id"
        class="rounded-lg bg-white p-6 shadow transition-shadow hover:shadow-md dark:bg-gray-800"
      >
        <div class="flex items-start justify-between">
          <div>
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">{{ exercise.title }}</h3>
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">{{ exercise.description }}</p>
          </div>
          <div class="flex text-yellow-400">
            <span v-for="i in exercise.rating" :key="i">★</span>
          </div>
        </div>
        
        <div class="mt-4 flex items-center justify-between">
          <span class="text-sm text-gray-500 dark:text-gray-400">
            {{ exercise.sentenceCount }} sentences
          </span>
          <NuxtLink
            :to="`/exercise/${exercise.id}`"
            class="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
          >
            Practice Again
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </NuxtLink>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  completedExercises: {
    type: Array,
    required: true
  }
})
</script>