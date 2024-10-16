import torch
import torch.nn as nn

# Globals for storing models
MODELS_ASR: dict[str, tuple[nn.Module, nn.Module]] = {}
SUPPORTED_LANGUAGES = ["en"]


def preloadASRModels(languages: list[str]) -> None:
    """
    Preloads ASR (like Silero-STT) models weights
    for specified language codes: "en"
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


# preload models
preloadASRModels(["en"])
