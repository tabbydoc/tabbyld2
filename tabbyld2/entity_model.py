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


class AbstractEntityModel(ABC):
    __slots__ = ()

    @abstractmethod
    def aggregate_scores(self) -> float:
        """
        Aggregate scores (ranks) across all metrics.
        """
        pass


class EntityModel(AbstractEntityModel):
    __slots__ = ("_uri", "_label", "_comment", "_string_similarity", "_ner_based_similarity",
                 "_heading_based_similarity", "_entity_embeddings_based_similarity",
                 "_context_based_similarity", "_final_score")

    def __init__(self, uri: Any = None, label: str = None, comment: str = None, string_similarity: float = None,
                 ner_based_similarity: float = None, heading_based_similarity: float = None,
                 entity_embeddings_based_similarity: float = None, context_based_similarity: float = None,
                 final_score: float = None):
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
        self._final_score = self.string_similarity * EntityRankingWeightFactor.STRING_SIMILARITY + \
                            self.ner_based_similarity * EntityRankingWeightFactor.NER_BASED_SIMILARITY + \
                            self.heading_based_similarity * EntityRankingWeightFactor.HEADING_BASED_SIMILARITY + \
                            self.entity_embeddings_based_similarity * \
                            EntityRankingWeightFactor.ENTITY_EMBEDDINGS_BASED_SIMILARITY + \
                            self.context_based_similarity * EntityRankingWeightFactor.CONTEXT_BASED_SIMILARITY
