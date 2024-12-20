import { ref } from 'vue'
import type { UserProgress, ProgressUpdate } from '~/types/progress'

export function useProgress() {
  const supabase = useSupabaseClient()
  const user = useSupabaseUser()
  
  const progress = ref<UserProgress | null>(null)
  const error = ref<string | null>(null)
  const loading = ref(false)

  async function fetchProgress(exerciseId: string) {
    if (!user.value) return null
    
    try {
      loading.value = true
      const { data, error: err } = await supabase
        .from('user_progress')
        .select('*')
        .eq('user_id', user.value.id)
        .eq('exercise_id', exerciseId)
        .single()

      if (err) throw err
      progress.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch progress'
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateProgress(exerciseId: string, update: ProgressUpdate) {
    if (!user.value) return null

    try {
      loading.value = true
      const { data, error: err } = await supabase
        .from('user_progress')
        .upsert({
          user_id: user.value.id,
          exercise_id: exerciseId,
          last_attempted: new Date().toISOString(),
          ...update
        })
        .select()
        .single()

      if (err) throw err
      progress.value = data
      return data
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to update progress'
      return null
    } finally {
      loading.value = false
    }
  }

  return {
    progress,
    error,
    loading,
    fetchProgress,
    updateProgress
  }
}