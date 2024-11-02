import random
from api.phoneme_converter import get_phonetic_transcription
from api.supabase_queries import get_sentences_with_length


def get_sample_response(sentence_length_group: str) -> dict:
    """
    Возвращает JSON ответ со случайным предложением и его транскрипцией.
    """
    # Получаем данные из таблицы с предложениями напрямую из бд (Supabase)
    data = get_sentences_with_length(
        sentence_length_group
    )
    
    print("[DEBUG]", type(data), type(data.data))

    # Преобразуем данные в список словарей
    records = data.data  # Содержимое данных будет доступно через data.data

    # Фильтруем записи по категории sentence_length_group
    filtered_records = [
        record
        for record in records
        if record["sentence_length_group"] == sentence_length_group
    ]

    if not filtered_records:
        return {"error": "No data available for the specified category"}

    # Выбираем случайное предложение
    random_record = random.choice(filtered_records)
    en_sentence = random_record.get("en_sentence", "N/A")
    sentence_length_group = random_record.get("sentence_length_group", "N/A")

    # Получаем фонетическую транскрипцию
    phonetic_transcription = get_phonetic_transcription(en_sentence)

    # Формируем JSON-ответ
    response_data = {
        "en_sentence": en_sentence,
        "sentence_length_group": sentence_length_group,
        "phonetic_transcription": phonetic_transcription,
    }

    return response_data
