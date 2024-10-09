import unittest
import epitran
import json

# project modules
import ModelInterfaces
import lambdaGetSample
import RuleBasedModels
import pronunciationTrainer as prTr


def test_category(category: int, threshold_min: int, threshold_max: int) -> bool:
    event = {
        "body": json.dumps({
            "category": category,
            "language": "de"
        })
    }

    for _ in range(1000):
        resp = lambdaGetSample.lambda_handler(event, [])
        resp_dict: dict[str, str] = json.loads(resp)
        number_of_words: int = len(resp_dict["real_transcript"][0].split())

        length_valid = (
            number_of_words > threshold_min
            and number_of_words <= threshold_max
        )

        if not length_valid:
            print(
                "Category ", category,
                " had a sentence with length ", number_of_words
            )
            return False
    return True


class TestDataset(unittest.TestCase):
    def test_random_sentences(self):
        self.assertFalse(test_category(0, 0, 8))

    def test_easy_sentences(self):
        self.assertTrue(test_category(1, 0, 8))

    def test_normal_sentences(self):
        self.assertTrue(test_category(2, 8, 20))

    def test_hard_sentences(self):
        self.assertTrue(test_category(3, 20, 10000))


def check_phoneme_converter(
    converter: ModelInterfaces.ITextToPhonemeModel,
    input: str,
    expected_output: str
) -> bool:
    output = converter.convertToPhoneme(input)
    is_correct = output == expected_output
    if not is_correct:
        print(
            'Conversion from "',
            input,
            '" should be "',
            expected_output,
            '", but was "',
            output,
            '"',
        )
    return is_correct


class TestPhonemeConverter(unittest.TestCase):
    def test_english(self):
        phoneme_converter = RuleBasedModels.EngPhonemeConverter()
        self.assertTrue(
            check_phoneme_converter(
                phoneme_converter,
                "Hello, this is a test",
                "hɛˈloʊ, ðɪs ɪz ə tɛst"
            )
        )

    def test_german(self):
        phoneme_converter = RuleBasedModels.EpitranPhonemeConverter(
            epitran.Epitran("deu-Latn")
        )
        self.assertTrue(
            check_phoneme_converter(
                phoneme_converter,
                "Hallo, das ist ein Test",
                "haloː, dɑːs ɪst ain tɛst"
            )
        )


trainer_SST_lambda: dict[str, prTr.PronunciationTrainer] = {}
trainer_SST_lambda["de"] = prTr.getTrainer("de")


class TestScore(unittest.TestCase):
    def test_exact_transcription(self):
        words_real = "Ich habe sehr viel glück, am leben und gesund zu sein"
        real_and_transcribed_words, _, _ = trainer_SST_lambda[
            "de"
        ].matchSampleAndRecordedWords(
            words_real,
            words_real
        )

        pronunciation_accuracy, _ = trainer_SST_lambda["de"].getPronunciationAccuracy(
            real_and_transcribed_words
        )
        self.assertTrue(int(pronunciation_accuracy) == 100)

    def test_incorrect_transcription(self):
        words_real          = "Ich habe sehr viel glück, am leben und gesund zu sein"
        words_transcribed   = "Ic hab zeh viel guck am und gesund tu sein"
        real_and_transcribed_words, _, _ = trainer_SST_lambda[
            "de"
        ].matchSampleAndRecordedWords(
            words_real,
            words_transcribed
        )

        pronunciation_accuracy, _ = trainer_SST_lambda["de"].getPronunciationAccuracy(
            real_and_transcribed_words
        )
        self.assertTrue(int(pronunciation_accuracy) == 71)


if __name__ == "__main__":
    unittest.main()
