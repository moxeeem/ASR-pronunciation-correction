export interface UserProgress {
  id: string;
  user_id: string;
  exercise_id: string;
  completion_status: 'not_started' | 'in_progress' | 'completed';
  last_attempted: string;
  sentences_skipped: string[];
  rating?: number;
}

export interface ProgressUpdate {
  completion_status?: UserProgress['completion_status'];
  sentences_skipped?: string[];
  rating?: number;
}

export interface SentenceProgress {
  user_id: string;
  exercise_id: string;
  sentence_id: string;
  status: 'not_attempted' | 'completed' | 'skipped';
}