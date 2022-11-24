import re
from enum import Enum

import stanza
import dateparser
from typing import Any
from abc import ABC, abstractmethod
from collections import defaultdict
from tabbyld2.helpers.utility import is_float
from tabbyld2.datamodel.tabular_data_model import TableModel


class NamedEntityLabel(str, Enum):
    PERSON = "PERSON"  # People, including fictional
    NORP = "NORP"  # Nationalities or religious or political groups
    FACILITY = "FACILITY"  # Buildings, airports, highways, bridges, etc.
    ORGANIZATION = "ORG"  # Companies, agencies, institutions, etc.
    GPE = "GPE"  # Countries, cities, states
    LOCATION = "LOC"  # Non-GPE locations, mountain ranges, bodies of water
    PRODUCT = "PRODUCT"  # Vehicles, weapons, foods, etc. (Not services)
    EVENT = "EVENT"  # Named hurricanes, battles, wars, sports events, etc.
    ART_WORK = "WORK OF ART"  # Titles of books, songs, etc.
    LAW = "LAW"  # Named documents made into laws
    NONE = "NONE"  # NER result is empty

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class LiteralLabel(str, Enum):
    # Literal types from OntoNotes package:
    HEXADECIMAL = "HEXADECIMAL"
    DATE = "DATE"  # Absolute or relative dates or periods
    TIME = "TIME"  # Times smaller than a day
    PERCENT = "PERCENT"  # Percentage (including "%")
    MONEY = "MONEY"  # Monetary values, including unit
    QUANTITY = "QUANTITY"  # Measurements, as of weight or distance
    ORDINAL = "ORDINAL"  # "first", "second", etc.
    CARDINAL = "CARDINAL"  # Numerals that do not fall under another type
    # Another literal types:
    POSITIVE_INTEGER = "POSITIVE INTEGER"  # Positive integer
    NEGATIVE_INTEGER = "NEGATIVE INTEGER"  # Negative integer
    FLOAT = "FLOAT"  # Float
    BOOLEAN = "BOOLEAN"  # true or false
    MAIL = "MAIL"  # Mail address
    EMAIL = "EMAIL"  # Email address
    ISSN = "ISSN"  # ISSN
    ISBN = "ISBN"  # ISBN
    IP_ADDRESS_V4 = "IP V4"  # IP address for 4 version
    BANK_CARD = "BANK CARD"  # Bank card number
    COORDINATES = "COORDINATES"  # Latitude and longitude coordinates
    PHONE = "PHONE"  # Phone number
    COLOR = "COLOR"  # Color number
    TEMPERATURE = "TEMPERATURE"  # Temperature degrees (celcius or fahrenheit)
    URL = "URL"  # URL address for site
    EMPTY = "EMPTY"  # Empty value
    SYMBOL = "SYMBOL"  # Some symbol
    ID = "ID" #Some ID

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class ColumnType(str, Enum):
    CATEGORICAL_COLUMN = "CATEGORICAL"  # Categorical column type
    LITERAL_COLUMN = "LITERAL"  # Literal column type
    SUBJECT_COLUMN = "SUBJECT"  # Subject column type


class AbstractAtomicColumnClassifier(ABC):
    __slots__ = ()

    @abstractmethod
    def recognize_named_entities(self) -> None:
        """
        Recognize named entities in table cells.
        """
        pass

    @abstractmethod
    def classify_columns(self) -> None:
        """
        Determine column types based on recognized named entities in table cells.
        """
        pass


class AtomicColumnClassifier(AbstractAtomicColumnClassifier):

    def __init__(self, table_model: TableModel = None):
        self._table_model = table_model

    @property
    def table_model(self):
        return self._table_model

    @staticmethod
    def determine_number(value: Any, label: str) -> str:
        """
        Determine number type based on input textual value.
        :param value: input textual value
        :param label: current label
        :return: new label
        """
        # If negative integer
        if re.search(r"^[-][1-9]\d*$", value):
            return LiteralLabel.NEGATIVE_INTEGER
        # If positive integer
        if re.search(r"^[1-9]\d*$", value):
            return LiteralLabel.POSITIVE_INTEGER
        # If float
        if is_float(value):
            return LiteralLabel.FLOAT
        return label

    @staticmethod
    def determine_entity_mention(entity_mention: str) -> str:
        """
        Correct entity mention (string) with the assignment of a specific label.
        :param entity_mention: text mention of an entity (a source text)
        :return: specific label
        """

        if entity_mention == "":
            return LiteralLabel.EMPTY
        else:
            if len(entity_mention) == 1 or len(entity_mention) == 2:
                return LiteralLabel.SYMBOL
            if dateparser.parse(entity_mention):
                return LiteralLabel.DATE
            if re.search(r"^'true|false|True|False|TRUE|FALSE'&", entity_mention):
                return LiteralLabel.BOOLEAN
            if re.search(r"^\d{6}$", entity_mention) or re.search(r"^\d{5}(?:[-\s]\d{4})?$", entity_mention):
                return LiteralLabel.MAIL
            if re.search(r"^[0-9]{4}-[0-9]{3}[0-9xX]$", entity_mention):
                return LiteralLabel.ISSN
            if re.search(r"^(?:ISBN(?:: ?| ))?((?:97[89])?\d{9}[\dx])+$", entity_mention):
                return LiteralLabel.ISBN
            if re.search(r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25["
                         r"0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                         entity_mention):
                return LiteralLabel.IP_ADDRESS_V4
            if re.search(r"^([456][0-9]{3})-?([0-9]{4})-?([0-9]{4})-?([0-9]{4})$", entity_mention):
                return LiteralLabel.BANK_CARD
            if re.search(r"#[0-9A-Fa-f]{6}", entity_mention):
                return LiteralLabel.COLOR
            if re.search(r"[\w.-]+@[\w.-]+\.?[\w]+?", entity_mention):
                return LiteralLabel.EMAIL
            if re.search(r"^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$", entity_mention):
                return LiteralLabel.COORDINATES
            if re.search(r"^((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{"
                         r"3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))$", entity_mention):
                return LiteralLabel.PHONE
            if re.search(r"([+-]?\d+(\.\d+)*)\s?°([CcFf])", entity_mention):
                return LiteralLabel.TEMPERATURE
            if re.search(r"((id|ID)[^a-zA-Z])|((([[:punct:]]id)|([[:punct:]]ID))^[^a-zA-Z])",entity_mention):
                return LiteralLabel.ID
            if re.search(r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,"
                         r"6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", entity_mention):
                return LiteralLabel.URL
            if re.search(r"(0x)?[A-Fa-f0-9]+",entity_mention):
                return LiteralLabel.HEXADECIMAL
        return NamedEntityLabel.NONE

    def recognize_named_entities(self) -> None:
        stanza.download("en")
        nlp = stanza.Pipeline(lang="en", processors="tokenize,ner")  # Neural pipeline preparation
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.cleared_value is not None:
                    doc = nlp(cell.cleared_value + ".")  # Named Entity Recognition
                    recognized_named_entities = [ent.type for ent in doc.ents] if len(doc.ents) > 1 else None
                    if len(doc.ents) == 1:
                        recognized_named_entities = doc.ents[0].type
                    if recognized_named_entities is None:
                        recognized_named_entities = self.determine_number(cell.cleared_value, NamedEntityLabel.NONE)
                    if recognized_named_entities == LiteralLabel.CARDINAL:
                        recognized_named_entities = self.determine_number(cell.cleared_value, LiteralLabel.CARDINAL)
                    if recognized_named_entities == NamedEntityLabel.NONE:
                        recognized_named_entities = self.determine_entity_mention(cell.cleared_value)
                    if determine_count_number(cell.cleared_value):
                        recognized_named_entities = LiteralLabel.SYMBOL
                    cell._label = recognized_named_entities
                else:
                    cell._label = LiteralLabel.EMPTY

    def classify_columns(self) -> None:
        # Counting categorical and literal cells
        categorical_number, literal_number, empty_number = defaultdict(int), defaultdict(int), 0
        for column in self.table_model.columns:
            for cell in column.cells:
                categorical_number[column.header_name] += 1 if NamedEntityLabel.has_value(cell.label) else 0
                literal_number[column.header_name] += 1 if LiteralLabel.has_value(cell.label) else 0
                empty_number += 1 if cell.label is LiteralLabel.EMPTY else 0
            if categorical_number[column.header_name] > 0 and literal_number[column.header_name] > 0:
                literal_number[column.header_name] -= empty_number
        # Determining atomic type for columns based on classified cells
        for column in self.table_model.columns:
            categorical, literal = categorical_number.get(column.header_name), literal_number.get(column.header_name)
            if categorical is not None and literal is not None:
                column.set_column_type(ColumnType.CATEGORICAL_COLUMN if categorical >= literal else ColumnType.LITERAL_COLUMN)


def test_ner(text):
    """
    Test recognition of named entities in a source text.
    :param text: a source text
    """
    stanza.download("en")
    nlp = stanza.Pipeline(lang="en", processors="tokenize,ner")
    doc = nlp(text)
    print(*[f"entity: {ent.text}\ttype: {ent.type}" for ent in doc.ents], sep="\n")



def determine_count_number(text):
    charText = list(text)
    countNumber = 0

    for i in charText:
        if i.isdigit():
            countNumber += 1
        else:
            countNumber += 0

    if countNumber > len(charText) / 2:
        return True
    else:
        return False
















