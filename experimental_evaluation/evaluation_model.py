from abc import ABC, abstractmethod
from typing import Dict

from pandas import DataFrame, read_csv
from tabbyld2.datamodel.tabular_data_model import TableModel
from tabbyld2.preprocessing.atomic_column_classifier import ColumnType


class AbstractEvaluation(ABC):
    __slots__ = ()

    @abstractmethod
    def serialize_evaluation(self) -> Dict[str, float]:
        """
        Serialize table evaluation in the form of dict
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

    def set_precision(self, precision: float):
        self._precision = precision

    def set_recall(self, recall: float):
        self._recall = recall

    def calculate_f1_score(self):
        """
        Calculate F1 score based on precision and recall
        """
        if (self._precision is not None and self._precision != 0) or (self._recall is not None and self._recall != 0):
            self._f1_score = (2 * self._precision * self._recall) / (self._precision + self._recall)

    def serialize_evaluation(self) -> Dict[str, float]:
        return {"precision": self._precision, "recall": self._recall, "f1_score": self._f1_score}


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

    def set_average_hierarchical_score(self, average_hierarchical_score: float):
        self._average_hierarchical_score = average_hierarchical_score

    def set_average_perfect_score(self, average_perfect_score: float):
        self._average_perfect_score = average_perfect_score

    def serialize_evaluation(self) -> Dict[str, float]:
        return {"average_hierarchical_score": self._average_hierarchical_score, "average_perfect_score": self._average_perfect_score}


class TableEvaluation:
    __slots__ = ("_table", "_column_classification_evaluation", "_subject_column_identification_evaluation",
                 "_cell_entity_annotation_evaluation", "_column_type_annotation_evaluation")

    def __init__(self, table: TableModel, column_classification_evaluation: MainEvaluation = MainEvaluation(),
                 subject_column_identification_evaluation: MainEvaluation = MainEvaluation(),
                 cell_entity_annotation_evaluation: MainEvaluation = MainEvaluation(),
                 column_type_annotation_evaluation: AdditionalEvaluation = AdditionalEvaluation()):
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
        Evaluate atomic classification of table columns (categorical or literal)
        """
        # Get number of classified columns
        classified_columns = sum(1 if column.column_type is not None else 0 for column in self.table.columns)
        # Get class checked data for tables from T2Dv2 dataset
        checked_data = DataFrame(read_csv(evaluation_path, sep=",", header=None, index_col=False))
        # Get number of correctly classified columns
        categorical_column_number, literal_column_number = 0, 0
        for i in range(len(checked_data.get(0))):
            if checked_data.get(0)[i] == self.table.table_name:
                for j in range(len(self.table.columns)):
                    if j == int(checked_data.get(1)[i]) and (self.table.columns[j].column_type != ColumnType.LITERAL_COLUMN):
                        categorical_column_number += 1
        literal_column_number = len(self.table.columns) - categorical_column_number
        cor_cls_columns = categorical_column_number + literal_column_number
        self.column_classification_evaluation.set_precision(cor_cls_columns / classified_columns if classified_columns != 0 else 0)
        self.column_classification_evaluation.set_recall(cor_cls_columns / len(self.table.columns) if len(self.table.columns) != 0 else 0)
        self.column_classification_evaluation.calculate_f1_score()
