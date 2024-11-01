from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from supabase import create_client, Client

# from GetSample import get_sample_response
#TODO: fix python modules problems related to api/ folder
import os

# sb_url: str = os.environ.get("SUPABASE_URL")
# sb_key: str = os.environ.get("SUPABASE_KEY")
sb_url: str = "https://tczadznejvcgkubymsoz.supabase.co"
sb_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjemFkem5lanZjZ2t1Ynltc296Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mjk4NTM4NjAsImV4cCI6MjA0NTQyOTg2MH0.e6vgqz64GGcqQu_Bxxv73cV_NsQuUNfE8pjnUglnBVg"
 
supabase: Client = create_client(
    supabase_url=sb_url,
    supabase_key=sb_key
)

app = FastAPI()


class SentenceRequest(BaseModel):
    sentence_length_group: str

# example usage of Supabase client to SELECT ALL from 'Text_data':
resp = supabase.table("Text_data").select("*").execute()

# wired fix encoding to utf-8
import sys
sys.stdout.reconfigure(encoding='utf-8')
# print fetched data
print(str(resp.data))
# see docs for SB in Python: https://supabase.com/docs/reference/python/select

@app.post("/getSample")
async def get_sample(request: SentenceRequest):
    # response_data = get_sample_response(request.sentence_length_group)
    resp = supabase.table("text_data").select("*").execute()
    print(resp["data"])
    
    if not True: #response_data:
        raise HTTPException(status_code=404, detail="No data available for the specified category")

    return JSONResponse(content=resp["data"])


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