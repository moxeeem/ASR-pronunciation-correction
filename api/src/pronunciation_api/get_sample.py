import random
from pronunciation_api.phoneme_converter import get_phonetic_transcription
# from api.supabase_queries import get_sentences_with_length
from pronunciation_api.supabase_queries import *
from uuid import UUID

current_data = {}

'''class SentenceStorage:
    def __init__(self):
        self.current_data = {}

    def get_sample_response(self, difficulty_level: int, user_id: UUID) -> dict:
        uncompleted_sentence_ids = get_uncompleted_sentence_ids(user_id)

        if not uncompleted_sentence_ids:
            self.current_data = {"error": "No data available for the specified category"}
            return self.current_data

        data = get_sentences_with_length(difficulty_level, uncompleted_sentence_ids)
        records = data.data

        random_record = random.choice(records)
        content = random_record.get("content", "N/A")
        ipa_transcription = random_record.get("ipa_transcription", "N/A")

        self.current_data = {
            "content": content,
            "difficulty_level": difficulty_level,
            "ipa_transcription": ipa_transcription,
        }

        return self.current_data

    def get_current_data(self) -> dict:
        """Функция для получения текущих данных."""
        return self.current_data

sentence_storage = SentenceStorage()

sentence_storage.get_sample_response(difficulty_level=1, user_id=UUID("95be94d1-fd5c-46e8-89ca-2740cc64ca24"))
current_data = sentence_storage.get_current_data()'''


'''def get_sample_response(difficulty_level: int) -> dict:
    """
    Возвращает JSON ответ со случайным предложением и его транскрипцией.
    """
    # Получаем данные из таблицы с предложениями напрямую из бд (Supabase)
    data = get_sentences_with_length(
        difficulty_level
    )
    
    print("[DEBUG]", type(data), type(data.data))

    records = data.data  # Убедитесь, что это список словарей

    if not records:
        return {"error": "No data available for the specified category"}

    random_record = random.choice(records)
    content = random_record.get("content", "N/A")
    ipa_transcription = random_record.get("ipa_transcription", "N/A")

    response_data = {
        "content": content,
        "difficulty_level": difficulty_level,
        "ipa_transcription": ipa_transcription,
    }

    return response_data
'''


def get_sample_response(difficulty_level: int, user_id: UUID) -> dict:
    global current_data
    # Получаем незавершенные предложения для пользователя
    uncompleted_sentence_ids = get_uncompleted_sentence_ids(user_id)

    # Если нет подходящих предложений
    if not uncompleted_sentence_ids:
        return {"error": "No data available for the specified category"}

    # Получаем предложения из основной таблицы
    data = get_sentences_with_length(difficulty_level, uncompleted_sentence_ids)
    records = data.data

    # Выбираем случайное предложение
    random_record = random.choice(records)
    content = random_record.get("content", "N/A")
    ipa_transcription = random_record.get("ipa_transcription", "N/A")

    current_data = {
        "content": content,
        "difficulty_level": difficulty_level,
        "ipa_transcription": ipa_transcription,
    }

    return current_data


get_sample_response(difficulty_level=1, user_id=UUID("95be94d1-fd5c-46e8-89ca-2740cc64ca24"))
# print(current_data.get("ipa_transcription", "N/A"))
