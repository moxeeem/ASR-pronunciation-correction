from uuid import UUID
from supabase import create_client, Client
from postgrest.base_request_builder import APIResponse
import pprint


from pronunciation_api.config import (
    SB_KEY,
    SB_URL,
    SENTENCES_TABLE,
    PROGRESS_TABLE
)

print(f"URL IS {SB_URL}")
print(f"KEY IS {SB_KEY}")

# создание клиента Supabase
supabase: Client = create_client(
    supabase_url=SB_URL,
    supabase_key=SB_KEY
)


def get_sentence_by_id(sentence_id: UUID) -> list[dict]:
    resp: APIResponse = supabase.table(
        SENTENCES_TABLE
    ).select("*").eq("id", sentence_id).execute()
    return resp.data


def get_all_sentences():
    return supabase.table(SENTENCES_TABLE).select("*").execute()


def get_uncompleted_sentence_ids(user_id: UUID) -> list[dict]:
    # Запрос для получения ID предложений, которые не завершены пользователем
    resp_progress: APIResponse = (
        supabase.table(PROGRESS_TABLE)
        .select("sentence_id")
        .eq("user_id", user_id)
        .neq("status", "completed")
        .execute()
    )
    # print(progress_response)
    # Извлекаем sentence_id из результатов
    uncompleted_sentence_ids = [
        record["sentence_id"] for record in resp_progress.data
    ]
    return uncompleted_sentence_ids


def get_sentences_with_length(length_group: int, uncompleted_sentence_ids: list) -> list[dict]:
    # Запрос для получения предложений с заданным уровнем сложности и исключением завершенных предложений
    resp_sentences: APIResponse = (
        supabase.table(SENTENCES_TABLE)
        .select("*")
        .eq("difficulty_level", length_group)
        .in_("id", uncompleted_sentence_ids)
        .execute()
    )
    return resp_sentences.data


# print(get_uncompleted_sentence_ids(UUID("95be94d1-fd5c-46e8-89ca-2740cc64ca24")))
# print(get_sentences_with_length(1))
if __name__ == "__main__":
    pprint.pp(get_sentence_by_id(UUID("11693b19-e25b-4b2a-8e5f-d0595f685d77")))