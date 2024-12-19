import os
import tempfile
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from transformers.feature_extraction_utils import BatchFeature
import librosa
import numpy as np
import torch
import pprint


def load_audio(audio_content: bytes) -> np.ndarray:
    """
    Loads and normalizes audio from a byte array to 16 kHz.
    """
    
    audio, _ = librosa.load(audio_content, sr=16000)
    return audio


def transcribe_audio(
    processor: Wav2Vec2Processor,
    phonetic_model: Wav2Vec2ForCTC,
    audio_content_as_ndarray: np.ndarray
) -> str:
    """
    Processes the audio and returns its phoneme transcription.
    """
    processed_res: BatchFeature = processor(
        audio_content_as_ndarray, return_tensors="pt", padding=False
    )
    print("[debug] transcribe_audio processed_res is:")
    pprint.pp([type(processed_res), processed_res])

    input_values = processed_res.input_values
    pprint.pp([type(input_values), input_values])

    # get logits and predictions
    with torch.no_grad():
        logits: torch.Tensor = phonetic_model(input_values).logits
        print("[debug] logits:")
        pprint.pp([type(logits), logits])

    predicted_ids = torch.argmax(logits, dim=-1)

    # decoding
    transcription: list[str] = processor.batch_decode(
        predicted_ids, clean_up_tokenization_spaces=True
    )
    # return only the transcription string
    return transcription[0]


def transcribe_audio_via_tempfile(
    processor: Wav2Vec2Processor,
    phonetic_model:Wav2Vec2ForCTC,
    file_content: bytes
) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file_content)
        tmp_file.flush()
        temp_file_path = tmp_file.name

    try:
        audio_np_arr, sr = librosa.load(temp_file_path, sr=16000)
        pprint.pp(sr)
        
        transcription = transcribe_audio(
            processor,
            phonetic_model,
            audio_np_arr
        )
    finally:
        os.remove(temp_file_path)

    return transcription
