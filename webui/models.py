import torch
import torch.nn as nn
import pickle
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)

# Globals for storing models
MODELS_ASR: dict[str, tuple[nn.Module, nn.Module]] = {}
MODELS_TTS: dict[str, nn.Module] = {}
MODELS_TRANSLATION: dict[str, tuple[AutoModelForSeq2SeqLM, AutoTokenizer]] = {}
SUPPORTED_LANGUAGES = ["en", "fr", "de"]


def preloadASRModels(languages: list[str]) -> None:
    """
    Preloads ASR (like Silero-STT) models weights
    for specified language codes: "en", "fr", "de"
    """
    for lang_code in languages:
        if lang_code not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language code: '{lang_code}'"
            )

        model, decoder, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_stt",
            language=lang_code,
            device="cpu",
        )

        MODELS_ASR[lang_code] = (model, decoder)


def getASRModel(
    lang_code: str,
    device: torch.device = torch.device("cpu")
) -> tuple[nn.Module, nn.Module]:
    if lang_code not in MODELS_ASR.keys():
        raise ValueError(
            f"ASR model for language '{lang_code}' not preloaded"
        )

    model, decoder = MODELS_ASR[lang_code]
    # set device for ASR model
    model.to(device)
    return model, decoder


def preloadTTSModels(
    models_info: dict[str, str]
) -> None:
    for language, speaker in models_info.items():
        res = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language=language,
            speaker=speaker,
        )
        model = res[0]
        MODELS_TTS[language] = model


def get_model_TTS(
    lang_code: str,
    device: torch.device = torch.device("cpu")
) -> nn.Module:
    if lang_code not in MODELS_TTS:
        raise ValueError(
            f"TTS model for language '{lang_code}' not preloaded"
        )

    model = MODELS_TTS[lang_code]
    model.to(device)
    return model


def preloadTranslationModels(
    lang_models_pairs: dict[str, str]
) -> None:
    for lang, model_name in lang_models_pairs.items():
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        MODELS_TRANSLATION[lang] = (model, tokenizer)

        # cache models for faster access
        with open(f"translation_model_{lang}.pickle", "wb") as file_mod:
            pickle.dump(model, file_mod)

        with open(f"translation_tokenizer_{lang}.pickle", "wb") as file_tok:
            pickle.dump(tokenizer, file_tok)


def getTranslationModel(lang_code: str) -> tuple[
    AutoModelForSeq2SeqLM,
    AutoTokenizer
]:
    if lang_code not in MODELS_TRANSLATION:
        raise ValueError(
            f"Translation model for language '{lang_code}' not preloaded"
        )
    
    return MODELS_TRANSLATION[lang_code]


# preload models
preloadASRModels(["en", "de"])
ASR_models_info = {
        "de": "thorsten_v2",    # 16 kHz
        "en": "lj_16khz",       # 16 kHz
}

preloadTTSModels(ASR_models_info)

lang_model_pairs = {
    "de": "Helsinki-NLP/opus-mt-de-en"
}

preloadTranslationModels(lang_model_pairs)
