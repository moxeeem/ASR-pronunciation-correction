typescript
export interface Exercise {
  id: string
  title: string
  description: string
  created_at: string
  updated_at: string
}

export interface Sentence {
  id: string
  content: string
  ipa_transcription: string | null
  arpabet_transcription: string | null
  word_count: number
  char_count_no_spaces: number
  char_count_total: number
  difficulty_level: number
  translation_ru: string | null
}

export interface ExerciseSentence {
  sentences: Sentence
}

export type CompletionStatus = 'not_started' | 'in_progress' | 'completed'
