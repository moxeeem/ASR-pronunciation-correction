import base64
import json
import time
from typing import Any
import os

import audioread
import numpy as np
import numpy.typing as npt
import torch
from torchaudio.transforms import Resample

import utils
import WordMatching as wm
import pronunciationTrainer as prTr

# Инициализация тренера для английского языка
trainer_SST_lambda: dict[str, prTr.PronunciationTrainer] = {"en": prTr.getTrainer("en")}

# Преобразование частоты дискретизации аудиосигнала с 48kHz до 16kHz
transform: Resample = Resample(
    orig_freq=48000,
    new_freq=16000
)


def lambda_handler(event: dict[str, Any], context: Any) -> str:
    """
    AWS Lambda хэндлер для обработки входящих данных и аудиофайлов.

    1. Распаковывает JSON данные, содержащие текст и аудиофайл.
    2. Сохраняет аудиофайл на диск и декодирует его.
    3. Применяет предобработку к аудиосигналу и вызывает тренер для обработки аудио относительно текста.
    4. Постобрабатывает результаты и возвращает их в виде JSON.

    Аргументы:
        event (dict): Входящее событие с данными, включая текст и закодированное аудио.
        context (Any): Контекст исполнения Lambda.

    Возвращает:
        str: JSON строка с результатами обработки транскрипций и аудио.
    """
    # Распаковка данных из запроса
    data: dict[str, str] = json.loads(event["body"])

    real_text = data["title"]
    file_bytes = base64.b64decode(data["base64Audio"][22:].encode("utf-8"))
    language = data["language"]

    # Если текст отсутствует, возвращаем пустой ответ
    if not real_text:
        return generate_response("")

    start = time.time()

    # Сохраняем закодированный аудиофайл на диск
    random_file_name = f"./{utils.generateRandomString()}.ogg"
    with open(random_file_name, "wb") as f:
        f.write(file_bytes)

    print("Time for saving binary in file: ", str(time.time() - start))

    # Загружаем и декодируем аудиофайл
    start = time.time()
    signal, fs = audioread_load(random_file_name)

    # Применяем преобразование частоты дискретизации
    signal = transform(torch.Tensor(signal)).unsqueeze(0)
    print("Time for loading .ogg file: ", str(time.time() - start))

    # Обрабатываем аудиофайл для заданного текста с помощью тренера
    result = trainer_SST_lambda[language].processAudioForGivenText(signal, real_text)

    # Удаляем временный файл
    start = time.time()
    os.remove(random_file_name)
    print("Time for deleting file: ", str(time.time() - start))

    # Постобработка результатов транскрипции и оценок произношения
    start = time.time()
    res = process_transcription_result(result)
    print("Time to post-process results: ", str(time.time() - start))

    # Возвращаем результат в формате JSON
    return json.dumps(res)


def generate_response(body: str) -> dict[str, Any]:
    """
    Генерирует стандартный HTTP-ответ для Lambda API.

    Аргументы:
        body (str): Тело ответа.

    Возвращает:
        dict: HTTP-ответ с кодом 200 и необходимыми заголовками.
    """
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
        },
        "body": body
    }


def process_transcription_result(result: dict[str, Any]) -> dict[str, Any]:
    """
    Обрабатывает результат транскрипции и оценки произношения.

    1. Извлекает исходный и транскрибированный текст в виде транскрипций IPA.
    2. Сравнивает транскрибированные слова с реальными.
    3. Оценивает правильность каждого символа и генерирует финальные результаты.

    Аргументы:
        result (dict): Результат обработки аудио и текста, включая оценки произношения.

    Возвращает:
        dict: Словарь с отформатированными данными по результатам транскрипции.
    """
    # Извлечение транскрипций IPA и оригинальных текстов
    real_transcripts_ipa = " ".join([word[0] for word in result["real_and_transcribed_words_ipa"]])
    matched_transcripts_ipa = " ".join([word[1] for word in result["real_and_transcribed_words_ipa"]])

    real_transcripts = " ".join([word[0] for word in result["real_and_transcribed_words"]])
    matched_transcripts = " ".join([word[1] for word in result["real_and_transcribed_words"]])

    # Преобразование в нижний регистр для сравнения реальных слов
    words_real = real_transcripts.lower().split()
    mapped_words = matched_transcripts.split()

    # Оценка правильности каждого символа в транскрибированных словах
    is_letter_correct_all_words = ''.join(
        ''.join([str(is_correct) for is_correct in wm.getWhichLettersWereTranscribedCorrectly(
            word_real, wm.get_best_mapped_words(mapped_words[idx], word_real)[0])]) + ' '
        for idx, word_real in enumerate(words_real)
    )

    # Категории точности для каждой пары слов
    pair_accuracy_category = ' '.join([str(category) for category in result['pronunciation_categories']])

    # Возвращаем отформатированные результаты
    return {
        'real_transcript': result['recording_transcript'],
        'ipa_transcript': result['recording_ipa'],
        'pronunciation_accuracy': str(int(result['pronunciation_accuracy'])),
        'real_transcripts': real_transcripts,
        'matched_transcripts': matched_transcripts,
        'real_transcripts_ipa': real_transcripts_ipa,
        'matched_transcripts_ipa': matched_transcripts_ipa,
        'pair_accuracy_category': pair_accuracy_category,
        'start_time': result['start_time'],
        'end_time': result['end_time'],
        'is_letter_correct_all_words': is_letter_correct_all_words
    }


def audioread_load(
    path: str,
    offset: float = 0.0,
    duration: float | None = None,
    dtype: np.dtype = np.float32
    ) -> tuple[npt.NDArray, int]:
    """
    Загружает аудиофайл с использованием библиотеки audioread и возвращает аудиосигнал и частоту дискретизации.

    1. Загружает аудиофайл блоками, начиная с заданного смещения (offset) и заканчивая через указанное время (duration).
    2. Преобразует аудиосигнал в массив с плавающей точкой.

    Аргументы:
        path (str): Путь к аудиофайлу.
        offset (float): Смещение начала загрузки аудио в секундах.
        duration (float): Продолжительность загрузки в секундах.
        dtype (np.dtype): Тип данных для аудиосигнала.

    Возвращает:
        tuple: Аудиосигнал в виде массива и частота дискретизации.
    """
    y: list = []
    with audioread.audio_open(path) as input_file:
        sr_native = input_file.samplerate
        n_channels = input_file.channels

        # Рассчитываем начальную и конечную точки считывания аудио
        s_start = int(np.round(sr_native * offset)) * n_channels
        s_end = np.inf if duration is None else s_start + (int(np.round(sr_native * duration)) * n_channels)

        n = 0
        for frame in input_file:
            frame = buf_to_float(frame, dtype=dtype)
            n_prev = n
            n = n + len(frame)

            if n < s_start:
                # Пропускаем кадры до нужного смещения
                continue
            if s_end < n_prev:
                # Если достигли конца, выходим
                break
            if s_end < n:
                # Если конец аудио сигнала в этом кадре, обрезаем его
                frame = frame[:s_end - n_prev]
            if n_prev <= s_start <= n:
                # Если начало аудио в этом кадре, загружаем его
                frame = frame[(s_start - n_prev):]

            # Добавляем кадр в список
            y.append(frame)

    # Конкатенируем блоки в один массив
    y_arr = np.concatenate(y) if y else np.empty(0, dtype=dtype)

    # Если сигнал многоканальный, преобразуем в нужный формат
    if n_channels > 1:
        y_arr = y_arr.reshape((-1, n_channels)).T

    return y_arr, sr_native


def buf_to_float(x: bytes, n_bytes: int = 2, dtype: np.dtype = np.float32) -> np.ndarray:
    """
    Конвертирует аудиобуфер из целых чисел в числа с плавающей точкой.

    Аргументы:
        x (bytes): Входной буфер с аудиоданными.
        n_bytes (int): Количество байт на семпл.
        dtype (np.dtype): Тип данных для выходного массива.

    Возвращает:
        np.ndarray: Аудио сигнал в формате с плавающей точкой.
    """
    # Преобразование данных из байтов в целочисленные значения и последующее масштабирование
    scale = 1.0 / float(1 << (8 * n_bytes - 1))
    fmt = f"<i{n_bytes}"
    return scale * np.frombuffer(x, fmt).astype(dtype)
