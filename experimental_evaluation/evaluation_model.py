from abc import ABC, abstractmethod
from typing import Tuple, Optional, Dict
from tabbyld2.tabular_data_model import TableModel


class AbstractTableEvaluationModel(ABC):
    __slots__ = ()

    @abstractmethod
    def calculate_f1_score(self) -> float:
        """
        Calculate F1 score based on precision and recall.
        """
        pass

    @abstractmethod
    def serialize_evaluation(self) -> dict:
        """
        Serialize table evaluation in the form of dict
        :return: table evaluation dict
        """
        pass


class TableEvaluationModel(AbstractTableEvaluationModel):
    __slots__ = ("_table", "_precision", "_recall", "_f1_score")

    def __init__(self, table: TableModel = None, precision: float = None, recall: float = None, f1_score: float = None):
        self._table = table
        self._precision = precision
        self._recall = recall
        self._f1_score = f1_score

    @property
    def table(self):
        return self._table

    @property
    def precision(self):
        return self._precision

    @property
    def recall(self):
        return self._recall

    @property
    def f1_score(self):
        return self._f1_score

    def calculate_f1_score(self):
        if (self.precision is not None and self.precision != 0) or (self.recall is not None and self.recall != 0):
            self._f1_score = (2 * self.precision * self.recall) / (self.precision + self.recall)

    def serialize_evaluation(self):
        serialized_evaluation = dict()
        serialized_evaluation["precision"] = self.precision
        serialized_evaluation["recall"] = self.recall
        serialized_evaluation["f1"] = self.f1_score

        return serialized_evaluation


class AbstractColumnsClassificationEvaluationModel(ABC):
    @abstractmethod
    def evaluate_columns_classification(self, checked_data: Optional[Dict]):
        """
        Evaluate classification of table columns.
        :param checked_data: checked data
        """
        pass


class AbstractSubjectColumnIdentificationEvaluationModel(ABC):
    @abstractmethod
    def evaluate_subject_column_identification(self, checked_data: Optional[Dict]):
        """
        Evaluate identification of subject column among categorical columns.
        :param checked_data: checked data
        """
        pass


class AbstractCellEntityAnnotationEvaluationModel(ABC):
    @abstractmethod
    def evaluate_cell_entity_annotation(self):
        """
        Evaluate cell entity annotation (CEA task).
        """
        pass


class AbstractColumnTypeAnnotationEvaluationModel(ABC):
    @abstractmethod
    def evaluate_column_type_annotation(self, checked_data: Optional[Dict]):
        """
        Evaluate column type annotation (CTA task).
        :param checked_data: checked data
        """
        pass


class AbstractColumnsPropertyAnnotationEvaluationModel(ABC):
    @abstractmethod
    def evaluate_columns_property_annotation(self, checked_data: Optional[Dict]):
        """
        Evaluate columns property annotation (CPA task).
        :param checked_data: checked data
        """
        pass


class AbstractDatasetEvaluationModel(ABC):
    __slots__ = ()

    @abstractmethod
    def calculate_precision(self) -> float:
        """
        Calculate precision for dataset.
        """
        pass

    @abstractmethod
    def calculate_recall(self) -> float:
        """
        Calculate recall for dataset.
        """
        pass

    @abstractmethod
    def calculate_f1_score(self) -> float:
        """
        Calculate F1 score for dataset based on precision and recall.
        """
        pass

    @abstractmethod
    def serialize_evaluation(self) -> dict:
        """
        Serialize all evaluation for dataset in the form of dict
        :return: dataset evaluation dict
        """
        pass


class DatasetEvaluationModel(AbstractDatasetEvaluationModel):
    __slots__ = ("_table_evaluations", "_precision", "_recall", "_f1_score")

    def __init__(self, table_evaluations: Tuple[TableEvaluationModel, ...] = None, precision: float = None,
                 recall: float = None, f1_score: float = None):
        self._table_evaluations = table_evaluations
        self._precision = precision
        self._recall = recall
        self._f1_score = f1_score

    @property
    def table_evaluations(self):
        return self._table_evaluations

    @property
    def precision(self):
        return self._precision

    @property
    def recall(self):
        return self._recall

    @property
    def f1_score(self):
        return self._f1_score

    def calculate_precision(self):
        if self.table_evaluations is not None:
            precision = 0
            for table_evaluation in self.table_evaluations:
                if table_evaluation.precision is not None:
                    precision += table_evaluation.precision
            self._precision = precision / len(self.table_evaluations)

    def calculate_recall(self):
        if self.table_evaluations is not None:
            recall = 0
            for table_evaluation in self.table_evaluations:
                if table_evaluation.recall is not None:
                    recall += table_evaluation.recall
            self._recall = recall / len(self.table_evaluations)

    def calculate_f1_score(self):
        if (self.precision is not None and self.precision != 0) or (self.recall is not None and self.recall != 0):
            self._f1_score = (2 * self.precision * self.recall) / (self.precision + self.recall)

    def serialize_evaluation(self):
        serialized_evaluation = dict()
        serialized_evaluation["precision"] = self.precision
        serialized_evaluation["recall"] = self.recall
        serialized_evaluation["f1"] = self.f1_score

        return serialized_evaluation
