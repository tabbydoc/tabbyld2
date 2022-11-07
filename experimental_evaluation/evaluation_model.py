from pandas import DataFrame, read_csv
from abc import ABC, abstractmethod

from tabbyld2.preprocessing.atomic_column_classifier import ColumnType
from tabbyld2.tabular_data_model import TableModel


class AbstractEvaluation(ABC):
    __slots__ = ()

    @abstractmethod
    def serialize_evaluation(self) -> dict:
        """
        Serialize table evaluation in the form of dict.
        :return: dict with table evaluation
        """
        pass


class MainEvaluation(AbstractEvaluation):
    __slots__ = ("_precision", "_recall", "_f1_score")

    def __init__(self, precision: float = None, recall: float = None, f1_score: float = None):
        self._precision = precision
        self._recall = recall
        self._f1_score = f1_score

    @property
    def precision(self):
        return self._precision

    @property
    def recall(self):
        return self._recall

    @property
    def f1_score(self):
        return self._f1_score

    def calculate_f1_score(self) -> None:
        """
        Calculate F1 score based on precision and recall.
        """
        if (self.precision is not None and self.precision != 0) or (self.recall is not None and self.recall != 0):
            self._f1_score = (2 * self.precision * self.recall) / (self.precision + self.recall)

    def serialize_evaluation(self) -> dict:
        return {"precision": self.precision, "recall": self.recall, "f1_score": self.f1_score}


class AdditionalEvaluation(AbstractEvaluation):
    __slots__ = ("_average_hierarchical_score", "_average_perfect_score")

    def __init__(self, average_hierarchical_score: float = None, average_perfect_score: float = None):
        self._average_hierarchical_score = average_hierarchical_score
        self._average_perfect_score = average_perfect_score

    @property
    def average_hierarchical_score(self):
        return self._average_hierarchical_score

    @property
    def average_perfect_score(self):
        return self._average_perfect_score

    def serialize_evaluation(self) -> dict:
        return {"average_hierarchical_score": self.average_hierarchical_score, "average_perfect_score": self.average_perfect_score}


class TableEvaluation:
    __slots__ = ("_table", "_column_classification_evaluation", "_subject_column_identification_evaluation",
                 "_cell_entity_annotation_evaluation", "_column_type_annotation_evaluation")

    def __init__(self, table: TableModel,
                 column_classification_evaluation: MainEvaluation = None,
                 subject_column_identification_evaluation: MainEvaluation = None,
                 cell_entity_annotation_evaluation: MainEvaluation = None,
                 column_type_annotation_evaluation: AdditionalEvaluation = None):
        self._table = table
        self._column_classification_evaluation = column_classification_evaluation
        self._subject_column_identification_evaluation = subject_column_identification_evaluation
        self._cell_entity_annotation_evaluation = cell_entity_annotation_evaluation
        self._column_type_annotation_evaluation = column_type_annotation_evaluation

    @property
    def table(self):
        return self._table

    @property
    def column_classification_evaluation(self):
        return self._column_classification_evaluation

    @property
    def subject_column_identification_evaluation(self):
        return self._subject_column_identification_evaluation

    @property
    def cell_entity_annotation_evaluation(self):
        return self._cell_entity_annotation_evaluation

    @property
    def column_type_annotation_evaluation(self):
        return self._column_type_annotation_evaluation

    def evaluate_columns_classification(self, evaluation_path: str):
        """
        Evaluate atomic classification of table columns (categorical or literal).
        """
        # Get number of classified columns
        classified_columns = sum(1 if column.column_type is not None else 0 for column in self.table.columns)
        # Get class checked data for tables from T2Dv2 dataset
        checked_data = DataFrame(read_csv(evaluation_path, sep=",", header=None, index_col=False))
        # Get number of correctly classified columns
        categorical_column_number, literal_column_number, rows = 0, 0, []
        for key, items in checked_data.items():
            if key == 0:
                for i in range(len(items)):
                    if items[i] == self.table.table_name:
                        rows.append(i)
                literal_column_number = len(self.table.columns) - len(rows)
            if key == 1:
                for i in range(len(items)):
                    for row_index in rows:
                        if i == row_index:
                            for k in range(len(self.table.columns)):
                                if k == int(items[i]):
                                    if self.table.columns[k].column_type == ColumnType.SUBJECT_COLUMN or \
                                            self.table.columns[k].column_type == ColumnType.CATEGORICAL_COLUMN:
                                        categorical_column_number += 1
        correctly_classified_columns = categorical_column_number + literal_column_number
        # Calculate evaluations
        self._column_classification_evaluation = MainEvaluation()
        self._column_classification_evaluation._precision = correctly_classified_columns / classified_columns if classified_columns != 0 else 0
        self._column_classification_evaluation._recall = correctly_classified_columns / len(self.table.columns) if len(self.table.columns) != 0 else 0
        self._column_classification_evaluation.calculate_f1_score()
