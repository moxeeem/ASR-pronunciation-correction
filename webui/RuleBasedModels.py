import ModelInterfaces
import eng_to_ipa


class EngPhonemeConverter(ModelInterfaces.ITextToPhonemeModel):
    def __init__(self):
        pass

    def convertToPhoneme(self, sentence: str) -> str:
        phoneme_repr = eng_to_ipa.convert(sentence)
        return phoneme_repr.replace("*", "")
