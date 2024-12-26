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
}

export interface ExerciseSentence {
  sentences: Sentence
}

export type CompletionStatus = 'not_started' | 'in_progress' | 'completed'