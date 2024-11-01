import pandas as pd
import random
from PhonemeConverter import get_phonetic_transcription

# Загрузка данных из CSV файла
df = pd.read_csv('backend/text_data')


def get_sample_response(sentence_length_group: str) -> dict:
    """
    Возвращает JSON ответ со случайным предложением и его транскрипцией.
    """
    # Фильтруем DataFrame по категории
    filtered_df = df[df['sentence_length_group'] == sentence_length_group]

    # Выбираем случайное предложение
    random_row = filtered_df.sample(n=1).iloc[0]
    en_sentence = random_row.get("en_sentence", "N/A")
    sentence_length_group = random_row.get("sentence_length_group", "N/A")

    # Получаем фонетическую транскрипцию
    phonetic_transcription = get_phonetic_transcription(en_sentence)

    # Формируем JSON-ответ
    response_data = {
        "en_sentence": en_sentence,
        "sentence_length_group": sentence_length_group,
        "phonetic_transcription": phonetic_transcription
    }

    return response_data
