from abc import ABC, abstractmethod
from typing import Any


class ClassRankingMethod:
    # Голосование большинством
    MAJORITY_VOTING = "majority voting"
    # Сходство заголовка
    HEADING_SIMILARITY = "heading similarity"
    # Прогнозирования класса
    COLUMN_TYPE_PREDICTION = "column type prediction"
    # Агрегация оценок (рангов)
    SCORES_AGGREGATION = "scores aggregation"


class ClassRankingWeightFactor:
    MAJORITY_VOTING = 1  # Голосование большинством
    HEADING_SIMILARITY = 1  # Сходство заголовка
    COLUMN_TYPE_PREDICTION = 1  # Прогнозирования класса


class AbstractClassModel(ABC):
    __slots__ = ()

    @abstractmethod
    def aggregate_scores(self) -> float:
        """
        Aggregate scores (ranks) across all metrics.
        """
        pass


class ClassModel(AbstractClassModel):
    __slots__ = ("_uri", "_label", "_comment", "_majority_voting_score", "_heading_similarity",
                 "_column_type_prediction_score", "_final_score")

    def __init__(self, uri: Any = None, label: str = None, comment: str = None, majority_voting_score: float = None,
                 heading_similarity: float = None, column_type_prediction_score: float = None,
                 final_score: float = None):
        self._uri = uri
        self._label = label
        self._comment = comment
        self._majority_voting_score = majority_voting_score
        self._heading_similarity = heading_similarity
        self._column_type_prediction_score = column_type_prediction_score
        self._final_score = final_score

    @property
    def uri(self):
        return self._uri

    @property
    def label(self):
        return self._label

    @property
    def comment(self):
        return self._comment

    @property
    def majority_voting_score(self):
        return self._majority_voting_score

    @property
    def heading_similarity(self):
        return self._heading_similarity

    @property
    def column_type_prediction_score(self):
        return self._column_type_prediction_score

    @property
    def final_score(self):
        return self._final_score

    def aggregate_scores(self):
        self._final_score = self.majority_voting_score * ClassRankingWeightFactor.MAJORITY_VOTING + \
                            self.heading_similarity * ClassRankingWeightFactor.HEADING_SIMILARITY + \
                            self.column_type_prediction_score * ClassRankingWeightFactor.COLUMN_TYPE_PREDICTION
