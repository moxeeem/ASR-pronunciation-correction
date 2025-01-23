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
            <span>Progress: {{ progressStats.completed }} / {{ progressStats.total }}</span>
            <div class="flex gap-4">
              <span class="text-green-600">Completed: {{ progressStats.completed }}</span>
              <span class="text-yellow-600">Skipped: {{ progressStats.skipped }}</span>
              <span>{{ Math.round(progressStats.percentage) }}%</span>
            </div>
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

    <!-- Completion Modal -->
    <div v-if="showCompletionModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <h3 class="mb-4 text-lg font-medium text-gray-900 dark:text-white">
          Exercise Completed!
        </h3>
        <p class="mb-6 text-gray-600 dark:text-gray-400">
          Would you like to reset your progress and try this exercise again?
        </p>
        <div class="flex justify-end gap-4">
          <button
            @click="handleReturnToDashboard"
            class="rounded-md bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
          >
            Return to Dashboard
          </button>
          <button
            @click="handleResetAndRetry"
            class="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            Reset and Retry
          </button>
        </div>
      </div>
    </div>

    <!-- Incomplete Exercise Modal -->
    <div v-if="showIncompleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-gray-800">
        <h3 class="mb-4 text-lg font-medium text-gray-900 dark:text-white">
          Exercise Not Completed
        </h3>
        <p class="mb-6 text-gray-600 dark:text-gray-400">
          You have skipped some sentences. Would you like to continue practicing or return to dashboard?
        </p>
        <div class="flex justify-end gap-4">
          <button
            @click="handleReturnToDashboard"
            class="rounded-md bg-gray-200 px-4 py-2 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600"
          >
            Return to Dashboard
          </button>
          <button
            @click="handleContinuePractice"
            class="rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
          >
            Continue Practice
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Exercise, Sentence } from '~/types/exercise'

const route = useRoute()
const supabase = useSupabaseClient()
const router = useRouter()
const user = useSupabaseUser()
const { resetExerciseSentencesProgress, checkExerciseCompletion } = useProgress()

const exercise = ref<Exercise | null>(null)
const remainingSentences = ref<Sentence[]>([])
const currentSentenceIndex = ref(0)
const loading = ref(true)
const showCompletionModal = ref(false)
const showIncompleteModal = ref(false)
const lastSentenceCompleted = ref(false)
const readyForNext = ref(false)

// Progress tracking
const progressStats = ref({
  total: 0,
  completed: 0,
  skipped: 0,
  percentage: 0
})

// Computed properties
const currentSentence = computed(() => remainingSentences.value[currentSentenceIndex.value])

function updateProgressStats() {
  // Считаем процент только по completed предложениям
  progressStats.value.percentage = (progressStats.value.completed / progressStats.value.total) * 100
}

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
        status: score >= 0.8 ? 'completed' : 'not_completed'
      })

    if (score >= 0.8) {
      progressStats.value.completed++
      updateProgressStats()
      
      // Проверяем, является ли это последним предложением
      const isLastSentence = currentSentenceIndex.value === remainingSentences.value.length - 1
      
      if (isLastSentence) {
        lastSentenceCompleted.value = true
        // Проверяем общее завершение упражнения
        const isCompleted = await checkExerciseCompletion(route.params.id as string)
        if (isCompleted) {
          await updateExerciseStatus('completed')
          // Отложенный показ модального окна
          setTimeout(() => {
            showCompletionModal.value = true
          }, 2000)
        }
      }
      // Устанавливаем флаг готовности к переходу вместо автоматического перехода
      readyForNext.value = true
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

    // Обновляем счетчик пропущенных только если это новое пропущенное предложение
    const isNewSkip = !remainingSentences.value.some(s => 
      s.id === currentSentence.value?.id && progressStats.value.skipped > 0
    )
    if (isNewSkip) {
      progressStats.value.skipped++
    }
    
    // Если это последнее предложение, показываем модальное окно о незавершенном упражнении
    if (currentSentenceIndex.value >= remainingSentences.value.length - 1) {
      showIncompleteModal.value = true
    } else {
      currentSentenceIndex.value++
    }
  } catch (err) {
    console.error('Error skipping sentence:', err)
  }
}

async function nextSentence() {
  // Проверяем готовность к переходу
  if (!readyForNext.value) return

  // Если это было последнее успешно выполненное предложение
  if (lastSentenceCompleted.value) {
    router.push('/dashboard')
    return
  }

  if (currentSentenceIndex.value < remainingSentences.value.length - 1) {
    currentSentenceIndex.value++
    // Сбрасываем флаг готовности после перехода
    readyForNext.value = false
  } else {
    // Перезагружаем данные, чтобы обновить список оставшихся предложений
    await loadExerciseData()
    // Сбрасываем флаг готовности после перезагрузки
    readyForNext.value = false
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

async function handleResetAndRetry() {
  try {
    loading.value = true
    await resetExerciseSentencesProgress(route.params.id as string)
    await loadExerciseData()
    showCompletionModal.value = false
    showIncompleteModal.value = false
    currentSentenceIndex.value = 0
  } catch (err) {
    console.error('Error resetting exercise:', err)
  } finally {
    loading.value = false
  }
}

function handleReturnToDashboard() {
  router.push('/dashboard')
}

function handleContinuePractice() {
  showIncompleteModal.value = false
  loadExerciseData()
}

async function loadExerciseData() {
  if (!user.value) return

  try {
    // First, get all sentences for this exercise
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
    const allSentences = exerciseData.exercise_sentences.map(es => es.sentences)
    progressStats.value.total = allSentences.length

    // Get progress for all sentences
    const { data: progressData } = await supabase
      .from('user_exercise_sentence_progress')
      .select('sentence_id, status')
      .eq('exercise_id', route.params.id)
      .eq('user_id', user.value.id)

    // Create a map of sentence progress
    const progressMap = new Map(
      progressData?.map(p => [p.sentence_id, p.status]) || []
    )

    // Сбрасываем флаги при загрузке новых данных
    lastSentenceCompleted.value = false
    readyForNext.value = false

    // Count completed and skipped sentences
    if (progressData) {
      // Считаем только уникальные пропущенные предложения
      const uniqueSkipped = new Set(progressData.filter(p => p.status === 'skipped').map(p => p.sentence_id))
      progressStats.value.completed = progressData.filter(p => p.status === 'completed').length
      progressStats.value.skipped = uniqueSkipped.size
    }

    // Filter out completed sentences, keep only not attempted or skipped
    remainingSentences.value = allSentences.filter(sentence => {
      const status = progressMap.get(sentence.id)
      return !status || status === 'not_completed' || status === 'skipped'
    })

    updateProgressStats()

    // Проверяем реальное завершение упражнения
    const isCompleted = await checkExerciseCompletion(route.params.id as string)
    if (isCompleted) {
      showCompletionModal.value = true
    }

  } catch (err) {
    console.error('Error fetching exercise:', err)
    throw err
  }
}

// Fetch exercise data and initialize progress
onMounted(async () => {
  if (!user.value) {
    return router.push('/auth/login')
  }

  try {
    await loadExerciseData()
  } catch (err) {
    console.error('Error loading exercise:', err)
  } finally {
    loading.value = false
  }
})
</script>