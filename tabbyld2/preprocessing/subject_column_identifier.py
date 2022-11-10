import collections
import operator
import re
from abc import ABC, abstractmethod
from math import sqrt

from atomic_column_classifier import ColumnType
from tabbyld2.preprocessing.prepositions import Preposition
from tabbyld2.datamodel.tabular_data_model import TableModel
from tabbyld2.helpers.utility import is_int


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

    def define_subject_column(self, column_index: int = None):
        """
        Определение сущностного (тематического) столбца на основе эвристических оценок.
        :param column_index: явное указание на номер сущностного (тематического) столбца
        """
        # If column index is explicitly specified, then this column is assigned to a subject column
        if is_int(str(column_index)) and 0 <= column_index < self.table_model.columns_number:
            i = 0
            for column in self.table_model.columns:
                if column_index == i:
                    column._column_type = ColumnType.SUBJECT_COLUMN
                i += 1
        else:
            column_index, sub_col = 0, {}
            for column in self.table_model.columns:
                if column.column_type == ColumnType.CATEGORICAL_COLUMN:
                    # Calculate heuristics
                    ucf = self.get_unique_content_cell_fraction(column_index)
                    awn = self.get_average_word_number(column_index, 10)
                    ecf = self.get_empty_cell_fraction(column_index)
                    cfa = self.get_cell_fraction_with_acronyms(column_index)
                    hpn = self.determine_prepositions_in_column_header_name(column_index)
                    dfc = self.get_distance_from_first_ne_column(column_index)
                    # Get penalty score
                    penalty_score = WeightingFactor.ECF * ecf + WeightingFactor.CFA * cfa + WeightingFactor.HPN * hpn
                    # Get total score
                    sub_col[column.header_name] = ((WeightingFactor.UCF * ucf + WeightingFactor.AWN * awn) - penalty_score) / sqrt(dfc + 1)
                    print("Total score for '" + str(column.header_name) + "' (candidate subject column) = " +
                          str(sub_col[column.header_name]))
                column_index += 1
            # Define current column with highest score as subject column
            for column in self.table_model.columns:
                if column.header_name == max(sub_col.items(), key=operator.itemgetter(1))[0]:
                    column._column_type = ColumnType.SUBJECT_COLUMN
