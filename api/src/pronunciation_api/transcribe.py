from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import numpy as np
import librosa
import tempfile
import os

from pathlib import Path
from enum import Enum

LOCAL_MODEL_PATH = "C:\\Users\\morph\\Downloads\\my_phoneme_models\\checkpoint-2024.12.18-wav2vec2-phoneme\\final"


class LoadingMethod(str, Enum):
    FromHF = "model huggingface model"
    Locally = "model from local path"


def load_model(
    method: LoadingMethod, hf_uri: str | None = None, local_path: Path | None = None
) -> tuple[Wav2Vec2Processor, Wav2Vec2ForCTC]:
    match method:
        case LoadingMethod.FromHF:
            if hf_uri is None:
                raise RuntimeError("Provide valid HF uri for downloading model")

            processor = Wav2Vec2Processor.from_pretrained(hf_uri)
            model = Wav2Vec2ForCTC.from_pretrained(hf_uri)
            return processor, model

        case LoadingMethod.Locally:
            if local_path is None:
                raise RuntimeError(
                    "Specify local path for loading model "
                    "locally from existing folder"
                )

            if local_path.exists() and local_path.is_dir():
                processor = Wav2Vec2Processor.from_pretrained(local_path)
                model = Wav2Vec2ForCTC.from_pretrained(local_path)
                return processor, model
            raise RuntimeError(f"Wrong path specified {local_path}")

        case _:
            raise RuntimeError(f"Unsupported model loading method {method}")


local_model_path = Path(LOCAL_MODEL_PATH)
# Load the model and processor
processor, model = load_model(
    LoadingMethod.Locally,
    # "mrrubino/wav2vec2-large-xlsr-53-l2-arctic-phoneme"
    local_path=local_model_path,
)


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
    input_values = processor(
        audio_content, return_tensors="pt", padding=False
    ).input_values
    # Get logits and predictions
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    # Decoding
    transcription = processor.batch_decode(
        predicted_ids, clean_up_tokenization_spaces=True
    )
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
