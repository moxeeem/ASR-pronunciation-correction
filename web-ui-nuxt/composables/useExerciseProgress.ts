import { ref, computed } from 'vue'
import type { CompletionStatus } from '~/types/exercise'

export function useExerciseProgress(totalSentences: number) {
  const currentIndex = ref(0)
  const completedSentences = ref(new Set<number>())
  const skippedSentences = ref(new Set<number>())

  const progress = computed(() => ({
    current: currentIndex.value + 1,
    total: totalSentences,
    percentage: ((completedSentences.value.size + skippedSentences.value.size) / totalSentences) * 100,
    completed: completedSentences.value.size,
    skipped: skippedSentences.value.size,
    remaining: totalSentences - (completedSentences.value.size + skippedSentences.value.size)
  }))

  const isCompleted = computed(() => 
    completedSentences.value.size + skippedSentences.value.size === totalSentences
  )

  function markCompleted(index: number) {
    completedSentences.value.add(index)
  }

  function markSkipped(index: number) {
    skippedSentences.value.add(index)
  }

  function moveNext() {
    if (currentIndex.value < totalSentences - 1) {
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
