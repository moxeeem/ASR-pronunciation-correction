# 📚 Тренажер произношения на английском языке
![img](/img/cover.png)

*Веб-сервис доступен [здесь](https://asr-pronunciation-correction.vercel.app/)*

## Описание проекта

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white) ![wav2vec2](https://img.shields.io/badge/wav2vec2-FFCE00?style=flat-square&logo=huggingface&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) ![Supabase](https://img.shields.io/badge/Supabase-3ECF8E?style=flat-square&logo=supabase&logoColor=white) ![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white) ![Nuxt 3](https://img.shields.io/badge/Nuxt_3-00DC82?style=flat-square&logo=nuxtdotjs&logoColor=white) ![Vite.js](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

Этот проект представляет систему автоматической коррекции произношения на английском языке с использованием нейронной сети, основанной на архитектуре Wav2Vec 2.0. В рамках разработки был создан специализированный датасет для решения задачи обнаружения ошибок в произношении на фонемном уровне.

Также рассматривается интеграция модели в веб-сервис, предназначенный для обучения пользователей иностранным языкам.

## Содержание

- [📚 Тренажер произношения на английском языке](#-тренажер-произношения-на-английском-языке)
  - [Описание проекта](#описание-проекта)
  - [Содержание](#содержание)
  - [Структура репозитория](#структура-репозитория)
  - [Датасет](#датасет)
  - [Модель](#модель)
  - [Структурная схема решения](#структурная-схема-решения)
  - [Веб-сервис](#веб-сервис)
  - [Настройка базы данных](#настройка-базы-данных)
  - [Веб-приложение](#веб-приложение)
  - [Авторы](#авторы)
  - [Лицензия](#лицензия)

## Структура репозитория
- [/analysis](https://github.com/moxeeem/ASR-pronunciation-correction/tree/main/analysis) : Jupyter Notebook файлы с обработкой датасетов
- [/api](https://github.com/moxeeem/ASR-pronunciation-correction/tree/main/api) : API веб-сервиса
- [/web-ui-nuxt](https://github.com/moxeeem/ASR-pronunciation-correction/tree/main/web-ui-nuxt) : Графический интерфейс веб-сервиса



## Датасет

В качестве датасета для дообучения модели использовалась комбинация из пяти датасетов.

| Название | Разметка | Содержит ли ошибки произношения | Процент в общем датасете | Длительность (час) |
|-----------|-----------|---------------------------|----------------------|------------------|
| TIMIT | IPA | - | 32.14 % | 5.4 |
| L2-ARCTIC | IPA | + | 35.71 % | 6 |
| Common Voice | IPA, wav2vec2 | + | 16.07 % | 2.7 |
| LJ-speech | IPA, gruut | - | 8.04 % | 1.37 |
| LibriSpeech | IPA, gruut | - | 8.04 % | 1.37 |

Фонемы в объединенном датасете были приведены к формату IPA.

Общее время датасета составило 16.8 часов, из которых:
- 8.7 часов датасетов с ошибками;
- 8.14 часов датасетов без ошибок. 
Общий объем аудиофайлов составил **15112** записей различной длительности.

Каждая запись в датасете имеет следующие атрибуты:
- `audio_path`: путь к wav-файлу (16 кГц);
- `sentence`: исходное предложение на английском языке;
- `phonemes`: список фонемных транскрипций для каждого слова;
- `duration`: длительность аудиозаписи в секундах;
- `dataset`: источник данных (TIMIT, CV, LS, LJ, L2).

---
- Для фонемной транскрпиции TIMIT и L2-ARCTIC использовались преобразованные в IPA фонемы формата ARPABET, поставляемые с датасетами.
Для этого вручную были созданы два маппинга: один для преобразования TIMIT, другой - для L2-ARCTIC.

- Для разметки датасета Common Voice была использована модель [wav2vec2-large-xlsr-53-l2-arctic-phoneme](https://huggingface.co/mrrubino/wav2vec2-large-xlsr-53-l2-arctic-phoneme).

- Для разметки LJ-speech и LibriSpeech использовалась библиотека gruut, которая преобразует текст в IPA-формат. 

## Модель

В качестве модели для дообучения использовалась предварительно обученная модель [wav2vec2-large-xlsr-53](https://huggingface.co/facebook/wav2vec2-large-xlsr-53).

Итоговое значение метрики **CER (Character Error Rate) = 0.1**.

Дообученная модель опубликована на HuggingFace: [![HuggingFace](https://img.shields.io/badge/HuggingFace-Model-yellow?style=flat-square&logo=huggingface&logoColor=white)](https://huggingface.co/moxeeeem/wav2vec2-finetuned-pronunciation-correction)

## Структурная схема решения

<p align="center">
  <img src="img\structure_schema.png" alt="Структурная схема решения" width="85%">
</p>


## Веб-сервис

API приложения разработан на базе фреймворка **FastAPI**.

**Основные функции:**

1. Предоставление предложений для тренировки 
   - Сервис выбирает случайное предложение из базы данных на основе уровня сложности и текущего прогресса пользователя.  
   - База данных содержит тексты предложений, их фонетические транскрипции и уровни сложности.

2. Оценка произношения
   - Пользователь загружает аудиофайл, который обрабатывается с помощью предобученной модели Wav2Vec2.  
   - Модель транскрибирует речь, сравнивая результат с эталонной транскрипцией из базы данных.  
   - Формируется процентное соответствие и обратная связь для пользователя.

**Docker:**

- Для упрощения развертывания был создан [Docker-контейнер](https://github.com/moxeeem/ASR-pronunciation-correction/blob/main/api/Dockerfile) с возможностью пересборки через [скрипт](https://github.com/moxeeem/ASR-pronunciation-correction/blob/main/api/rebuild_container.sh).


## Инструкция по установке

* Склонировать репозиторий <https://github.com/moxeeem/ASR-pronunciation-correction.git>;

### Настройка бэкэнда

Установить зависимости:

```shell
python install -r
```

* Переименовать файл `.env.example` в `.env` и указать переменные окружения:
  * `SUPABASE_URL` (url к базе данных supabase, где хранятся упражнения);
  * `SUPABASE_KEY` (ключ управления supabase);
  * `LOCAL_MODEL_PATH` (локальный путь к модели / ссылка на модель через hugging face);
  * `MODEL_SOURCE`=`'LOCAL'`/`'HF'` (путь загрузки модели - локально или через hugging face).

**Запуск API:**

```shell
cd api/
python -m uvicorn src.pronunciation_api.api:app --reload
```

### Настройка фронтэнда

Установить зависимости:

```shell
npm install
```

* Переименовать файл `.env.example` в `.env` и указать переменные окружения:
  * `SUPABASE_URL` (url к базе данных supabase, где хранятся упражнения);
  * `SUPABASE_KEY` (ключ управления supabase);
  * `DATABASE_URL` (url к базе данных для миграций);
    * например:
    `postgresql://postgres.padludpvkvposslxxcky:[вашпароль]@aws-0-eu-central-2.pooler.supabase.com:6543/postgres`
  * `BACKEND_API_URL` (url бэкэнда).
    * например:
    `http://127.0.0.1:8000/`

**Запуск приложения:**

```shell
cd web-ui-nuxt/
npm run dev
```

### Настройка базы данных

При желании замены датасета с предложениями создать файл `.csv`.
Пример оформления `.csv` файла с упражнениями:

| Название столбца | Тип | Пример | Пояснение |
|---|---|---|---|
| content | string | It's all over between us. | Текст предложения |
| sentence_length_group | enum("small", "medium", "large") | small | Размер предложения |
| ipaTranscription | string | ɪts ɔl oʊvɚ bɪtwin ʌs | Транскрипция в ipa |
| arpabetTranscription | string | H1-T-S AO1-L OW1-V-ER0 B-IH0-T-W-IY1-N AH1-S | Транскрипция в ARPABET |
| wordCount | integer | 5 | Количество слов |
| charCountNoSpaces | integer | 21 | Количество символов (без пробелов) |
| charCountTotal | integer | 25 | Количество символов (с пробелами) |
| difficultyLevel | integer | 2 | Уровень сложности |
| translationRu | string |  | Перевод |

#### Проведение миграций

Схема drizzle находится по пути [```web-ui-nuxt/drizzle/schema.ts```](https://github.com/moxeeem/ASR-pronunciation-correction/blob/main/web-ui-nuxt/drizzle/schema.ts)

Для генерации миграций запустить код в терминале Powershell:

```shell
npx drizzle-kit generate --config drizzle.config.ts 
# генерирует миграции из описания схемы PostgreSQL
npx drizzle-kit migrate --config drizzle.config.ts
# осуществление миграции. Для этого и нужна переменная DATABASE_URL
```

#### Заполнение базы данных

Для заполнения базы данных запустить код:

```shell
npx run seed:sentences
npx run seed:exercises
```


## Веб-приложение

Для разработки веб-приложения использовались TypeScript, Vue.js 3, Nuxt 3, Vite.js.

**Скриншоты работы приложения:**

- Окно авторизации
<p align="center">
  <img src="img\auth.png" alt="Окно авторизации" width="60%">
</p>

- Выбор упражнений
<p align="center">
  <img src="img\selection.png" alt="Выбор упражнений" width="60%">
</p>

- Упражнение
<p align="center">
  <img src="img\task.png" alt="Упражнение" width="60%">
</p>

- Результат выполнения упражнения
<p align="center">
  <img src="img\result.png" alt="Результат выполнения упражнения" width="60%">
</p>

## Авторы
[![Михаил Дорохин](https://img.shields.io/badge/Михаил_Дорохин-GitHub-black?style=flat-square&logo=github&logoColor=white)](https://github.com/Quasarel)  
[![Виктор Хованов](https://img.shields.io/badge/Виктор_Хованов-GitHub-black?style=flat-square&logo=github&logoColor=white)](https://github.com/m0rphed)  
[![Максим Иванов](https://img.shields.io/badge/Максим_Иванов-GitHub-black?style=flat-square&logo=github&logoColor=white)](https://github.com/moxeeem)


## Лицензия

Данный репозиторий лицензируется по лицензии MIT. Дополнительную информацию см. в файле [LICENSE](/LICENSE).
