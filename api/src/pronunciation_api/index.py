from fastapi import FastAPI, HTTPException, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pronunciation_api.get_sample import get_sample_response
import pronunciation_api.speech_to_score as speech_to_score
from uuid import UUID

app = FastAPI()


class SentenceRequest(BaseModel):
    difficulty_level: int
    user_id: UUID


@app.post("/api/get_sample")
async def get_sample(request: SentenceRequest):
    response_data = get_sample_response(request.difficulty_level, request.user_id)

    if not response_data:
        raise HTTPException(
            status_code=404, detail="No data available for the specified category"
        )

    return JSONResponse(content=response_data)


@app.post("/api/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    text: str = Form(...),
    ipa: str = Form(...),
    arpabet: str = Form(...),
):
    audio_content = await audio.read()
    result = speech_to_score.get_transcription_result(audio_content)
    # transcription = transcribe_audio_from_file(audio_content)
    return {"result": result}


@app.get("/api")
def hello_world():
    return {"message": "Hello World", "api": "Python"}


@app.get("/api/test")
def test():
    return {"message": "Test"}


@app.get("/api/new")
def new_function():
    return {"message": "Это новая функция", "api": "Python API"}
