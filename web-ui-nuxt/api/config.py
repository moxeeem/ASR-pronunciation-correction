from api.utils import try_get_env_vars

_required = [
    "SUPABASE_URL",
    "SUPABASE_KEY"
]

_all_loaded, _env = try_get_env_vars(
    _required,
    load_dotenv=True
)

if not _all_loaded:
    raise RuntimeError(
        f"Some of env. variables: {_required} "
        f"weren't loaded! Which were loaded: {_env.keys()}"
    )

# Supabase keys to connect to database
SB_URL: str = _env["SUPABASE_URL"]
SB_KEY: str = _env["SUPABASE_KEY"]

# table that holds English sentences data
#  in the DB of choice (Supabase for now)
SENTENCES_TABLE = "sentences"
PROGRESS_TABLE = "user_exercise_sentence_progress"
