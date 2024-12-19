from phonemizer import phonemize
from gruut import sentences
import re


def get_phonetic_transcription(sentence: str) -> str:
    """
    Функция для получения фонетической транскрипции предложения с помощью phonemizer в IPA (алфавит).
    """
    transcription = phonemize(
        sentence,
        language="en-us",
        backend="espeak",
    )
    return transcription


def get_gruut_phonemes(eng_text: str) -> str:
    # убираем знаки препинания
    eng_text = re.sub(r"[^\w\s]", "", eng_text)

    phonemes_list = []

    # разбиваем текст на предложения и слова, затем получаем фонемы
    for sent in sentences(
        eng_text,
        lang="en-US",
        espeak=False,
        punctuations=False,
        major_breaks=False,
        minor_breaks=False,
    ):
        for word in sent:
            if word.phonemes:  # если есть фонемы
                # объединяем фонемы слова без пробелов
                phonemes_list.append("".join(word.phonemes))

    # возвращаем строку: каждое слово разделено пробелом
    phonemes_with_stress_marks = " ".join(phonemes_list)
    return re.sub(r"[ˈˌ]", "", phonemes_with_stress_marks)


if __name__ == "__main__":
    print(get_gruut_phonemes("This is a test massage!"))
