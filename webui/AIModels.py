from typing import Any
import ModelInterfaces as mi
import torch
from transformers import (
    AutoModelForSeq2SeqLM,
    AutoTokenizer
)


class NeuralASR(mi.IASRModel):
    word_locations_in_samples = None
    audio_transcript = None

    def __init__(self,
        model: torch.nn.Module,
        decoder: torch.nn.Module
    ) -> None:
        self.model = model
        # Decoder from CTC-outputs to transcripts
        self.decoder = decoder

    def getTranscript(self) -> str:
        """
        Get the transcripts of the processed audio
        """
        if self.audio_transcript is None:
            raise RuntimeError(
                "Can get audio transcripts "
                "without having the audio processed"
            )
        return self.audio_transcript

    def getWordLocations(self) -> list[dict[str, Any]]:
        """
        Get the pair of words locations from the audio
        """
        if self.word_locations_in_samples is None:
            raise RuntimeError (
                "Can get word locations "
                "without having the audio processed"
            )
        return self.word_locations_in_samples

    def processAudio(self, audio: torch.Tensor):
        """
        Process the audio
        """
        audio_length_in_samples = audio.shape[1]
        with torch.inference_mode():
            nn_output: torch.Tensor = self.model(audio)
            self.audio_transcript, self.word_locations_in_samples = self.decoder(
                nn_output[0, :, :].detach(),
                audio_length_in_samples,
                word_align=True
            )


class NeuralTTS(mi.ITextToSpeechModel):
    def __init__(self,
        model: torch.nn.Module,
        sampling_rate: int
    ) -> None:
        self.model = model
        self.sampling_rate = sampling_rate

    def getAudioFromSentence(self, sentence: str) -> torch.Tensor:
        with torch.inference_mode():
            audio_transcript = self.model.apply_tts(
                texts=[sentence],
                sample_rate=self.sampling_rate
            )[0]

        return audio_transcript


class NeuralTranslator(mi.ITranslationModel):
    def __init__(self,
        model: AutoModelForSeq2SeqLM,
        tokenizer: AutoTokenizer
    ) -> None:
        self.model = model
        self.tokenizer = tokenizer

    def translateSentence(self, sentence: str) -> str:
        """
        Get the translation of specified sentence
        """
        tokenized_text = self.tokenizer(sentence, return_tensors="pt")
        translation = self.model.generate(**tokenized_text)
        translated_text = self.tokenizer.batch_decode(
            translation,
            skip_special_tokens=True
        )[0]
        
        return translated_text
