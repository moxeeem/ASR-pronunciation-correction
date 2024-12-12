<template>
  <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="fixed inset-0 bg-black/50" @click="$emit('update:modelValue', false)"></div>
    <div class="relative z-10 w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
      <h3 class="text-xl font-semibold text-gray-900 dark:text-white">Rate this exercise</h3>
      <p class="mt-2 text-gray-600 dark:text-gray-400">How would you rate your experience with this exercise?</p>
      
      <div class="mt-4 flex justify-center space-x-2">
        <button
          v-for="rating in 5"
          :key="rating"
          @click="handleRating(rating)"
          class="p-2 text-2xl"
          :class="selectedRating >= rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'"
        >
          ★
        </button>
      </div>

      <div class="mt-6 flex justify-end space-x-3">
        <button
          @click="$emit('update:modelValue', false)"
          class="rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          Cancel
        </button>
        <button
          @click="submitRating"
          :disabled="!selectedRating"
          class="rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50 dark:bg-blue-500 dark:hover:bg-blue-600"
        >
          Submit
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: Boolean,
  exerciseId: String
})

const emit = defineEmits(['update:modelValue', 'rated'])
const selectedRating = ref(0)

function handleRating(rating) {
  selectedRating.value = rating
}

async function submitRating() {
  emit('rated', selectedRating.value)
  emit('update:modelValue', false)
  selectedRating.value = 0
}
</script>