<script setup>
const supabase = useSupabaseClient()
const user = useSupabaseUser()
const exercises = ref([])
const completedExercises = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    // Fetch all exercises with their progress
    const { data: progressData, error: progressError } = await supabase
      .from('user_progress')
      .select(`
        exercise_id,
        completion_status,
        rating,
        exercises (
          id,
          title,
          description,
          created_at,
          updated_at,
          exercise_sentences!inner (
            sentence:sentences (
              id
            )
          )
        )
      `)
      .eq('user_id', user.value.id)

    if (progressError) throw progressError

    // Separate completed and uncompleted exercises
    const allExercises = progressData.map(progress => ({
      id: progress.exercises.id,
      title: progress.exercises.title,
      description: progress.exercises.description,
      createdAt: progress.exercises.created_at,
      updatedAt: progress.exercises.updated_at,
      sentenceCount: progress.exercises.exercise_sentences.length,
      status: progress.completion_status,
      rating: progress.rating
    }))

    completedExercises.value = allExercises.filter(ex => ex.status === 'done')
    exercises.value = allExercises.filter(ex => ex.status !== 'done')

    // Fetch exercises without progress to add them to available exercises
    const { data: newExercises, error: newExError } = await supabase
      .from('exercises')
      .select(`
        id,
        title,
        description,
        created_at,
        updated_at,
        exercise_sentences!inner (
          sentence:sentences (
            id
          )
        )
      `)
      .not('id', 'in', `(${allExercises.map(e => e.id).join(',')})`)

    if (!newExError && newExercises) {
      exercises.value = [
        ...exercises.value,
        ...newExercises.map(ex => ({
          id: ex.id,
          title: ex.title,
          description: ex.description,
          createdAt: ex.created_at,
          updatedAt: ex.updated_at,
          sentenceCount: ex.exercise_sentences.length,
          status: 'not started'
        }))
      ]
    }
  } catch (err) {
    console.error('Error fetching exercises:', err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-6 dark:bg-gray-900">
    <div class="mx-auto max-w-4xl">
      <div class="mb-8">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Welcome to English Learning!</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Choose an exercise to start practicing.</p>
      </div>

      <div v-if="loading" class="text-center text-gray-900 dark:text-white">
        <p>Loading exercises...</p>
      </div>

      <div v-else class="space-y-8">
        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">Available Exercises</h2>
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="exercise in exercises"
              :key="exercise.id"
              class="rounded-lg bg-white p-6 shadow transition-shadow hover:shadow-md dark:bg-gray-800"
            >
              <h3 class="text-lg font-medium text-gray-900 dark:text-white">{{ exercise.title }}</h3>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">{{ exercise.description }}</p>
              
              <div class="mt-4 flex items-center justify-between">
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  {{ exercise.sentenceCount }} sentences
                </span>
                <NuxtLink
                  :to="`/exercise/${exercise.id}`"
                  class="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  {{ exercise.status === 'in_progress' ? 'Continue' : 'Start' }} Exercise
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </NuxtLink>
              </div>
            </div>
          </div>
        </section>

        <CompletedExercises
          v-if="completedExercises.length > 0"
          :completed-exercises="completedExercises"
        />
      </div>
    </div>
  </div>
</template>