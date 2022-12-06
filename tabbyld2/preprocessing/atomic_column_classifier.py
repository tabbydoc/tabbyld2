import re
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Enum
from typing import Dict, Tuple, Union

import dateparser
from duckling import Dim, DucklingWrapper
from stanza import Pipeline
from tabbyld2.datamodel.tabular_data_model import TableModel
from tabbyld2.helpers.utility import is_float
from tabbyld2.preprocessing.labels import LiteralLabel, NamedEntityLabel


class ColumnType(str, Enum):
    CATEGORICAL_COLUMN = "CATEGORICAL"  # Categorical column type
    LITERAL_COLUMN = "LITERAL"  # Literal column type
    SUBJECT_COLUMN = "SUBJECT"  # Subject column type


class AbstractAtomicColumnClassifier(ABC):
    __slots__ = ()

    @abstractmethod
    def _recognize_named_entities(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        """
        Recognize named entities in table cells and count categorical and literal cells
        """
        pass

    @abstractmethod
    def classify_columns(self) -> None:
        """
        Determine column types based on recognized named entities in table cells.
        """
        pass


class AtomicColumnClassifier(AbstractAtomicColumnClassifier):
    __slots__ = ("_named_entity_recognition", "_duckling_wrapper", "_table_model")

    def __init__(self, table_model: TableModel, named_entity_recognition: Pipeline, duckling_wrapper: DucklingWrapper):
        self._table_model = table_model
        self._named_entity_recognition = named_entity_recognition
        self._duckling_wrapper = duckling_wrapper

    @property
    def table_model(self):
        return self._table_model

    @property
    def named_entity_recognition(self):
        return self._named_entity_recognition

    @property
    def duckling_wrapper(self):
        return self._duckling_wrapper

    @staticmethod
    def _determine_number(text: str) -> Union[LiteralLabel, NamedEntityLabel]:
        """
        Determine a number type in an input textual value
        :param text: an input textual value
        :return: a new literal label for a cell value
        """
        # If negative integer
        if re.search(r"^-[1-9]\d*$", text):
            return LiteralLabel.NEGATIVE_INTEGER
        # If positive integer
        if re.search(r"^[1-9]\d*$", text):
            return LiteralLabel.POSITIVE_INTEGER
        # If float
        if is_float(text):
            return LiteralLabel.FLOAT
        return NamedEntityLabel.NONE

    @staticmethod
    def _determine_complex_numerical_values(text: str) -> Union[LiteralLabel, NamedEntityLabel]:
        """
        Determine complex numerical values in an input textual value
        :param text: an input textual value
        :return: a new literal label for a cell value
        """
        if re.search(r"^[0-9]{4}-[0-9]{3}[0-9xX]$", text):
            return LiteralLabel.ISSN
        if re.search(r"^(?:ISBN(?:: ?| ))?((?:97[89])?\d{9}[\dx])+$", text):
            return LiteralLabel.ISBN
        if re.search(r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9]["
                     r"0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$", text):
            return LiteralLabel.IP_ADDRESS_V4
        if re.search(r"^([456][0-9]{3})-?([0-9]{4})-?([0-9]{4})-?([0-9]{4})$", text):
            return LiteralLabel.BANK_CARD
        if re.search(r"#[0-9A-Fa-f]{6}", text):
            return LiteralLabel.COLOR
        if re.search(r"^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$", text):
            return LiteralLabel.COORDINATES
        if re.search(r"^((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}["
                     r"-\.\s]??\d{4}))$", text):
            return LiteralLabel.PHONE
        if re.search(r"([+-]?\d+(\.\d+)*)\s?°([CcFf])", text):
            return LiteralLabel.TEMPERATURE
        if re.search(r"^(0x)?[a-fA-F0-9]+$", text):
            return LiteralLabel.HEXADECIMAL
        return NamedEntityLabel.NONE

    @staticmethod
    def _determine_time(text: str, duckling_wrapper: DucklingWrapper) -> Union[LiteralLabel, NamedEntityLabel]:
        """
        Determine time label in a source text based on the Duckling library
        :param text: an input textual value
        :param duckling_wrapper: a DucklingWrapper object
        :return: a time label for cell value
        """
        dim_list = duckling_wrapper.parse(text, reference_time="1")
        if dim_list is not None:
            for item in dim_list:
                if item["text"] == text and item["dim"] == Dim.TIME:
                    return LiteralLabel.TIME
        return NamedEntityLabel.NONE

    @staticmethod
    def _determine_date(text: str) -> Union[LiteralLabel, NamedEntityLabel]:
        """
        Determine date label in a source text based on the DateParser library
        :param text: an input textual value
        :return: a date label for cell value
        """
        if dateparser.parse(text):
            return LiteralLabel.DATE
        return NamedEntityLabel.NONE

    @staticmethod
    def _determine_entity_mention(text: str) -> Union[LiteralLabel, NamedEntityLabel]:
        """
        Correct an entity mention (a source text) with the assignment of a specific literal label
        :param text: an input textual value
        :return: a new literal label for cell value
        """
        if re.search(r"^'true|false|True|False|TRUE|FALSE'&", text):
            return LiteralLabel.BOOLEAN
        if re.search(r"^\d{6}$", text) or re.search(r"^\d{5}(?:[-\s]\d{4})?$", text):
            return LiteralLabel.MAIL
        if re.search(r"[\w.-]+@[\w.-]+\.?[\w]+?", text):
            return LiteralLabel.EMAIL
        if re.search(r"((id|ID)[^a-zA-Z])|((([[:punct:]]id)|([[:punct:]]ID))^[^a-zA-Z])", text):
            return LiteralLabel.ID
        if re.search(r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*", text):
            return LiteralLabel.URL
        return NamedEntityLabel.NONE

    @staticmethod
    def _determine_symbol(text: str) -> Union[LiteralLabel, NamedEntityLabel]:
        """
        Determine symbol label in a source text based on number of letters in source cell value (must be less than half) and text length
        :param text: an input textual value
        :return: a new literal label for cell value
        """
        # If letters in text are less than half
        if sum(True for i in list(text) if i.isalpha()) < len(list(text)) / 2:
            return LiteralLabel.SYMBOL
        # If text length is 1 or 2
        if len(text) == 1 or len(text) == 2:
            return LiteralLabel.SYMBOL
        return NamedEntityLabel.NONE

    def _recognize_named_entities(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        categorical_number, literal_number, empty_number = defaultdict(int), defaultdict(int), 0
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.cleared_value is not None:
                    # Named Entity Recognition
                    doc = self.named_entity_recognition(cell.cleared_value.lower().title() + ".")
                    recognized_named_entities = [ent.type for ent in doc.ents] if len(doc.ents) > 1 else NamedEntityLabel.NONE
                    if len(doc.ents) == 1:
                        recognized_named_entities = doc.ents[0].type
                    # Custom recognition
                    if recognized_named_entities == NamedEntityLabel.NONE or recognized_named_entities == LiteralLabel.CARDINAL:
                        recognized_named_entities = self._determine_number(cell.cleared_value)
                    if recognized_named_entities == NamedEntityLabel.NONE or recognized_named_entities == LiteralLabel.CARDINAL:
                        recognized_named_entities = self._determine_time(cell.cleared_value, self.duckling_wrapper)
                    if recognized_named_entities == NamedEntityLabel.NONE or recognized_named_entities == LiteralLabel.CARDINAL:
                        recognized_named_entities = self._determine_date(cell.cleared_value)
                    if recognized_named_entities == NamedEntityLabel.NONE or recognized_named_entities == LiteralLabel.CARDINAL:
                        recognized_named_entities = self._determine_entity_mention(cell.cleared_value)
                    if recognized_named_entities == NamedEntityLabel.NONE or recognized_named_entities == LiteralLabel.CARDINAL:
                        recognized_named_entities = self._determine_symbol(cell.cleared_value)
                    cell.set_label(recognized_named_entities if recognized_named_entities is not None else NamedEntityLabel.NONE)
                else:
                    cell.set_label(LiteralLabel.EMPTY)
                # Counting categorical and literal cells
                if isinstance(cell.label, list):
                    for label in cell.label:
                        categorical_number[column.header_name] += 1 if NamedEntityLabel.has_value(label) else 0
                        literal_number[column.header_name] += 1 if LiteralLabel.has_value(label) else 0
                        empty_number += 1 if label is LiteralLabel.EMPTY else 0
                else:
                    categorical_number[column.header_name] += 1 if NamedEntityLabel.has_value(cell.label) else 0
                    literal_number[column.header_name] += 1 if LiteralLabel.has_value(cell.label) else 0
                    empty_number += 1 if cell.label is LiteralLabel.EMPTY else 0
            if categorical_number[column.header_name] > 0 and literal_number[column.header_name] > 0:
                literal_number[column.header_name] -= empty_number
        return categorical_number, literal_number

    def classify_columns(self) -> None:
        categorical_number, literal_number = self._recognize_named_entities()  # Recognize named entities for table cells
        # Determine an atomic type for columns based on classified cells
        for column in self.table_model.columns:
            categorical, literal = categorical_number.get(column.header_name), literal_number.get(column.header_name)
            if categorical is not None and literal is not None:
                column.set_column_type(ColumnType.CATEGORICAL_COLUMN if categorical >= literal else ColumnType.LITERAL_COLUMN)
