from phonemizer import phonemize


def get_phonetic_transcription(sentence: str) -> str:
    """
    Функция для получения фонетической транскрипции предложения с помощью Phonemizer в IPA (алфавит).
    """
    transcription = phonemize(
        sentence,
        language="en-us",
        backend="espeak",
    )
    return transcription
