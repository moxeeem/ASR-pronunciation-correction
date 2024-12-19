import {
  pgTable,
  text,
  timestamp,
  uuid,
  integer,
  jsonb,
  check,
  primaryKey,
} from 'drizzle-orm/pg-core';
import { sql } from 'drizzle-orm';

// Таблица для хранения предложений
export const sentences = pgTable('sentences', {
  id: uuid('id').primaryKey().defaultRandom(),
  content: text('content').notNull(),
  ipaTranscription: text('ipa_transcription'),
  arpabetTranscription: text('arpabet_transcription'),
  wordCount: integer('word_count').notNull(),
  charCountNoSpaces: integer('char_count_no_spaces').notNull(),
  charCountTotal: integer('char_count_total').notNull(),
  difficultyLevel: integer('difficulty_level').notNull(),
  translationRu: text('translation_ru'),
});

// Таблица для упражнений
export const exercises = pgTable('exercises', {
  id: uuid('id').primaryKey().defaultRandom(),
  title: text('title').notNull(),
  description: text('description').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// Связующая таблица между упражнениями и предложениями
export const exerciseSentences = pgTable(
  'exercise_sentences',
  {
    exerciseId: uuid('exercise_id')
      .notNull()
      .references(() => exercises.id),
    sentenceId: uuid('sentence_id')
      .notNull()
      .references(() => sentences.id),
  },
  (table) => ({
    pk: primaryKey({
      name: 'exercise_sentences_pk',
      columns: [table.exerciseId, table.sentenceId],
    }),
  })
);

// Таблица для отслеживания прогресса пользователя в упражнениях
export const userProgress = pgTable(
  'user_progress',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    userId: uuid('user_id').notNull(),
    exerciseId: uuid('exercise_id')
      .notNull()
      .references(() => exercises.id),
    completionStatus: text('completion_status')
      .default('not started')
      .notNull(),
    lastAttempted: timestamp('last_attempted').defaultNow().notNull(),
    rating: integer('rating'),
  },
  (table) => ({
    checkRatingOnCompletion: check(
      'rating_check',
      sql`${table.completionStatus} = 'done' AND ${table.rating} IS NOT NULL OR ${table.completionStatus} != 'done' AND ${table.rating} IS NULL`
    ),
  })
);

// Таблица профиля пользователя
export const userProfiles = pgTable('user_profiles', {
  userId: uuid('user_id').primaryKey(),
  avatarPath: text('avatar_path'),
  completedExercisesCount: integer('completed_exercises_count')
    .default(0)
    .notNull(),
  sentencesByDifficulty: jsonb('sentences_by_difficulty')
    .default('{}')
    .notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
});

// Новая таблица для отслеживания прогресса пользователя на уровне каждого предложения
export const userExerciseSentenceProgress = pgTable(
  'user_exercise_sentence_progress',
  {
    userId: uuid('user_id').notNull(), // Ссылка на пользователя
    exerciseId: uuid('exercise_id')
      .notNull()
      .references(() => exercises.id), // Ссылка на упражнение
    sentenceId: uuid('sentence_id')
      .notNull()
      .references(() => sentences.id), // Ссылка на предложение
    status: text('status').default('not attempted').notNull(), // Статус выполнения: 'not attempted', 'completed', 'skipped'
  },
  (table) => ({
    // Уникальность комбинации (user, exercise, sentence)
    uniqueUserExerciseSentence: primaryKey({
      name: 'user_exercise_sentence_progress_pk',
      columns: [table.userId, table.exerciseId, table.sentenceId],
    }),
  })
);
