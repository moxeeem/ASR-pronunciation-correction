from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pronunciation_api.supabase_queries import get_sentence_by_id
import pronunciation_api.transcribe as transcribe_api
import pronunciation_api.speech_to_score as speech_to_score_api
from uuid import UUID

app = FastAPI()


@app.post("/api/transcribe_sentence")
async def transcribe(
    audio: UploadFile = File(...),
    sentence_id: UUID = Form(...),
):
    audio_content: bytes = await audio.read()
    # TODO: check if get_sentence_by_id(sentence_id) returns non-empty list
    sentence = get_sentence_by_id(sentence_id)[0]
    result = speech_to_score_api.get_transcription_result(
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
        phonetic_transcription = transcribe_api.get_gruut_phonemes(eng_text)
        return {"ipa_gruut_transcription": phonetic_transcription}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
