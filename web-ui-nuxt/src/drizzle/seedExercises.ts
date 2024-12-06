import { db } from './index'; // Подключение к базе данных
import { exercises, exerciseSentences, sentences, userProgress, userExerciseSentenceProgress } from './schema'; // Импорт таблиц из схемы Drizzle
import { eq, lte, gt, and, between } from 'drizzle-orm'; // Импорт операторов
import { config } from 'dotenv';
import { createClient } from '@supabase/supabase-js';

config({ path: '.env' }); // Загрузка переменных окружения

// Подключение к Supabase
const supabaseUrl = process.env.SUPABASE_URL || '';
// SUPABASE_KEY для получения доступа к Auth должен быть уровня admin
const supabaseKey = process.env.SUPABASE_KEY || '';
const supabase = createClient(supabaseUrl, supabaseKey);

// Функция для получения случайного userId
async function getRandomUserId(): Promise<string| null> {
  const { data: { users }, error } = await supabase.auth.admin.listUsers()

  if (error) {
    console.error('Ошибка получения случайного пользователя:', error);
    throw new Error('Не удалось получить идентификатор пользователя');
  }

  if (users.length < 1) {
    console.error('Ошибка - не удалось получить id пользователя, т.к. в схеме auth пользователей не обнаружено', );
    throw new Error('В схеме auth пользователей не обнаружено - невозможно получить id');
  }

  return users && users.length > 0 ? users[0].id : null;
}

async function seedExercises() {
  console.log('Начало заполнения данных в таблицу exercises...');

  // Получаем случайного пользователя
  const userId = await getRandomUserId();
  if (!userId) {
    console.error('Не удалось получить идентификатор пользователя');
    return;
  }

  // Получаем предложения для упражнений на основе уровня сложности и длины
  const beginnerSentences = await db
    .select()
    .from(sentences)
    .where(and(eq(sentences.difficultyLevel, 1), lte(sentences.wordCount, 5)))
    .limit(10);

  const intermediateSentences = await db
    .select()
    .from(sentences)
    .where(and(eq(sentences.difficultyLevel, 2), between(sentences.wordCount, 6, 10)))
    .limit(10);

  const advancedSentences = await db
    .select()
    .from(sentences)
    .where(and(eq(sentences.difficultyLevel, 3), gt(sentences.wordCount, 10)))
    .limit(10);

  // Функция для добавления упражнения и связывания его с предложениями
  async function createExercise(title: string, description: string, sentenceRows: { id: string }[]) {
    // Вставка упражнения с использованием метода returning
    const [exercise] = await db
      .insert(exercises)
      .values({
        title,
        description,
      })
      .returning({ id: exercises.id });

    // Связка предложений с упражнением в таблице exerciseSentences
    const exerciseSentenceValues = sentenceRows.map((sentence) => ({
      exerciseId: exercise.id,
      sentenceId: sentence.id,
    }));
    await db.insert(exerciseSentences).values(exerciseSentenceValues);

    // Создание записи в user_progress для отслеживания статуса упражнения для пользователя
    await db.insert(userProgress).values({
      userId: userId,
      exerciseId: exercise.id,
      completionStatus: 'not started', // Начальный статус упражнения
      lastAttempted: new Date(),
      rating: null, // Рейтинг будет установлен после завершения
    });

    // Заполнение user_exercise_sentence_progress для каждого предложения упражнения
    const sentenceProgressValues = sentenceRows.map((sentence) => ({
      userId: userId,
      exerciseId: exercise.id,
      sentenceId: sentence.id,
      // status: 'not attempted', // Начальный статус для каждого предложения
    }));
    await db.insert(userExerciseSentenceProgress).values(sentenceProgressValues);
  }

  try {
    // Создание упражнений с привязкой предложений
    await createExercise(
      'Beginner Level',
      'Basic phrases and sentences for beginners',
      beginnerSentences
    );

    await createExercise(
      'Intermediate Level',
      'Intermediate phrases and sentences for everyday conversations',
      intermediateSentences
    );

    await createExercise(
      'Advanced Level',
      'Advanced phrases and sentences for fluent speakers',
      advancedSentences
    );

    console.log('Заполнение таблицы exercises завершено успешно!');
  } catch (error) {
    console.error('Ошибка при заполнении данных:', error);
  } finally {
    // if (db.close) {
    //   await db.close();
    // }
    console.log('Соединение с базой данных закрыто.');
  }
}

// Запуск функции заполнения
seedExercises().catch((error) => {
  console.error('Ошибка выполнения скрипта:', error);
});
