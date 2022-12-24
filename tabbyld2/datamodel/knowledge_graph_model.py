from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Tuple

from dbpedia_sparql_endpoint import get_objects_for_entity, get_subjects_for_entity


class EntityRankingMethod(str, Enum):
    STRING_SIMILARITY = "string similarity"
    NER_BASED_SIMILARITY = "ner based similarity"
    HEADING_BASED_SIMILARITY = "heading based similarity"
    ENTITY_EMBEDDINGS_BASED_SIMILARITY = "entity embeddings based similarity"
    CONTEXT_BASED_SIMILARITY = "context based similarity"
    SCORES_AGGREGATION = "scores aggregation"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class EntityRankingWeightFactor:
    STRING_SIMILARITY = 1
    NER_BASED_SIMILARITY = 1
    HEADING_BASED_SIMILARITY = 1
    ENTITY_EMBEDDINGS_BASED_SIMILARITY = 1
    CONTEXT_BASED_SIMILARITY = 1


class ClassRankingMethod(str, Enum):
    MAJORITY_VOTING = "majority voting"
    HEADING_SIMILARITY = "heading similarity"
    COLUMN_TYPE_PREDICTION = "column type prediction"
    NER_BASED_SIMILARITY = "NER based similarity"
    SCORES_AGGREGATION = "scores aggregation"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


class ClassRankingWeightFactor:
    MAJORITY_VOTING = 1
    HEADING_SIMILARITY = 1
    COLUMN_TYPE_PREDICTION = 1


class AbstractEntityModel(ABC):
    __slots__ = ()

    @abstractmethod
    def get_context(self) -> None:
        """
        Get context for an entity (subjects and objects from RDF triples that are associated with an entity)
        """
        pass

    @abstractmethod
    def aggregate_scores(self) -> float:
        """
        Aggregate scores (ranks) across all metrics
        """
        pass


class EntityModel(AbstractEntityModel, EntityRankingWeightFactor):
    __slots__ = ("_uri", "_label", "_comment", "_context", "_string_similarity", "_ner_based_similarity", "_heading_based_similarity",
                 "_entity_embeddings_based_similarity", "_context_based_similarity", "_final_score")

    def __init__(self, uri: str = None, label: str = None, comment: str = None, context: Tuple['EntityModel', ...] = None,
                 string_similarity: float = 0, ner_based_similarity: float = 0, heading_based_similarity: float = 0,
                 entity_embeddings_based_similarity: float = 0, context_based_similarity: float = 0, final_score: float = 0):
        self._uri = uri
        self._label = label
        self._comment = comment
        self._context = context
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
    def context(self):
        return self._context

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

    def get_context(self):
        context = {**get_subjects_for_entity(self.uri), **get_objects_for_entity(self.uri)}
        self._context = tuple([EntityModel(uri, label, comment) for uri, (label, comment) in context.items()])

    def aggregate_scores(self):
        self._final_score = self.string_similarity * self.STRING_SIMILARITY + self.ner_based_similarity * self.NER_BASED_SIMILARITY +  \
            self.heading_based_similarity * self.HEADING_BASED_SIMILARITY + self.entity_embeddings_based_similarity * \
            self.ENTITY_EMBEDDINGS_BASED_SIMILARITY + self.context_based_similarity * self.CONTEXT_BASED_SIMILARITY


class AbstractClassModel(ABC):
    __slots__ = ()

    @abstractmethod
    def aggregate_scores(self) -> float:
        """
        Aggregate scores (ranks) across all metrics
        """
        pass


class ClassModel(AbstractClassModel, ClassRankingWeightFactor):
    __slots__ = ("_uri", "_label", "_comment", "_majority_voting_score", "_heading_similarity",
                 "_column_type_prediction_score", "_ner_based_similarity", "_final_score")

    def __init__(self, uri: Any = None, label: str = None, comment: str = None, majority_voting_score: float = 0,
                 heading_similarity: float = 0, column_type_prediction_score: float = 0, ner_based_similarity: float = 0,
                 final_score: float = 0):
        self._uri = uri
        self._label = label
        self._comment = comment
        self._majority_voting_score = majority_voting_score
        self._heading_similarity = heading_similarity
        self._column_type_prediction_score = column_type_prediction_score
        self._ner_based_similarity = ner_based_similarity
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
    def ner_based_similarity(self):
        return self._ner_based_similarity

    @property
    def final_score(self):
        return self._final_score

    def aggregate_scores(self):
        self._final_score = self.majority_voting_score * self.MAJORITY_VOTING + self.heading_similarity * self.HEADING_SIMILARITY + \
            self.column_type_prediction_score * self.COLUMN_TYPE_PREDICTION
