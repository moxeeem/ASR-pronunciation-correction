import os
import tempfile
from pathlib import Path
from enum import Enum
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from transformers.feature_extraction_utils import BatchFeature
import librosa
import numpy as np
import torch
from pronunciation_api.config import LOCAL_MODEL_PATH
import pprint


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


# TODO: remove from global scope!
print("[info] Model local path", LOCAL_MODEL_PATH)
if LOCAL_MODEL_PATH is None:
    raise RuntimeError("local model path env variable not set!")

# Load the model and processor
processor, model = load_model(
    LoadingMethod.Locally,
    local_path=Path(LOCAL_MODEL_PATH),
)


def load_audio(audio_content) -> np.ndarray:
    """
    Loads and normalizes audio from a byte array to 16 kHz.
    """
    print(f"[info] (load_audio) audio_content is {type(audio_content)}")
    audio, _ = librosa.load(audio_content, sr=16000)
    return audio


def transcribe_audio(audio_content_as_ndarray: np.ndarray) -> str:
    """
    Processes the audio and returns its phoneme transcription.
    """
    processed_res: BatchFeature = processor(
        audio_content_as_ndarray,
        return_tensors="pt",
        padding=False
    )
    print("[debug] transcribe_audio processed_res is:")
    pprint.pp([type(processed_res), processed_res])

    input_values = processed_res.input_values
    pprint.pp([type(input_values), input_values])
    
    # get logits and predictions
    with torch.no_grad():
        logits = model(input_values).logits
        print("[debug] logits:")
        pprint.pp([type(logits), logits])

    predicted_ids = torch.argmax(
        logits,
        dim=-1
    )

    # decoding
    transcription: list[str] = processor.batch_decode(
        predicted_ids, clean_up_tokenization_spaces=True
    )
    # return only the transcription string
    return transcription[0]


def transcribe_audio_via_tempfile(file_content: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file_content)
        tmp_file.flush()
        temp_file_path = tmp_file.name

    try:
        audio_np, sr = librosa.load(temp_file_path, sr=16000)
        print("[debug] (transcribe_audio_via_tempfile) sampling rate from librosa")
        pprint.pp(sr)
        transcription = transcribe_audio(audio_np)
    finally:
        os.remove(temp_file_path)

    return transcription
