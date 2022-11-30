from abc import ABC, abstractmethod


class AbstractSemanticTableAnnotator(ABC):
    __slots__ = ()

    @abstractmethod
    def find_candidate_entities(self, only_subject_column: bool = False) -> None:
        """
        Find a set of candidate entities based on a textual entity mention
        :param only_subject_column: flag to include or exclude all columns from result
        """
        pass

    @abstractmethod
    def rank_candidate_entities_by_string_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column by using a string similarity
        :return:
        """
        pass

    @abstractmethod
    def rank_candidate_entities_by_ner_based_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column by using a NER based similarity
        """
        pass

    @abstractmethod
    def rank_candidate_entities_by_heading_based_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column by
        using a heading based similarity
        """
        pass

    @abstractmethod
    def rank_candidate_entities_by_entity_embeddings_based_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column by
        using an entity embeddings based similarity
        """
        pass

    @abstractmethod
    def rank_candidate_entities_by_context_based_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column by
        using a context based similarity
        """
        pass

    @abstractmethod
    def aggregate_ranked_candidate_entities(self) -> None:
        """
        Aggregate scores for candidate entities based on five heuristics
        """
        pass

    @abstractmethod
    def annotate_cells(self) -> None:
        """
        Annotate all cell values
        """
        pass

    @abstractmethod
    def rank_candidate_classes_by_majority_voting(self) -> None:
        """
        Rank candidate classes for categorical columns including a subject column by using a majority voting
        """
        pass

    @abstractmethod
    def rank_candidate_classes_by_heading_similarity(self) -> None:
        """
        Rank candidate classes for categorical columns including a subject column by using a heading similarity
        """
        pass

    @abstractmethod
    def rank_candidate_classes_by_column_type_prediction(self) -> None:
        """
        Rank candidate classes for categorical columns including a subject column by using a column type prediction.
        """
        pass

    @abstractmethod
    def aggregate_ranked_candidate_classes(self) -> None:
        """
        Aggregate scores for candidate classes based on three methods.
        """
        pass

    @abstractmethod
    def annotate_categorical_columns(self) -> None:
        """
        Annotate all categorical columns including a subject column.
        """
        pass

    @abstractmethod
    def annotate_literal_columns(self) -> None:
        """
        Annotate all literal columns based on recognized named entities (NER) in cells.
        """
        pass
