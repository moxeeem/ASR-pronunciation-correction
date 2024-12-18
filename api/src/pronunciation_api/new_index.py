from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pronunciation_api.supabase_queries import get_sentence_by_id
import pronunciation_api.speech_to_score as speech2score
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
    result = speech2score.get_transcription_result(
        audio_content,
        real_text=sentence["content"],
        transcription_actual=sentence["ipa_transcription"],
    )
    return {"result": result}
