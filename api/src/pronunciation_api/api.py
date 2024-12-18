from fastapi import FastAPI, Form, File, UploadFile, HTTPException
# from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from pronunciation_api.transcribe import transcribe_audio_via_tempfile
from pronunciation_api.phoneme_converter import get_phonetic_transcription
from pronunciation_api.speech_to_score import get_transcription_result

app = FastAPI(
    title="Speech Pronunciation Assessment API",
    description="API для оценки произношения и получения фонетической транскрипции",
    version="0.1.0",
)


class TranscribeTextRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Текст для фонетической транскрипции",
    )


class TranscribeAudioRequest(BaseModel):
    audio: UploadFile
    reference_text: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Эталонный текст для сравнения"
    )


class TranscriptionResponse(BaseModel):
    transcription: str
    pronunciation_accuracy: float | None = None


@app.post(
    "/api/transcribe/text",
    response_model=TranscriptionResponse
)
async def transcribe_text(request: TranscribeTextRequest):
    """
    Получение фонетической транскрипции текста с использованием phonemizer (+ espeak)
    """
    try:
        phonetic_transcription = get_phonetic_transcription(request.text)
        return {"transcription": phonetic_transcription}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/transcribe/audio", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(...), reference_text: str = Form(...)
):
    """
    Транскрибация аудио с оценкой точности произношения
    """
    try:
        # Чтение содержимого файла
        audio_content = await audio.read()

        # Получение результатов транскрибации
        result = get_transcription_result(audio_content)

        return {
            "transcription": result["transcription"],
            "pronunciation_accuracy": result["accuracy"],
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
