import random
# from pronunciation_api.phoneme_converter import get_gruut_phonemes
from pronunciation_api.supabase_queries import (
    get_uncompleted_sentence_ids,
    get_sentences_with_length,
)

from uuid import UUID

current_data = {}


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


if __name__ == "__main__":
    get_sample_response(
        difficulty_level=1, user_id=UUID("95be94d1-fd5c-46e8-89ca-2740cc64ca24")
    )

    # print(current_data.get("ipa_transcription", "N/A"))
