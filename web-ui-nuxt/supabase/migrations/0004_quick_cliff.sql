/*
  # Update user progress table

  1. Changes
    - Add sentences_skipped column to user_progress table
    - Add index on user_id and exercise_id for faster lookups
  
  2. Security
    - Enable RLS on user_progress table
    - Add policy for users to manage their own progress
*/

-- Add sentences_skipped column if it doesn't exist
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns 
    WHERE table_name = 'user_progress' AND column_name = 'sentences_skipped'
  ) THEN
    ALTER TABLE user_progress 
    ADD COLUMN sentences_skipped uuid[] DEFAULT '{}';
  END IF;
END $$;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_progress_user_exercise 
ON user_progress(user_id, exercise_id);

-- Enable RLS
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;

-- Add RLS policies
CREATE POLICY "Users can view their own progress"
ON user_progress FOR SELECT
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can update their own progress"
ON user_progress FOR UPDATE
TO authenticated
USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own progress"
ON user_progress FOR INSERT
TO authenticated
WITH CHECK (auth.uid() = user_id);