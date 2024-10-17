from abc import ABC, abstractmethod
from typing import Any
import torch


class IASRModel(ABC):
    @abstractmethod
    def getTranscript(self) -> str:
        """
        Get the transcripts of processed audio
        """
        pass

    @abstractmethod
    def getWordLocations(self) -> list[dict[str, Any]]:
        """
        Get the pair of words locations from audio
        """
        pass

    @abstractmethod
    def processAudio(self, audio) -> None:
        """
        Process the audio
        """
        pass


class ITranslationModel(ABC):
    @abstractmethod
    def translateSentence(self, sentence: str) -> str:
        """
        Get the translation of specified sentence
        """
        pass


class ITextToSpeechModel(ABC):
    @abstractmethod
    def getAudioFromSentence(self, sentence: str) -> torch.Tensor:
        """
        Get the audio from specified sentence
        """
        pass


class ITextToPhonemeModel(ABC):
    @abstractmethod
    def convertToPhoneme(self, sentence: str) -> str:
        """
        Convert sentence to phonemes
        """
        pass
