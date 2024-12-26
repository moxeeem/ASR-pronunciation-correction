import { ref, computed, Ref } from 'vue'
import type { CompletionStatus, Sentence } from '~/types/exercise'

export function useExerciseProgress(sentences: Ref<Sentence[]>) {
  const currentIndex = ref(0)
  const completedSentences = ref(new Set<number>())
  const skippedSentences = ref(new Set<number>())

  const progress = computed(() => ({
    current: currentIndex.value + 1,
    total: sentences.value.length,
    percentage: ((completedSentences.value.size + skippedSentences.value.size) / sentences.value.length) * 100,
    completed: completedSentences.value.size,
    skipped: skippedSentences.value.size,
    remaining: sentences.value.length - (completedSentences.value.size + skippedSentences.value.size)
  }))

  const isCompleted = computed(() => 
    completedSentences.value.size + skippedSentences.value.size === sentences.value.length
  )

  function markCompleted(index: number) {
    completedSentences.value.add(index)
  }

  function markSkipped(index: number) {
    skippedSentences.value.add(index)
  }

  function moveNext() {
    if (currentIndex.value < sentences.value.length - 1) {
      currentIndex.value++
      return true
    }
    return false
  }

  async function updateExerciseStatus(
    supabase: any, 
    userId: string, 
    exerciseId: string
  ) {
    const status: CompletionStatus = isCompleted.value ? 'completed' : 'in_progress'
    
    try {
      await supabase
        .from('user_progress')
        .upsert({
          user_id: userId,
          exercise_id: exerciseId,
          completion_status: status,
          last_attempted: new Date().toISOString()
        })
    } catch (err) {
      console.error('Error updating exercise status:', err)
      throw err
    }
  }

  return {
    progress,
    isCompleted,
    currentIndex,
    markCompleted,
    markSkipped,
    moveNext,
    updateExerciseStatus
  }
}
