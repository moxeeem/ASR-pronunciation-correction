import pronunciation_api.get_sample
from pronunciation_api.transcribe import transcribe_audio_from_file
import numpy as np
import pronunciation_api.WordMatching as wm


# def transcribe_audio(audio_content: np.ndarray):
def get_current_text_transcription():
    current_text_transcription = api.get_sample.current_data.get("ipa_transcription", "N/A")  # "ðɪs ɪz ɐ tɛst mɛsɪdʒ"
    return current_text_transcription


def get_transcription_result(audio_content: np.ndarray):
    transcription = transcribe_audio_from_file(audio_content)
    real_transcription = get_current_text_transcription()

    words_real = real_transcription.lower().split()
    words_estimated = transcription.split()

    mapped_words, mapped_words_indices = wm.get_best_mapped_words(words_estimated, words_real)

    correct_letters = ''.join(
        ''.join([str(is_correct) for is_correct in wm.getWhichLettersWereTranscribedCorrectly(
            word_real, wm.get_best_mapped_words(mapped_words[idx], word_real)[0])]) + ' '
        for idx, word_real in enumerate(words_real)
    )

    accuracy = correct_letters.replace(" ", "").count('1') / len(correct_letters.replace(" ", ""))

    result = {
        'real_transcription': real_transcription,
        'transcription': transcription,
        'correct_letters': correct_letters,
        'accuracy': accuracy
    }

    return result



'''transcription = "ðɪs ɪz ʌɛst mɛsɪd͡ʒ"
real_transcription = "ðɪs ɪz ɐ tɛst mɛsɪdʒ"

words_real = real_transcription.lower().split()
words_estimated = transcription.split()

mapped_words, mapped_words_indices = wm.get_best_mapped_words(words_estimated, words_real)

# Оценка правильности каждого символа в транскрибированных словах
correct_letters = ''.join(
    ''.join([str(is_correct) for is_correct in wm.getWhichLettersWereTranscribedCorrectly(
        word_real, wm.get_best_mapped_words(mapped_words[idx], word_real)[0])]) + ' '
    for idx, word_real in enumerate(words_real)
)

accuracy = correct_letters.replace(" ", "").count('1') / len(correct_letters.replace(" ", ""))

result = {
    'real_transcription': real_transcription,
    'transcription': transcription,
    'correct_letters': correct_letters,
    'accuracy': accuracy
}

print(result)'''