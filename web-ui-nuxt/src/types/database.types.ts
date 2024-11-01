export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json }
  | Json[]

export interface Database {
  public: {
    Tables: {
      tasks: {
        Row: {
          completed: boolean | null
          created_at: string | null
          id: number
          title: string | null
          user: string
        }
        Insert: {
          completed?: boolean | null
          created_at?: string | null
          id?: number
          title?: string | null
          user: string
        }
        Update: {
          completed?: boolean | null
          created_at?: string | null
          id?: number
          title?: string | null
          user?: string
        }
      }
      text_data: {
        Row: {
          text_id: number
          en_sentence: string
          sentence_length_group: string
        }
        Insert: {
          text_id: number
          en_sentence: string
          sentence_length_group: string
        }
        Update: {
          text_id: number
          en_sentence: string
          sentence_length_group: string
        }
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      [_ in never]: never
    }
    Enums: {
      [_ in never]: never
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}
