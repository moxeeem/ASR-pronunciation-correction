
from typing import Any
import torch
import numpy as np
import models as mo
import WordMetrics
import WordMatching as wm
import epitran
import ModelInterfaces as mi
import AIModels
import RuleBasedModels
from string import punctuation
import utils


def getTrainer(language: str) -> "PronunciationTrainer":
    model, decoder = mo.getASRModel(
        language,
        device=torch.device("cpu")
    )
    model.eval()
    asr_model = AIModels.NeuralASR(model, decoder)

    phoneme_converter: (
        RuleBasedModels.EpitranPhonemeConverter
        | RuleBasedModels.EngPhonemeConverter
    )
    
    if language == "de":
        phoneme_converter = RuleBasedModels.EpitranPhonemeConverter(
            epitran.Epitran("deu-Latn")
        )
    elif language == "en":
        phoneme_converter = RuleBasedModels.EngPhonemeConverter()
    else:
        raise ValueError("Language not implemented")

    trainer = PronunciationTrainer(
        asr_model,
        phoneme_converter
    )
    return trainer


class PronunciationTrainer:
    current_transcript: str
    current_ipa: str
    current_recorded_audio: torch.Tensor
    current_recorded_transcript: str
    current_recorded_word_locations: list
    current_recorded_intonations: torch.Tensor
    current_words_pronunciation_accuracy: list[str] = []
    categories_thresholds = np.array([80, 60, 59])

    sampling_rate = 16000

    def __init__(self,
        asr_model: mi.IASRModel,
        word_to_ipa_converter: mi.ITextToPhonemeModel
    ) -> None:
        self.asr_model = asr_model
        self.ipa_converter = word_to_ipa_converter

    def getTranscriptAndWordsLocations(self,
        audio_length_in_samples: int
    ) -> tuple[str, list[tuple[int, int]]]:

        audio_transcript: str = self.asr_model.getTranscript()
        word_locations_in_samples: list[dict[str, Any]] = self.asr_model.getWordLocations()        
        fade_duration_in_samples: float = 0.05 * self.sampling_rate
        
        word_locations_in_samples2 = [
            (
                int(np.maximum(0, word["start_ts"] - fade_duration_in_samples)),
                int(np.minimum(audio_length_in_samples - 1, word["end_ts"] + fade_duration_in_samples))
            ) for word in word_locations_in_samples
        ]

        return audio_transcript, word_locations_in_samples2

    def getWordsRelativeIntonation(self,
        Audio: torch.tensor,
        word_locations: list
    ):
        intonations = torch.zeros((len(word_locations), 1))
        intonation_fade_samples = 0.3 * self.sampling_rate
        
        print(intonations.shape)
        
        for word in range(len(word_locations)):
            intonation_start    = int(np.maximum(0, word_locations[word][0] - intonation_fade_samples))
            intonation_end      = int(np.minimum(Audio.shape[1] - 1, word_locations[word][1] + intonation_fade_samples))
            intonations[word]   = torch.sqrt(
                torch.mean(Audio[0][intonation_start:intonation_end] ** 2)
            )

        intonations = intonations/torch.mean(intonations)
        return intonations

    ##################### ASR Functions ###########################

    def processAudioForGivenText(self,
        recordedAudio: torch.Tensor,
        real_text: str
    ):
        with utils.catch_time("NN transcribing audio"):
            recording_transcript, recording_ipa, word_locations = self.getAudioTranscript(
                recordedAudio
            )
        
        print("[DEBUG] RECORDING TRANSCRIPT:",  type(recording_transcript), recording_transcript)
        print("[DEBUG] RECORDING IPA:",         type(recording_ipa),        recording_ipa)
        print("[DEBUG] WORD_LOCATIONS:",        type(word_locations),       word_locations)        

        with utils.catch_time("Matching transcripts:"):
            real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = self.matchSampleAndRecordedWords(
                real_text,
                recording_transcript
            )            
        
        start_time, end_time = self.getWordLocationsFromRecordInSeconds(
            word_locations,
            mapped_words_indices
        )

        pronunciation_accuracy, current_words_pronunciation_accuracy = self.getPronunciationAccuracy(
            real_and_transcribed_words
        )  # _ipa

        pronunciation_categories = self.getWordsPronunciationCategory(
            current_words_pronunciation_accuracy
        )

        result = {
            "recording_transcript": recording_transcript,
            "real_and_transcribed_words": real_and_transcribed_words,
            "recording_ipa": recording_ipa,
            "start_time": start_time,
            "end_time": end_time,
            "real_and_transcribed_words_ipa": real_and_transcribed_words_ipa,
            "pronunciation_accuracy": pronunciation_accuracy,
            "pronunciation_categories": pronunciation_categories
        }

        return result

    def getAudioTranscript(self, recordedAudio: torch.Tensor | None = None) -> tuple[str, str, list]:
        current_rec_audio = recordedAudio
        processed_recording = self.preprocessAudio(
            current_rec_audio
        )

        self.asr_model.processAudio(processed_recording)
        current_recorded_transcript, current_recorded_word_locations = self.getTranscriptAndWordsLocations(
            processed_recording.shape[1]
        )
        
        current_recorded_ipa = self.ipa_converter.convertToPhoneme(
            current_recorded_transcript
        )

        return current_recorded_transcript, current_recorded_ipa, current_recorded_word_locations

    def getWordLocationsFromRecordInSeconds(self, word_locations, mapped_words_indices) -> tuple[str, str]:
        start_time = []
        end_time = []
        for word_idx in range(len(mapped_words_indices)):
            start_time.append(
                float(word_locations[mapped_words_indices[word_idx]][0]) / self.sampling_rate
            )
            
            end_time.append(
                float(word_locations[mapped_words_indices[word_idx]][1]) / self.sampling_rate
            )
        
        start_timings: str  = " ".join([str(t) for t in start_time])
        end_timings: str    = " ".join([str(t) for t in end_time])
        
        return start_timings, end_timings
        
    ##################### END ASR Functions ###########################

    ##################### Evaluation Functions ###########################
    def matchSampleAndRecordedWords(self, real_text: str, recorded_transcript: str):
        words_estimated = recorded_transcript.split()

        if real_text is None:
            words_real = self.current_transcript[0].split()
        else:
            words_real = real_text.split()

        mapped_words, mapped_words_indices = wm.get_best_mapped_words(
            words_estimated,
            words_real
        )

        real_and_transcribed_words = []
        real_and_transcribed_words_ipa = []
        for word_idx in range(len(words_real)):
            if word_idx >= len(mapped_words)-1:
                mapped_words.append('-')
            
            real_and_transcribed_words.append(
                (
                    words_real[word_idx],
                    mapped_words[word_idx]
                )
            )
            real_and_transcribed_words_ipa.append(
                (
                    self.ipa_converter.convertToPhoneme(words_real[word_idx]),
                    self.ipa_converter.convertToPhoneme(mapped_words[word_idx])
                )
            )
        return real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices

    def getPronunciationAccuracy(self, real_and_transcribed_words_ipa) -> tuple[float, list[float]]:
        total_mismatches = 0.
        number_of_phonemes = 0.
        current_words_pronunciation_accuracy = []
        for pair in real_and_transcribed_words_ipa:

            real_without_punctuation = self.removePunctuation(pair[0]).lower()
            number_of_word_mismatches = WordMetrics.edit_distance_python(
                real_without_punctuation, self.removePunctuation(pair[1]).lower())
            total_mismatches += number_of_word_mismatches
            number_of_phonemes_in_word = len(real_without_punctuation)
            number_of_phonemes += number_of_phonemes_in_word

            current_words_pronunciation_accuracy.append(float(
                number_of_phonemes_in_word-number_of_word_mismatches)/number_of_phonemes_in_word*100)

        percentage_of_correct_pronunciations = (
            number_of_phonemes-total_mismatches)/number_of_phonemes*100

        return np.round(percentage_of_correct_pronunciations), current_words_pronunciation_accuracy

    def removePunctuation(self, word: str) -> str:
        return ''.join([char for char in word if char not in punctuation])

    def getWordsPronunciationCategory(self, accuracies) -> list:
        categories = []

        for accuracy in accuracies:
            categories.append(
                self.getPronunciationCategoryFromAccuracy(accuracy))

        return categories

    def getPronunciationCategoryFromAccuracy(self, accuracy) -> np.intp:
        return np.argmin(abs(self.categories_thresholds - accuracy))

    def preprocessAudio(self, audio: torch.Tensor) -> torch.Tensor:
        _audio = audio - torch.mean(audio)
        _audio_processed = _audio / torch.max(torch.abs(_audio))
        return _audio_processed
