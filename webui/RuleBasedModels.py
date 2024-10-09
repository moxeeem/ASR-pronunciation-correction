import ModelInterfaces
import epitran
import eng_to_ipa


class EpitranPhonemeConverter(ModelInterfaces.ITextToPhonemeModel):
    word_locations_in_samples = None
    audio_transcript = None

    def __init__(self, epitran_model: epitran.Epitran):
        self.epitran_model = epitran_model

    def convertToPhoneme(self, sentence: str) -> str:
        _phoneme_repr = self.epitran_model.transliterate(
            sentence
        )
        return _phoneme_repr


class EngPhonemeConverter(ModelInterfaces.ITextToPhonemeModel):
    def __init__(self):
        pass

    def convertToPhoneme(self, sentence: str) -> str:
        phoneme_repr = eng_to_ipa.convert(sentence)
        return phoneme_repr.replace("*", "")
