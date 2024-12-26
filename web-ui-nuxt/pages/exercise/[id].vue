```vue
<template>
  <div class="min-h-screen bg-gray-50 p-6 dark:bg-gray-900">
    <div class="mx-auto max-w-4xl">
      <LoadingSpinner v-if="loading" />
      
      <template v-else-if="exercise && currentSentence">
        <!-- Exercise Header -->
        <div class="mb-8">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ exercise.title }}</h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">{{ exercise.description }}</p>
        </div>

        <!-- Progress Bar -->
        <div class="mb-8">
          <div class="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>Progress: {{ currentIndex + 1 }} / {{ sentences.length }}</span>
            <span>{{ Math.round((currentIndex + 1) / sentences.length * 100) }}%</span>
          </div>
          <div class="mt-2 h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
            <div
              class="h-2 rounded-full bg-blue-600 transition-all duration-300 dark:bg-blue-500"
              :style="{ width: `${(currentIndex + 1) / sentences.length * 100}%` }"
            />
          </div>
        </div>

        <!-- Current Sentence -->
        <div class="mb-8 rounded-lg bg-white p-6 shadow-md dark:bg-gray-800">
          <div class="mb-6">
            <div class="flex items-center justify-between">
              <p class="text-xl text-gray-900 dark:text-white">{{ currentSentence.content }}</p>
              <button
                @click="speakSentence"
                class="flex items-center gap-2 rounded-md bg-blue-100 px-3 py-1.5 text-blue-600 hover:bg-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:hover:bg-blue-900/50"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.707.707L4.586 13H2a1 1 0 01-1-1V8a1 1 0 011-1h2.586l3.707-3.707a1 1 0 011.09-.217zM14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.984 5.984 0 01-1.757 4.243 1 1 0 01-1.415-1.415A3.984 3.984 0 0013 10a3.983 3.983 0 00-1.172-2.828 1 1 0 010-1.415z" clip-rule="evenodd" />
                </svg>
                <span class="text-sm font-medium">Listen</span>
              </button>
            </div>
          </div>
          
          <AudioRecorder
            :sentence="currentSentence"
            :key="currentSentence.id"
            @score="handlePronunciationScore"
            @next="nextSentence"
            @skip="skipSentence"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const supabase = useSupabaseClient()
const router = useRouter()
const user = useSupabaseUser()

const exercise = ref(null)
const sentences = ref([])
const currentIndex = ref(0)
const loading = ref(true)

onMounted(async () => {
  if (!user.value) {
    return router.push('/auth/login')
  }

  try {
    const { data: exerciseData, error: exerciseError } = await supabase
      .from('exercises')
      .select(`
        *,
        exercise_sentences!inner (
          sentences (
            id,
            content,
            ipa_transcription,
            arpabet_transcription
          )
        )
      `)
      .eq('id', route.params.id)
      .single()

    if (exerciseError) throw exerciseError

    exercise.value = exerciseData
    sentences.value = exerciseData.exercise_sentences.map(es => es.sentences)
  } catch (err) {
    console.error('Error fetching exercise:', err)
  } finally {
    loading.value = false
  }
})

// Computed properties
const currentSentence = computed(() => sentences.value[currentIndex.value])

// Methods
function speakSentence() {
  if (!currentSentence.value) return
  
  const utterance = new SpeechSynthesisUtterance(currentSentence.value.content)
  utterance.lang = 'en-US'
  speechSynthesis.speak(utterance)
}

async function nextSentence() {
  if (currentIndex.value < sentences.value.length - 1) {
    currentIndex.value++
  } else {
    // Exercise completed
    await updateExerciseStatus('completed')
    router.push('/dashboard')
  }
}

async function skipSentence() {
  if (!currentSentence.value || !user.value) return

  try {
    await supabase
      .from('user_exercise_sentence_progress')
      .upsert({
        user_id: user.value.id,
        exercise_id: route.params.id,
        sentence_id: currentSentence.value.id,
        status: 'skipped'
      })

    nextSentence()
  } catch (err) {
    console.error('Error skipping sentence:', err)
  }
}

async function handlePronunciationScore(score: number) {
  if (!currentSentence.value || !user.value) return
  
  try {
    await supabase
      .from('user_exercise_sentence_progress')
      .upsert({
        user_id: user.value.id,
        exercise_id: route.params.id,
        sentence_id: currentSentence.value.id,
        status: score >= 0.8 ? 'completed' : 'not_attempted'
      })
  } catch (err) {
    console.error('Error updating sentence progress:', err)
  }
}

async function updateExerciseStatus(status: 'in_progress' | 'completed') {
  if (!user.value) return

  try {
    await supabase
      .from('user_progress')
      .upsert({
        user_id: user.value.id,
        exercise_id: route.params.id,
        completion_status: status,
        last_attempted: new Date().toISOString()
      })
  } catch (err) {
    console.error('Error updating exercise status:', err)
  }
}
</script>
```