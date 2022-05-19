from abc import ABC, abstractmethod
from typing import Any


class EntityRankingMethod:
    # Сходства строк
    STRING_SIMILARITY = "string similarity"
    # Сходства на основе NER-классов
    NER_BASED_SIMILARITY = "ner based similarity"
    # Сходство на основе заголовка
    HEADING_BASED_SIMILARITY = "heading based similarity"
    # Сходство на основе семантической близости сущностей кандидатов
    ENTITY_EMBEDDINGS_BASED_SIMILARITY = "entity embeddings based similarity"
    # Сходство на основе контекста
    CONTEXT_BASED_SIMILARITY = "context based similarity"
    # Агрегация оценок (рангов)
    SCORES_AGGREGATION = "scores aggregation"


class EntityRankingWeightFactor:
    STRING_SIMILARITY = 1  # Сходства строк
    NER_BASED_SIMILARITY = 1  # Сходства на основе NER-классов
    HEADING_BASED_SIMILARITY = 1  # Сходство на основе заголовка
    ENTITY_EMBEDDINGS_BASED_SIMILARITY = 1  # Сходство на основе семантической близости сущностей кандидатов
    CONTEXT_BASED_SIMILARITY = 1  # Сходство на основе контекста


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


class AbstractEntityModel(ABC):
    __slots__ = ()

    @abstractmethod
    def aggregate_scores(self) -> float:
        """
        Aggregate scores (ranks) across all metrics.
        """
        pass


class EntityModel(AbstractEntityModel, EntityRankingWeightFactor):
    __slots__ = ("_uri", "_label", "_comment", "_string_similarity", "_ner_based_similarity",
                 "_heading_based_similarity", "_entity_embeddings_based_similarity",
                 "_context_based_similarity", "_final_score")

    def __init__(self, uri: Any = None, label: str = None, comment: str = None, string_similarity: float = 0,
                 ner_based_similarity: float = 0, heading_based_similarity: float = 0,
                 entity_embeddings_based_similarity: float = 0, context_based_similarity: float = 0,
                 final_score: float = 0):
        self._uri = uri
        self._label = label
        self._comment = comment
        self._string_similarity = string_similarity
        self._ner_based_similarity = ner_based_similarity
        self._heading_based_similarity = heading_based_similarity
        self._entity_embeddings_based_similarity = entity_embeddings_based_similarity
        self._context_based_similarity = context_based_similarity
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
    def string_similarity(self):
        return self._string_similarity

    @property
    def ner_based_similarity(self):
        return self._ner_based_similarity

    @property
    def heading_based_similarity(self):
        return self._heading_based_similarity

    @property
    def entity_embeddings_based_similarity(self):
        return self._entity_embeddings_based_similarity

    @property
    def context_based_similarity(self):
        return self._context_based_similarity

    @property
    def final_score(self):
        return self._final_score

    def aggregate_scores(self):
        self._final_score = self.string_similarity * self.STRING_SIMILARITY + \
                            self.ner_based_similarity * self.NER_BASED_SIMILARITY + \
                            self.heading_based_similarity * self.HEADING_BASED_SIMILARITY + \
                            self.entity_embeddings_based_similarity * self.ENTITY_EMBEDDINGS_BASED_SIMILARITY + \
                            self.context_based_similarity * self.CONTEXT_BASED_SIMILARITY


class AbstractClassModel(ABC):
    __slots__ = ()

    @abstractmethod
    def aggregate_scores(self) -> float:
        """
        Aggregate scores (ranks) across all metrics.
        """
        pass


class ClassModel(AbstractClassModel, ClassRankingWeightFactor):
    __slots__ = ("_uri", "_label", "_comment", "_majority_voting_score", "_heading_similarity",
                 "_column_type_prediction_score", "_final_score")

    def __init__(self, uri: Any = None, label: str = None, comment: str = None, majority_voting_score: float = 0,
                 heading_similarity: float = 0, column_type_prediction_score: float = 0, final_score: float = 0):
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
        self._final_score = self.majority_voting_score * self.MAJORITY_VOTING + \
                            self.heading_similarity * self.HEADING_SIMILARITY + \
                            self.column_type_prediction_score * self.COLUMN_TYPE_PREDICTION
