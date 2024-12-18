from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import numpy as np
import librosa
import tempfile
import os

# Load the model and processor
processor = Wav2Vec2Processor.from_pretrained("mrrubino/wav2vec2-large-xlsr-53-l2-arctic-phoneme")
model = Wav2Vec2ForCTC.from_pretrained("mrrubino/wav2vec2-large-xlsr-53-l2-arctic-phoneme")


def load_audio(audio_content):
    """
    Loads and normalizes audio from a byte array to 16 kHz.
    """
    audio, _ = librosa.load(audio_content, sr=16000)
    return audio


def transcribe_audio(audio_content: np.ndarray):
    """
    Processes the audio and returns its phoneme transcription.
    """
    input_values = processor(audio_content, return_tensors="pt", padding=False).input_values
    # Get logits and predictions
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    # Decoding
    transcription = processor.batch_decode(predicted_ids, clean_up_tokenization_spaces=True)
    return transcription[0]  # Return only the transcription string


def transcribe_audio_from_file(file_content):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file_content)
        tmp_file.flush()
        temp_file_path = tmp_file.name

    try:
        audio_np, sr = librosa.load(temp_file_path, sr=16000)
        transcription = transcribe_audio(audio_np)
    finally:
        os.remove(temp_file_path)

    return transcription
