import pprint
from pronunciation_api.transcribe import transcribe_audio_via_tempfile
import pronunciation_api.word_matching as wm


def get_transcription_result(
    audio_content: bytes,
    real_text: str,
    transcription_actual: str
):
    print(f"[info] (get_transcription_result) {type(audio_content)}")
    transcription_IPA = transcribe_audio_via_tempfile(audio_content)
    words_ph_real: list[str] = transcription_actual.lower().split()
    words_estimated: list[str] = transcription_IPA.split()

    # TODO: можно ли извлечь из mapped_words_indices
    # какую-либо полезную информацию
    mapped_words, mapped_words_indices = wm.get_best_mapped_words(
        words_estimated, words_ph_real
    )

    correct_letters = "".join(
        "".join(
            [
                str(is_correct)
                for is_correct in wm.getWhichLettersWereTranscribedCorrectly(
                    word_real, wm.get_best_mapped_words(
                        mapped_words[idx],
                        word_real
                    )[0]
                )
            ]
        )
        + " "
        for idx, word_real in enumerate(words_ph_real)
    )

    accuracy = correct_letters.replace(" ", "").count("1") / len(
        correct_letters.replace(" ", "")
    )

    result = {
        "real_transcription": transcription_actual,
        "transcription": transcription_IPA,
        "correct_letters": correct_letters,
        "accuracy": accuracy,
    }

    return result


if __name__ == "__main__":
    transcription = "ðɪs ɪz ʌɛst mɛsɪd͡ʒ"
    real_transcription = "ðɪs ɪz ɐ tɛst mɛsɪdʒ"

    words_real = real_transcription.lower().split()
    words_estimated = transcription.split()

    mapped_words, mapped_words_indices = wm.get_best_mapped_words(
        words_estimated, words_real
    )
    print("[debug] mapped_words:", type(mapped_words))
    pprint.pp(mapped_words)
    
    print("[debug] words_real:", type(words_real))
    pprint.pp(words_real)
    
    # оценка правильности каждого символа в транскрибированных словах
    correct_letters = "".join(
        "".join(
            [
                str(is_correct)
                for is_correct in wm.getWhichLettersWereTranscribedCorrectly(
                    word_real, wm.get_best_mapped_words(
                        mapped_words[idx],
                        word_real
                    )[0]
                )
            ]
        )
        + " "
        for idx, word_real in enumerate(words_real)
    )

    accuracy = correct_letters.replace(" ", "").count("1") / len(
        correct_letters.replace(" ", "")
    )

    result = {
        "real_transcription": real_transcription,
        "transcription": transcription,
        "correct_letters": correct_letters,
        "accuracy": accuracy,
    }

    print(result)
