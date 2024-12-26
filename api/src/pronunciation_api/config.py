import os
from pathlib import Path
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from pronunciation_api.utils import try_get_env_vars
from dataclasses import dataclass


_required = [
    "SUPABASE_URL",
    "SUPABASE_KEY",
    "MODEL_SOURCE"
    # "LOCAL_MODEL_PATH"
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
SB_URL: str             = _env["SUPABASE_URL"]
SB_KEY: str             = _env["SUPABASE_KEY"]

# print(f"[DEBUG] SUPABASE: URL, KEY: {SB_URL} {SB_KEY}")
# Local path (specify if needed)
MODEL_SOURCE: str | None = os.getenv("MODEL_SOURCE", "HF")
LOCAL_MODEL_PATH: str | None = os.environ.get("LOCAL_MODEL_PATH")

# table that holds English sentences data
#  in the DB of choice (Supabase for now)
SENTENCES_TABLE         = "sentences"
PROGRESS_TABLE          = "user_exercise_sentence_progress"


@dataclass()
class PhoneticTranscriptionModelContainer:
    processor: None | Wav2Vec2Processor = None
    model: None | Wav2Vec2ForCTC = None
    is_loaded: bool = False

    def load_from_path(self, local_path: str) -> "PhoneticTranscriptionModelContainer":
        path = Path(local_path)
        if path.exists() and path.is_dir():
            self.processor = Wav2Vec2Processor.from_pretrained(path)
            self.model = Wav2Vec2ForCTC.from_pretrained(path)
            self.is_loaded = True
            return self
        
        raise RuntimeError(f"Wrong path specified {path}")

    def load_from_huggingface(self, hf_uri: str) -> "PhoneticTranscriptionModelContainer":
        self.processor = Wav2Vec2Processor.from_pretrained(hf_uri)
        self.model = Wav2Vec2ForCTC.from_pretrained(hf_uri)
        self.is_loaded = True
        return self
