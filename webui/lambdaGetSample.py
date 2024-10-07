import pandas as pd
import json
import RuleBasedModels
import epitran
import random
import pickle
from typing import Dict, Any


class TextDataset:
    """
    Класс для хранения текстового набора данных и работы с ним.

    Атрибуты:
        table_dataframe (pd.DataFrame): Датафрейм с данными.
        number_of_samples (int): Количество образцов в таблице.
        language (str): Язык текстов, используемый для выборки строк.
    """

    def __init__(self, table: pd.DataFrame, language: str = '-') -> None:
        self.table_dataframe = table
        self.number_of_samples = len(table)
        self.language = language

    def __getitem__(self, idx: int) -> list:
        """
        Возвращает строку в зависимости от указанного языка.

        Аргументы:
            idx (int): Индекс строки.

        Возвращает:
            list: Список, содержащий предложение на выбранном языке.
        """
        if self.language == 'de':
            line = [self.table_dataframe['de_sentence'].iloc[idx]]
        elif self.language == 'en':
            line = [self.table_dataframe['en_sentence'].iloc[idx]]
        else:
            line = [self.table_dataframe['sentence'].iloc[idx]]
        return line

    def __len__(self) -> int:
        """
        Возвращает количество образцов в наборе данных.

        Возвращает:
            int: Количество образцов.
        """
        return self.number_of_samples


# Инициализация глобальных переменных
sample_folder = "./"
lambda_database: Dict[str, TextDataset] = {}
lambda_ipa_converter: Dict[str, Any] = {}

with open(sample_folder + 'data_de_en_2.pickle', 'rb') as handle:
    df = pickle.load(handle)

lambda_database['en'] = TextDataset(df, 'en')
lambda_translate_new_sample = False

lambda_ipa_converter['en'] = RuleBasedModels.EngPhonemConverter()


def lambda_handler(event: Dict[str, Any], context: Any) -> str:
    """
    AWS Lambda хэндлер для обработки входящих событий и генерации результата.

    Аргументы:
        event (dict): Входящее событие с данными.
        context (Any): Контекст исполнения Lambda.

    Возвращает:
        str: JSON-строка с реальным транскриптом, IPA-транскриптом и переводом.
    """
    body = json.loads(event['body'])
    category = int(body['category'])
    language = body['language']

    sample_in_category = False

    while not sample_in_category:
        valid_sequence = False
        while not valid_sequence:
            try:
                sample_idx = random.randint(0, len(lambda_database[language]) - 1)
                current_transcript = lambda_database[language][sample_idx]
                valid_sequence = True
            except:
                pass

        sentence_category = getSentenceCategory(current_transcript[0])
        sample_in_category = (sentence_category == category) or category == 0

    translated_transcript = ""

    current_ipa = lambda_ipa_converter[language].convertToPhonem(current_transcript[0])

    result = {
        'real_transcript': current_transcript,
        'ipa_transcript': current_ipa,
        'transcript_translation': translated_transcript
    }

    return json.dumps(result)


def getSentenceCategory(sentence: str) -> int:
    """
    Определяет категорию предложения на основе количества слов.

    Аргументы:
        sentence (str): Предложение для анализа.

    Возвращает:
        int: Категория предложения.
    """
    number_of_words = len(sentence.split())
    categories_word_limits = [0, 8, 20, 100000]

    for category in range(len(categories_word_limits) - 1):
        if categories_word_limits[category] < number_of_words <= categories_word_limits[category + 1]:
            return category + 1
