import { createReadStream } from 'fs';
import { parse } from 'csv-parse';
import { db } from './index'; // Подключение к базе данных
import { sentences } from './schema'; // Импорт таблицы из схемы Drizzle
import { config } from 'dotenv';

config({ path: '.env' }); // Загрузка переменных окружения

const csvFilePath = './text_augmented.csv';

// Определение типа для строки
interface SentenceData {
  content: string;
  ipaTranscription: string | null;
  arpabetTranscription: string | null;
  wordCount: number;
  charCountNoSpaces: number;
  charCountTotal: number;
  difficultyLevel: number;
  translationRu: string | null;
}

async function seedSentences() {
  console.log('Начало заполнения данных в таблицу sentences...');

  const sentencesData: SentenceData[] = [];

  // Настройки парсера для чтения CSV с разделителем ';'
  const parser = createReadStream(csvFilePath).pipe(
    parse({
      delimiter: ';',
      columns: true, // Использовать первую строку как заголовок столбцов
      skip_empty_lines: true
    })
  );

  // Чтение и преобразование данных
  for await (const row of parser) {
    const sentence: SentenceData = {
      content: row.content,
      ipaTranscription: row.ipaTranscription || null,
      arpabetTranscription: row.arpabetTranscription || null,
      wordCount: parseInt(row.wordCount, 10),
      charCountNoSpaces: parseInt(row.charCountNoSpaces, 10),
      charCountTotal: parseInt(row.charCountTotal, 10),
      difficultyLevel: parseInt(row.difficultyLevel, 10),
      translationRu: row.translationRu || null,
    };

    sentencesData.push(sentence);
  }

  // Вставка данных в таблицу
  try {
    // for (const sentence of sentencesData) {
    //   await db.insert(sentences).values(sentence);
    // }
    await db.insert(sentences).values(sentencesData); // Вставка данных в одном запросе
    console.log('Заполнение завершено успешно!');
  } catch (error) {
    console.error('Ошибка при заполнении данных:', error);
  }
}

// Вызов функции заполнения
seedSentences()
  .then(() => console.log("Скрипт завершен"))
  .catch((error) => console.error("Ошибка выполнения скрипта:", error));