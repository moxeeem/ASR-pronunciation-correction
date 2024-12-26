import { ref } from 'vue'

export function useProgress() {
  const supabase = useSupabaseClient()
  const user = useSupabaseUser()
  
  const error = ref<string | null>(null)

  async function updateSentenceProgress(exerciseId: string, sentenceId: string, status: 'not_attempted' | 'completed' | 'skipped') {
    if (!user.value) return
    
    try {
      const { error: err } = await supabase
        .from('user_exercise_sentence_progress')
        .upsert({
          user_id: user.value.id,
          exercise_id: exerciseId,
          sentence_id: sentenceId,
          status
        })

      if (err) throw err
    } catch (e) {
      console.error('Failed to update sentence progress:', e)
      throw e
    }
  }

  async function checkExerciseCompletion(exerciseId: string): Promise<boolean> {
    if (!user.value) return false

    try {
      // Get all sentences for this exercise
      const { data: sentences, error: sentencesError } = await supabase
        .from('exercise_sentences')
        .select('sentence_id')
        .eq('exercise_id', exerciseId)

      if (sentencesError) throw sentencesError

      // Get progress for all sentences
      const { data: progress, error: progressError } = await supabase
        .from('user_exercise_sentence_progress')
        .select('status')
        .eq('exercise_id', exerciseId)
        .eq('user_id', user.value.id)

      if (progressError) throw progressError

      // Exercise is complete if all sentences are either completed or skipped
      // and at least one sentence is completed
      const hasCompletedSentence = progress.some(p => p.status === 'completed')
      const allSentencesAttempted = progress.length === sentences.length &&
        progress.every(p => p.status === 'completed' || p.status === 'skipped')

      return hasCompletedSentence && allSentencesAttempted
    } catch (e) {
      console.error('Failed to check exercise completion:', e)
      return false
    }
  }

  async function updateExerciseProgress(exerciseId: string) {
    if (!user.value) return

    try {
      const isCompleted = await checkExerciseCompletion(exerciseId)
      
      const { error: err } = await supabase
        .from('user_progress')
        .upsert({
          user_id: user.value.id,
          exercise_id: exerciseId,
          completion_status: isCompleted ? 'completed' : 'in_progress',
          last_attempted: new Date().toISOString()
        })

      if (err) throw err
    } catch (e) {
      console.error('Failed to update exercise progress:', e)
      throw e
    }
  }

  return {
    updateSentenceProgress,
    updateExerciseProgress,
    checkExerciseCompletion,
    error
  }
}