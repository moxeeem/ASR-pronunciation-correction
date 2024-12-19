from uuid import UUID
from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from pronunciation_api.supabase_queries import get_sentence_by_id
from pronunciation_api.phoneme_converter import get_gruut_phonemes
import pronunciation_api.speech_to_score as speech_to_score_api
from pronunciation_api.config import (
    LOCAL_MODEL_PATH,
    PhoneticTranscriptionModelContainer
)


# create model container - keeps processor and model together
ipa_model_container = PhoneticTranscriptionModelContainer()

print("[info] Model local path", LOCAL_MODEL_PATH)
if LOCAL_MODEL_PATH is None:
    raise RuntimeError("LOCAL_MODEL_PATH environment variable WAS NOT SET!")

# load model for IPA phonetic transcription
ipa_model_container.load_from_path(LOCAL_MODEL_PATH)
print(f"[debug] IPA Model loaded {ipa_model_container.is_loaded}")

app = FastAPI()

# подключаем CORS
app.add_middleware(
    CORSMiddleware,
                            # разрешённые источники
    allow_origins=["*"],
                            # TODO: в данный момент разрешено всё - нужно поставить сюда BACKEND_API_URL 
    allow_credentials=True, # разрешить передачу cookies и авторизации
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],    # разрешённые заголовки (например, Authorization, Content-Type)
)

@app.post("/api/transcribe_sentence")
async def transcribe(
    audio: UploadFile = File(...),
    sentence_id: UUID = Form(...),
):
    audio_content: bytes = await audio.read()
    # TODO: check if get_sentence_by_id(sentence_id) returns non-empty list
    sentence = get_sentence_by_id(sentence_id)[0]
    result = speech_to_score_api.get_transcription_result(
        ipa_model_container,
        audio_content,
        real_text=sentence["content"],
        transcription_actual=sentence["ipa_transcription"],
    )
    return {"result": result}


@app.post("/api/transcribe_text_gruut")
async def transcribe_text(eng_text: str = Form(...)):
    """
    Получение фонетической транскрипции текста с использованием gruut (без espeak)
    """
    try:
        phonetic_transcription = get_gruut_phonemes(eng_text)
        return {"ipa_gruut_transcription": phonetic_transcription}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
