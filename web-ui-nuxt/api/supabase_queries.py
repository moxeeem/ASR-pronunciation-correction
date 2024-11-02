from supabase import create_client, Client

# from supabase.lib import APIResponse
from api.config import SB_KEY, SB_URL, SENTENCES_TABLE

# создание клиента Supabase
supabase: Client = create_client(
    supabase_url=SB_URL,
    supabase_key=SB_KEY
)


def get_all_sentences():
    return supabase.table(SENTENCES_TABLE).select("*").execute()


def get_sentences_with_length(length_group: str):
    return (
        supabase.table(SENTENCES_TABLE)
        .select("*")
        # фильтры: https://supabase.com/docs/reference/python/using-filters
        .eq("sentence_length_group", length_group)
        .execute()
    )
