import unittest
import json

import ModelInterfaces
import lambdaGetSample
import RuleBasedModels


def test_category(category: int, threshold_min: int, threshold_max: int) -> bool:
    event = {
        "body": json.dumps({
            "category": category,
            "language": "en"
        })
    }

    for _ in range(1000):
        resp = lambdaGetSample.lambda_handler(event, [])
        resp_dict: dict[str, str] = json.loads(resp)
        number_of_words: int = len(resp_dict["real_transcript"][0].split())

        length_valid = (
                threshold_min < number_of_words <= threshold_max
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

if __name__ == "__main__":
    unittest.main()
