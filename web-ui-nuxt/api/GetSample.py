from supabase import create_client, Client
from dotenv import load_dotenv
import os
import random
from api.PhonemeConverter import get_phonetic_transcription

# Загрузка переменных окружения
load_dotenv()
sb_url: str = os.environ.get("SUPABASE_URL")
sb_key: str = os.environ.get("SUPABASE_KEY")

# Создание клиента Supabase
supabase: Client = create_client(supabase_url=sb_url, supabase_key=sb_key)


def get_sample_response(sentence_length_group: str) -> dict:
    """
    Возвращает JSON ответ со случайным предложением и его транскрипцией.
    """
    # Получаем данные из таблицы Text_data
    data = supabase.table("Text_data").select("*").execute()

    # Преобразуем данные в список словарей
    records = data.data  # Содержимое данных будет доступно через data.data

    # Фильтруем записи по категории sentence_length_group
    filtered_records = [record for record in records if record['sentence_length_group'] == sentence_length_group]

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
        "phonetic_transcription": phonetic_transcription
    }

    return response_data
