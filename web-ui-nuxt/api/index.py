from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.GetSample import get_sample_response

app = FastAPI()


class SentenceRequest(BaseModel):
    sentence_length_group: str


@app.post("/api/getSample")
async def get_sample(request: SentenceRequest):
    response_data = get_sample_response(request.sentence_length_group)

    if not response_data:
        raise HTTPException(status_code=404, detail="No data available for the specified category")

    return JSONResponse(content=response_data)


@app.get("/transcribe")
async def transcribe():
    """
    Возвращает фонемную транскрипцию аудиофайла test.wav.
    """
    file_path = "C:/Users/Asus/Desktop/ASR-model/test.wav"  # Укажите путь к вашему аудиофайлу
    transcription = transcribe_audio(file_path)
    return {"transcription": transcription}


@app.get("/api")
def hello_world():
    return {"message": "Hello World", "api": "Python"}


@app.get("/api/test")
def test():
    return {"message": "Test"}


@app.get("/api/new")
def new_function():
    return {"message": "Это новая функция", "api": "Python API"}
