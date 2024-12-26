import os
import tempfile
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from transformers.feature_extraction_utils import BatchFeature
import librosa
import numpy as np
import torch
import pprint


# def load_audio(audio_content: bytes) -> np.ndarray:
#     """
#     Loads and normalizes audio from a byte array to 16 kHz.
#     """
#     audio, _ = librosa.load(audio_content, sr=16000)
#     return audio


def transcribe_audio(
    processor: Wav2Vec2Processor,
    phonetic_model: Wav2Vec2ForCTC,
    audio_content_as_ndarray: np.ndarray
) -> tuple:
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
    return transcription[0], logits, predicted_ids


def transcribe_audio_via_tempfile(
    processor: Wav2Vec2Processor,
    phonetic_model:Wav2Vec2ForCTC,
    file_content: bytes
) -> tuple:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file_content)
        tmp_file.flush()
        temp_file_path = tmp_file.name
        print("TEMP FILE at:", temp_file_path)

    try:
        audio_np_arr, sr = librosa.load(temp_file_path, sr=16000)
        pprint.pp(sr)
        
        transcription, logits, predicted_ids = transcribe_audio(
            processor,
            phonetic_model,
            audio_np_arr
        )
    finally:
        os.remove(temp_file_path)

    return transcription, logits, predicted_ids


# Функция для получения временных меток фонем
def get_phoneme_timestamps(logits, predicted_ids, processor, audio, sampling_rate=16000):
    num_time_steps = logits.shape[1]
    audio_duration = len(audio) / sampling_rate
    time_per_step = audio_duration / num_time_steps

    phoneme_locations = []
    last_pred = -1
    start_time = 0

    for idx, predicted_id in enumerate(predicted_ids[0]):
        if predicted_id != last_pred:
            if last_pred != -1:
                decoded_char = processor.decode([last_pred]).strip()
                if decoded_char:
                    end_time = idx * time_per_step
                    phoneme_locations.append({
                        "phoneme": decoded_char,
                        "start_time": start_time,
                        "end_time": end_time
                    })
            start_time = idx * time_per_step
        last_pred = predicted_id

    decoded_char = processor.decode([last_pred]).strip()
    if decoded_char:
        end_time = audio_duration
        phoneme_locations.append({
            "phoneme": decoded_char,
            "start_time": start_time,
            "end_time": end_time
        })

    return phoneme_locations


# Функция для получения временных меток слов
def get_word_timestamps(transcription, logits, predicted_ids, processor, audio):
    phonemes = get_phoneme_timestamps(logits, predicted_ids, processor, audio)

    words = transcription.split()
    word_locations = []
    phoneme_idx = 0

    for word in words:
        word_start_time = None
        word_end_time = None
        current_word_phonemes = list(word)

        while phoneme_idx < len(phonemes) and current_word_phonemes:
            phoneme_data = phonemes[phoneme_idx]
            phoneme = phoneme_data["phoneme"]

            if phoneme == current_word_phonemes[0]:
                if word_start_time is None:
                    word_start_time = phoneme_data["start_time"]
                word_end_time = phoneme_data["end_time"]
                current_word_phonemes.pop(0)

            phoneme_idx += 1

        if word_start_time is not None and word_end_time is not None:
            word_locations.append({
                "word": word,
                "start_time": word_start_time,
                "end_time": word_end_time
            })

    return word_locations


'''
from pronunciation_api.config import PhoneticTranscriptionModelContainer, LOCAL_MODEL_PATH
path = "C:/Users/Asus/Desktop/ASR-model/test.wav"
audio_content, _ = librosa.load(path, sr=16000)
model_container = PhoneticTranscriptionModelContainer()
model_container.load_from_path(LOCAL_MODEL_PATH)

transcription, logits, predicted_ids = transcribe_audio(model_container.processor, model_container.model, audio_content)

phoneme_locations = get_phoneme_timestamps(logits, predicted_ids, model_container.processor, audio_content)
print("Phoneme timestamps:", phoneme_locations)

word_locations = get_word_timestamps(transcription, logits, predicted_ids, model_container.processor, audio_content)
print("Word timestamps:", word_locations)'''