from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from api.get_sample import get_sample_response
from api.transcribe import transcribe_audio

app = FastAPI()


class SentenceRequest(BaseModel):
    sentence_length_group: str


@app.post("/api/get_sample")
async def get_sample(request: SentenceRequest):
    response_data = get_sample_response(request.sentence_length_group)

    if not response_data:
        raise HTTPException(
            status_code=404, detail="No data available for the specified category"
        )

    return JSONResponse(content=response_data)


@app.get("/api/transcribe")
async def transcribe():
    file_path = (
        "./test.wav"
    )
    transcription = transcribe_audio(file_path)
    return {"transcription": transcription}


'''@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    # Load and process the audio file
    content = await file.read()
    transcription = transcribe_audio(content)  # Replace with actual transcription logic
    return {"transcription": transcription}'''


@app.get("/api")
def hello_world():
    return {"message": "Hello World", "api": "Python"}


@app.get("/api/test")
def test():
    return {"message": "Test"}


@app.get("/api/new")
def new_function():
    return {"message": "Это новая функция", "api": "Python API"}
