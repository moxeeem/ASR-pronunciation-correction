<script setup>
const route = useRoute()
const supabase = useSupabaseClient()
const router = useRouter()
const user = useSupabaseUser()

const exercise = ref(null)
const sentences = ref([])
const currentSentenceIndex = ref(0)
const loading = ref(true)
const currentScore = ref(null)
const skippedSentences = ref([]) // Initialize as empty array

onMounted(async () => {
  try {
    // Fetch exercise details
    const { data: exerciseData, error: exerciseError } = await supabase
      .from('exercises')
      .select('*')
      .eq('id', route.params.id)
      .single()
    
    if (exerciseError) throw exerciseError
    exercise.value = exerciseData

    // Fetch related sentences through the junction table
    const { data: sentenceData, error: sentenceError } = await supabase
      .from('exercise_sentences')
      .select(`
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
      `)
      .eq('exercise_id', route.params.id)

    if (sentenceError) throw sentenceError
    sentences.value = sentenceData.map(item => item.sentences)

    // Fetch user progress
    const { data: progressData, error: progressError } = await supabase
      .from('user_progress')
      .select('*')
      .eq('user_id', user.value?.id)
      .eq('exercise_id', route.params.id)
      .single()

    if (!progressError && progressData?.sentences_skipped) {
      skippedSentences.value = progressData.sentences_skipped
    }
  } catch (err) {
    console.error('Error fetching exercise:', err)
  } finally {
    loading.value = false
  }
})

function speakSentence() {
  if (!sentences.value[currentSentenceIndex.value]) return
  
  const utterance = new SpeechSynthesisUtterance(
    sentences.value[currentSentenceIndex.value].content
  )
  utterance.lang = 'en-US'
  speechSynthesis.speak(utterance)
}

async function nextSentence() {
  if (currentSentenceIndex.value < sentences.value.length - 1) {
    currentSentenceIndex.value++
    currentScore.value = null
  } else {
    // Exercise completed
    await updateProgress('done')
    // Show rating dialog or redirect to dashboard
    router.push('/dashboard')
  }
}

async function skipSentence() {
  const currentSentenceId = sentences.value[currentSentenceIndex.value]?.id
  if (currentSentenceId) {
    skippedSentences.value = [...skippedSentences.value, currentSentenceId]
    await updateProgress('in_progress')
  }
  nextSentence()
}

async function updateProgress(status) {
  try {
    if (!user.value?.id) return

    await supabase
      .from('user_progress')
      .upsert({
        user_id: user.value.id,
        exercise_id: route.params.id,
        completion_status: status,
        sentences_skipped: skippedSentences.value,
        last_attempted: new Date().toISOString()
      })
      .eq('user_id', user.value.id)
      .eq('exercise_id', route.params.id)
  } catch (err) {
    console.error('Error updating progress:', err)
  }
}

function handlePronunciationScore(score) {
  currentScore.value = score
}

const currentSentence = computed(() => 
  sentences.value[currentSentenceIndex.value] || null
)

const progress = computed(() => ({
  current: currentSentenceIndex.value + 1,
  total: sentences.value.length,
  percentage: ((currentSentenceIndex.value + 1) / sentences.value.length) * 100
}))

const canProceed = computed(() => {
  const currentSentenceId = currentSentence.value?.id
  return currentScore.value >= 0.85 || 
    (currentSentenceId && skippedSentences.value?.includes(currentSentenceId)) || 
    false
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 p-6 dark:bg-gray-900">
    <div class="mx-auto max-w-2xl">
      <div v-if="loading" class="text-center text-gray-900 dark:text-white">
        <p>Loading exercise...</p>
      </div>

      <template v-else-if="exercise && currentSentence">
        <div class="mb-8">
          <button
            @click="router.push('/dashboard')"
            class="text-sm text-gray-600 hover:text-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ← Back to Dashboard
          </button>
          <h1 class="mt-4 text-2xl font-bold text-gray-900 dark:text-white">{{ exercise.title }}</h1>
          <p class="mt-2 text-gray-600 dark:text-gray-400">{{ exercise.description }}</p>
        </div>

        <!-- Progress bar -->
        <div class="mb-6">
          <div class="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
            <span>Progress</span>
            <span>{{ progress.current }} / {{ progress.total }}</span>
          </div>
          <div class="h-2 bg-gray-200 rounded-full dark:bg-gray-700">
            <div 
              class="h-2 bg-blue-600 rounded-full dark:bg-blue-500 transition-all duration-300"
              :style="{ width: `${progress.percentage}%` }"
            ></div>
          </div>
        </div>

        <div class="rounded-lg bg-white p-6 shadow dark:bg-gray-800">
          <!-- Main sentence -->
          <div class="mb-6 space-y-4">
            <p class="text-2xl font-medium text-gray-900 dark:text-white">
              {{ currentSentence.content }}
            </p>
            
            <!-- Transcriptions -->
            <div class="space-y-2">
              <div v-if="currentSentence.ipa_transcription" class="text-sm">
                <span class="text-gray-500 dark:text-gray-400">IPA: </span>
                <span class="font-mono text-gray-900 dark:text-white">{{ currentSentence.ipa_transcription }}</span>
              </div>
              <div v-if="currentSentence.arpabet_transcription" class="text-sm">
                <span class="text-gray-500 dark:text-gray-400">ARPABET: </span>
                <span class="font-mono text-gray-900 dark:text-white">{{ currentSentence.arpabet_transcription }}</span>
              </div>
            </div>

            <!-- Translation -->
            <div v-if="currentSentence.translation_ru" class="text-gray-600 dark:text-gray-400">
              {{ currentSentence.translation_ru }}
            </div>

            <!-- Sentence stats -->
            <div class="flex gap-4 text-sm text-gray-500 dark:text-gray-400">
              <span>Words: {{ currentSentence.word_count }}</span>
              <span>Characters: {{ currentSentence.char_count_total }}</span>
              <span>Level: {{ currentSentence.difficulty_level }}</span>
            </div>
          </div>

          <!-- Audio controls -->
          <div class="mb-6 space-y-4">
            <button
              @click="speakSentence"
              class="flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              </svg>
              Listen to Example
            </button>

            <AudioRecorder
              :sentence="currentSentence"
              @score="handlePronunciationScore"
            />
          </div>

          <!-- Navigation controls -->
          <div class="flex flex-wrap gap-4">
            <button
              @click="nextSentence"
              :disabled="!canProceed"
              class="rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed dark:bg-green-500 dark:hover:bg-green-600"
            >
              Next
            </button>

            <button
              @click="skipSentence"
              class="rounded-md border border-gray-300 px-4 py-2 text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
            >
              Skip
            </button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>