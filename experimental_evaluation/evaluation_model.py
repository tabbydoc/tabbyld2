from abc import ABC, abstractmethod
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


class BaseEvaluation(AbstractEvaluation):
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


class AbstractTableEvaluation(ABC):
    __slots__ = ()


class TableEvaluation(AbstractTableEvaluation):
    __slots__ = ("_table", "_column_classification_evaluation", "_subject_column_identification_evaluation",
                 "_cell_entity_annotation_evaluation", "_column_type_annotation_evaluation")

    def __init__(self, table: TableModel,
                 column_classification_evaluation: BaseEvaluation = None,
                 subject_column_identification_evaluation: BaseEvaluation = None,
                 cell_entity_annotation_evaluation: BaseEvaluation = None,
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
