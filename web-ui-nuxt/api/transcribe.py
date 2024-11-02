from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import librosa

# Загрузка модели и процессора при инициализации модуля
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-xlsr-53-espeak-cv-ft")


def load_audio(file_path: str):
    """
    Загружает и нормализует аудиофайл до 16 кГц.
    """
    audio, _ = librosa.load(file_path, sr=16000)
    return audio


def transcribe_audio(file_path: str):
    """
    Обрабатывает аудиофайл и возвращает его фонемную транскрипцию.
    """
    # Загрузка и подготовка аудио
    audio_input = load_audio(file_path)
    # Токенизация
    input_values = processor(audio_input, return_tensors="pt", padding=False).input_values
    # Получение логитов и предсказаний
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    # Декодирование
    transcription = processor.batch_decode(predicted_ids, clean_up_tokenization_spaces=True)
    return transcription[0]  # Возвращаем только строку транскрипции
