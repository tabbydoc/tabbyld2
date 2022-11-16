import collections
import re
from abc import ABC, abstractmethod
from math import sqrt

from tabbyld2.preprocessing.atomic_column_classifier import ColumnType
from tabbyld2.preprocessing.prepositions import Preposition
from tabbyld2.datamodel.tabular_data_model import TableModel


class WeightingFactor:
    UCF = 2
    AWN = 1
    ECF = 1
    CFA = 1
    HPN = 1


class AbstractSubjectColumnIdentifier(ABC):
    __slots__ = ()

    @abstractmethod
    def get_empty_cell_fraction(self, column_index: int = None) -> float:
        """
        Get a proportion of empty cells for current column from table.
        :param column_index: index of current column
        :return: proportion of blank cells for current column
        """
        pass

    @abstractmethod
    def get_cell_fraction_with_acronyms(self, column_index: int = None) -> float:
        """
        Get a proportion of cells with acronyms for current column from table.
        :param column_index: index of current column
        :return: proportion of cells with acronyms for current column
        """
        pass

    @abstractmethod
    def get_unique_content_cell_fraction(self, column_index: int = None) -> float:
        """
        Get a proportion of cells with unique content for current column from table.
        :param column_index: index of current column
        :return: proportion of cells with unique content for current column
        """
        pass

    @abstractmethod
    def get_distance_from_first_ne_column(self, column_index: int = None) -> int:
        """
        Get a distance from the first categorical column to current column.
        :param column_index: index of current column
        :return: distance from the first categorical column
        """
        pass

    @abstractmethod
    def get_average_word_number(self, column_index: int = None, threshold_factor: int = 0) -> float:
        """
        Get average number of words for current column.
        :param column_index: index of current column
        :param threshold_factor: threshold factor for cells that contains long text
        :return: average number of words
        """
        pass

    @abstractmethod
    def determine_prepositions_in_column_header_name(self, column_index: int = None) -> int:
        """
        Define preposition names in current column heading.
        :param column_index: index of current column
        :return: 1 if heading is a preposition, otherwise 0
        """
        pass

    @abstractmethod
    def identify_subject_column(self, column_index: int = None) -> None:
        """
        Define a subject (thematic) column among categorical ones based on heuristic estimates.
        :param column_index: explicit reference to a subject column index
        """
        pass


class SubjectColumnIdentifier(AbstractSubjectColumnIdentifier):

    def __init__(self, table_model: TableModel = None):
        self._table_model = table_model

    @property
    def table_model(self):
        return self._table_model

    def get_empty_cell_fraction(self, column_index: int = None) -> float:
        return sum(1 if not cell else 0 for cell in self.table_model.column(column_index)) / self.table_model.rows_number

    def get_cell_fraction_with_acronyms(self, column_index: int = None) -> float:
        cn = sum(1 if cell is not None and re.search(r"\b[A-ZА-Я.]{2,}\b", cell) else 0 for cell in self.table_model.column(column_index))
        return cn / self.table_model.rows_number

    def get_unique_content_cell_fraction(self, column_index: int = None) -> float:
        col = collections.Counter()
        for cell in self.table_model.column(column_index):
            col[cell] += 1
        return len(col) / self.table_model.rows_number

    def get_distance_from_first_ne_column(self, column_index: int = None) -> int:
        categorical_column_index = 0
        for column in self.table_model.columns:
            if column.column_type == ColumnType.CATEGORICAL_COLUMN:
                break
            categorical_column_index += 1
        return sum(1 if i < column_index else 0 for i in range(categorical_column_index, self.table_model.columns_number))

    def get_average_word_number(self, column_index: int = None, threshold_factor: int = 0) -> float:
        score = sum(len(cell.split()) if cell else 0 for cell in self.table_model.column(column_index)) / self.table_model.rows_number
        return score / threshold_factor if score <= threshold_factor else 0

    def determine_prepositions_in_column_header_name(self, column_index: int = None) -> int:
        column_number = 0
        for column in self.table_model.columns:
            if column_number == column_index and Preposition.has_value(column.header_name.lower()):
                return 1
            column_number += 1
        return 0

    def identify_subject_column(self, column_index: int = None):
        # If column index is explicitly specified, then this column is assigned to a subject column
        if column_index is not None and 0 <= column_index < self.table_model.columns_number:
            self.table_model.columns[column_index].set_column_type(ColumnType.SUBJECT_COLUMN)
            print("Subject column = " + self.table_model.columns[column_index].header_name)
        else:
            index, sub_col, final_score, score = 0, None, 0, 0
            for column in self.table_model.columns:
                if column.column_type == ColumnType.CATEGORICAL_COLUMN:
                    # Calculate heuristics
                    ucf = self.get_unique_content_cell_fraction(index)
                    awn = self.get_average_word_number(index, 10)
                    ecf = self.get_empty_cell_fraction(index)
                    cfa = self.get_cell_fraction_with_acronyms(index)
                    hpn = self.determine_prepositions_in_column_header_name(index)
                    dfc = self.get_distance_from_first_ne_column(index)
                    # Get penalty score
                    penalty_score = WeightingFactor.ECF * ecf + WeightingFactor.CFA * cfa + WeightingFactor.HPN * hpn
                    # Get total score
                    score = ((WeightingFactor.UCF * ucf + WeightingFactor.AWN * awn) - penalty_score) / sqrt(dfc + 1)
                    print("Score for '" + str(column.header_name) + "' (candidate subject column) = " + str(score))
                    if final_score < score:
                        final_score, sub_col = score, index
                index += 1
            if sub_col is not None:
                self.table_model.columns[sub_col].set_column_type(ColumnType.SUBJECT_COLUMN)
            else:
                print("A subject column not defined for current table!")
