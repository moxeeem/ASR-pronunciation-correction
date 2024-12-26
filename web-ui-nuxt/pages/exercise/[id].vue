<template>
  <div class="min-h-screen bg-gray-50 p-6 dark:bg-gray-900">
    <div class="mx-auto max-w-4xl">
      <LoadingSpinner v-if="loading" />
      
      <template v-else-if="exercise && currentSentence">
        <!-- Exercise Header -->
        <ExerciseHeader
          :title="exercise.title"
          :description="exercise.description"
        />

        <!-- Progress Bar -->
        <div class="mb-8">
          <div class="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>Progress: {{ progressStats.current }} / {{ progressStats.total }}</span>
            <span>{{ Math.round(progressStats.percentage) }}%</span>
          </div>
          <div class="mt-2 h-2 w-full rounded-full bg-gray-200 dark:bg-gray-700">
            <div
              class="h-2 rounded-full bg-blue-600 transition-all dark:bg-blue-500"
              :style="{ width: `${progressStats.percentage}%` }"
            ></div>
          </div>
        </div>

        <!-- Exercise Content -->
        <ExerciseContent
          :sentence="currentSentence"
          @speak="speakSentence"
          @score="handlePronunciationScore"
          @next="nextSentence"
          @skip="skipSentence"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Exercise, Sentence } from '~/types/exercise'

const route = useRoute()
const supabase = useSupabaseClient()
const router = useRouter()
const user = useSupabaseUser()

const exercise = ref<Exercise | null>(null)
const sentences = ref<Sentence[]>([])
const currentSentenceIndex = ref(0)
const loading = ref(true)
const completedCount = ref(0)
const skippedCount = ref(0)

// Computed properties
const currentSentence = computed(() => sentences.value[currentSentenceIndex.value])

const progressStats = computed(() => ({
  current: currentSentenceIndex.value + 1,
  total: sentences.value.length,
  percentage: ((completedCount.value + skippedCount.value) / sentences.value.length) * 100
}))

// Methods
function speakSentence() {
  if (!currentSentence.value) return
  
  const utterance = new SpeechSynthesisUtterance(currentSentence.value.content)
  utterance.lang = 'en-US'
  speechSynthesis.speak(utterance)
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

    if (score >= 0.8) {
      completedCount.value++
    }
  } catch (err) {
    console.error('Error updating sentence progress:', err)
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

    skippedCount.value++
    nextSentence()
  } catch (err) {
    console.error('Error skipping sentence:', err)
  }
}

async function nextSentence() {
  if (currentSentenceIndex.value < sentences.value.length - 1) {
    currentSentenceIndex.value++
  } else {
    await updateExerciseStatus('completed')
    router.push('/dashboard')
  }
}

async function updateExerciseStatus(status: 'completed' | 'in_progress') {
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

// Fetch exercise data
onMounted(async () => {
  if (!user.value) {
    return router.push('/auth/login')
  }

  try {
    // Fetch exercise with sentences
    const { data: exerciseData, error: exerciseError } = await supabase
      .from('exercises')
      .select(`
        *,
        exercise_sentences!inner (
          sentences (
            id,
            content,
            ipa_transcription,
            arpabet_transcription,
            word_count,
            char_count_no_spaces,
            char_count_total,
            difficulty_level,
            translation_ru
          )
        )
      `)
      .eq('id', route.params.id)
      .single()

    if (exerciseError) throw exerciseError

    exercise.value = exerciseData
    sentences.value = exerciseData.exercise_sentences.map(es => es.sentences)

    // Fetch progress
    const { data: progressData } = await supabase
      .from('user_exercise_sentence_progress')
      .select('status')
      .eq('exercise_id', route.params.id)
      .eq('user_id', user.value.id)

    if (progressData) {
      completedCount.value = progressData.filter(p => p.status === 'completed').length
      skippedCount.value = progressData.filter(p => p.status === 'skipped').length
    }
  } catch (err) {
    console.error('Error fetching exercise:', err)
  } finally {
    loading.value = false
  }
})
</script>
