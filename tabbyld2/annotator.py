import os
from abc import ABC, abstractmethod
from collections import Counter
from typing import Tuple

# from Levenshtein._levenshtein import distance
# from pyrdf2vec.graphs import KG
# from pyrdf2vec import RDF2VecTransformer
# from pyrdf2vec.embedders import Word2Vec
# from pyrdf2vec.walkers import RandomWalker
# from gensim.models.word2vec import Word2Vec as W2V
import tabbyld2.dbpedia_lookup as dbl
import tabbyld2.dbpedia_sparql_endpoint as dbs
from tabbyld2.tabular_data_model import TableModel
from tabbyld2.knowledge_graph_model import EntityModel, ClassModel
from tabbyld2.column_classifier import ColumnType, NamedEntityLabel, LiteralLabel


class OntologyClass:
    PARK = "dbo:Park"
    MINE = "dbo:Mine"
    GARDEN = "dbo:Garden"
    CEMETERY = "dbo:Cemetery"
    WINE_REGION = "dbo:WineRegion"
    NATURAL_PLACE = "dbo:NaturalPlace"
    PROTECTED_AREA = "dbo:ProtectedArea"
    WORLD_HERITAGE_SITE = "dbo:WorldHeritageSite"
    SITE_OF_SPECIAL_SCIENTIFIC_INTEREST = "dbo:SiteOfSpecialScientificInterest"
    POPULATED_PLACE = "dbo:PopulatedPlace"
    ETHNIC_GROUP = "dbo:EthnicGroup"
    PERSON = "dbo:Person"
    DEVICE = "dbo:Device"
    FOOD = "dbo:Food"
    MEAN_OF_TRANSPORTATION = "dbo:MeanOfTransportation"
    ARCHITECTURAL_STRUCTURE = "dbo:ArchitecturalStructure"
    ORGANISATION = "dbo:Organisation"
    EVENT = "dbo:Event"
    WORK = "dbo:Work"
    LAW = "dbo:Law"
    LEGAL_CASE = "dbo:LegalCase"


CLASS_MAPPING = {
    NamedEntityLabel.LOCATION: [OntologyClass.PARK, OntologyClass.MINE, OntologyClass.GARDEN, OntologyClass.WINE_REGION,
                                OntologyClass.NATURAL_PLACE, OntologyClass.PROTECTED_AREA, OntologyClass.WORLD_HERITAGE_SITE,
                                OntologyClass.SITE_OF_SPECIAL_SCIENTIFIC_INTEREST],
    NamedEntityLabel.GPE: OntologyClass.POPULATED_PLACE,
    NamedEntityLabel.NORP: OntologyClass.ETHNIC_GROUP,
    NamedEntityLabel.PERSON: OntologyClass.PERSON,
    NamedEntityLabel.PRODUCT: [OntologyClass.DEVICE, OntologyClass.FOOD, OntologyClass.MEAN_OF_TRANSPORTATION],
    NamedEntityLabel.FACILITY: OntologyClass.ARCHITECTURAL_STRUCTURE,
    NamedEntityLabel.ORGANIZATION: OntologyClass.ORGANISATION,
    NamedEntityLabel.EVENT: OntologyClass.EVENT,
    NamedEntityLabel.ART_WORK: OntologyClass.WORK,
    NamedEntityLabel.LAW: [OntologyClass.LAW, OntologyClass.LEGAL_CASE]
}


class XMLSchemaDataType:
    DATE = "xsd:date"
    TIME = "xsd:time"
    NON_NEGATIVE_INTEGER = "xsd:nonNegativeInteger"
    POSITIVE_INTEGER = "xsd:positiveInteger"
    NEGATIVE_INTEGER = "xsd:negativeInteger"
    DECIMAL = "xsd:decimal"
    FLOAT = "xsd:float"
    BOOLEAN = "xsd:boolean"
    STRING = "xsd:string"
    URL = "xsd:anyURI"


DATATYPE_MAPPING = {
    LiteralLabel.DATE: XMLSchemaDataType.DATE,
    LiteralLabel.TIME: XMLSchemaDataType.TIME,
    LiteralLabel.PERCENT: XMLSchemaDataType.NON_NEGATIVE_INTEGER,
    LiteralLabel.MONEY: XMLSchemaDataType.NON_NEGATIVE_INTEGER,
    LiteralLabel.QUANTITY: XMLSchemaDataType.NON_NEGATIVE_INTEGER,
    LiteralLabel.POSITIVE_INTEGER: XMLSchemaDataType.NON_NEGATIVE_INTEGER,
    LiteralLabel.ORDINAL: XMLSchemaDataType.POSITIVE_INTEGER,
    LiteralLabel.CARDINAL: XMLSchemaDataType.DECIMAL,
    LiteralLabel.MAIL: XMLSchemaDataType.DECIMAL,
    LiteralLabel.BANK_CARD: XMLSchemaDataType.DECIMAL,
    LiteralLabel.PHONE: XMLSchemaDataType.DECIMAL,
    LiteralLabel.NEGATIVE_INTEGER: XMLSchemaDataType.NEGATIVE_INTEGER,
    LiteralLabel.FLOAT: XMLSchemaDataType.FLOAT,
    LiteralLabel.BOOLEAN: XMLSchemaDataType.BOOLEAN,
    LiteralLabel.URL: XMLSchemaDataType.URL
}


class AbstractSemanticTableAnnotator(ABC):
    __slots__ = ()

    @abstractmethod
    def find_candidate_entities(self, only_subject_column: bool = False) -> None:
        """
        Find a set of candidate entities based on a textual entity mention.
        :param only_subject_column: flag to include or exclude all columns from result
        """
        pass

    @abstractmethod
    def rank_candidate_entities_by_string_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column
        by using a string similarity.
        :return:
        """
        pass

    @abstractmethod
    def rank_candidate_entities_by_ner_based_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column
        by using a NER based similarity.
        """

    @abstractmethod
    def rank_candidate_entities_by_heading_based_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column
        by using a heading based similarity.
        """

    @abstractmethod
    def rank_candidate_entities_by_entity_embeddings_based_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column
        by using an entity embeddings based similarity.
        """

    @abstractmethod
    def rank_candidate_entities_by_context_based_similarity(self) -> None:
        """
        Rank a set of candidate entities for cell values of categorical columns including a subject column
        by using a context based similarity.
        """

    @abstractmethod
    def aggregate_ranked_candidate_entities(self) -> None:
        """
        Aggregate scores for candidate entities based on five heuristics.
        """
        pass

    @abstractmethod
    def annotate_cells(self) -> None:
        """
        Annotate all cell values.
        """
        pass

    @abstractmethod
    def rank_candidate_classes_by_majority_voting(self) -> None:
        """
        Rank candidate classes for categorical columns including a subject column by using a majority voting.
        """
        pass

    @abstractmethod
    def rank_candidate_classes_by_heading_similarity(self) -> None:
        """
        Rank candidate classes for categorical columns including a subject column by using a heading similarity.
        """

    @abstractmethod
    def rank_candidate_classes_by_column_type_prediction(self) -> None:
        """
        Rank candidate classes for categorical columns including a subject column by using a column type prediction.
        """

    @abstractmethod
    def aggregate_ranked_candidate_classes(self) -> None:
        """
        Aggregate scores for candidate classes based on three methods.
        """

    @abstractmethod
    def annotate_categorical_columns(self) -> None:
        """
        Annotate all categorical columns including a subject column.
        """

    @abstractmethod
    def annotate_literal_columns(self) -> None:
        """
        Annotate all literal columns based on recognized named entities (NER) in cells.
        """


class SemanticTableAnnotator(AbstractSemanticTableAnnotator):
    def __init__(self, table_model: TableModel = None):
        self._table_model = table_model

    @property
    def table_model(self):
        return self._table_model

    def find_candidate_entities(self, only_subject_column: bool = False) -> None:
        for column in self.table_model.columns:
            if (column.column_type == ColumnType.CATEGORICAL_COLUMN and not only_subject_column) or \
                    column.column_type == ColumnType.SUBJECT_COLUMN:
                for cell in column.cells:
                    if cell.cleared_value is not None and cell.candidate_entities is None:
                        # Get a set of candidate entities using the DBpedia SPARQL Endpoint
                        candidate_entities_from_dbs = dbs.get_candidate_entities(cell.cleared_value, False)
                        # Form dict of candidate entity models
                        if candidate_entities_from_dbs:
                            cell._candidate_entities = [EntityModel(item[0], item[1], item[2]) for item in candidate_entities_from_dbs]
                        # Get a set of candidate entities using the DBpedia Lookup
                        candidate_entities_from_dbl = dbl.get_candidate_entities(cell.cleared_value, 100, None, False)
                        # Form dict of candidate entity models
                        if candidate_entities_from_dbl:
                            for candidate_entity_from_dbl in candidate_entities_from_dbl:
                                exist_entity = False
                                for candidate_entity_from_dbs in candidate_entities_from_dbs:
                                    if candidate_entity_from_dbl[0] == candidate_entity_from_dbs[0]:
                                        exist_entity = True
                                if not exist_entity:
                                    entity = EntityModel(candidate_entity_from_dbl[0], candidate_entity_from_dbl[1],
                                                         candidate_entity_from_dbl[2])
                                    if cell.candidate_entities is None:
                                        cell._candidate_entities = []
                                    cell._candidate_entities += (entity,)
                        # Form a set of candidate entities for cells with same values
                        for c in column.cells:
                            if c.cleared_value == cell.cleared_value and c.candidate_entities is None:
                                c._candidate_entities = cell.candidate_entities
                    print("The candidate entity lookup for '" + str(cell.cleared_value) + "' cell is complete.")

    @staticmethod
    def get_levenshtein_distance(text_mention: str = None, candidate: str = None, candidates: Tuple = None,
                                 underscore_replacement: bool = True, short_name: bool = True) -> float:
        """
        Calculate the Levenshtein distance (edit distance) between two strings.
        :param text_mention: a textual mention of entity or class
        :param candidate: an candidate concept (entity or class)
        :param candidates: a set of candidate concepts (entities or classes)
        :param underscore_replacement: flag to enable or disable replace mode of underscore character with a space
        :param short_name: flag to enable or disable short concept name display mode (without full URI)
        :return: normalized Levenshtein distance in the range [0, ..., 1]
        """
        if underscore_replacement:
            candidate = candidate.replace("_", " ")
        if short_name:
            candidate = candidate.replace("http://dbpedia.org/resource/", "").replace("http://dbpedia.org/ontology/", "")
        # Calculate Levenshtein distance
        levenshtein_distance = distance(text_mention, candidate)
        # Normalize Levenshtein distance
        max_range = len(text_mention)
        for c in candidates:
            cnd = c.uri.replace("http://dbpedia.org/resource/", "").replace("http://dbpedia.org/ontology/", "") if short_name else c.uri
            if len(cnd) > max_range:
                max_range = len(cnd)
        normalized_levenshtein_distance = 1 - ((levenshtein_distance - 0) / (max_range - 0))

        return normalized_levenshtein_distance

    def rank_candidate_entities_by_string_similarity(self) -> None:
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._string_similarity = self.get_levenshtein_distance(cell.cleared_value, candidate_entity.uri,
                                                                                            cell.candidate_entities)
        print("Ranking of candidate entities by string similarity is complete.")

    def rank_candidate_entities_by_ner_based_similarity(self) -> None:
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        # Mapping between NER and ontology classes
                        target_classes = CLASS_MAPPING.get(cell.label)
                        # Define distance to a target class for a candidate entity
                        distance_to_class = dbs.get_distance_to_class(candidate_entity.uri, target_classes)
                        # Define a score based on distance to a target class
                        candidate_entity._ner_based_similarity = 1 if int(distance_to_class) > 0 else 0
        print("Ranking of candidate entities by NER based similarity is complete.")

    def rank_candidate_entities_by_heading_based_similarity(self) -> None:
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._heading_based_similarity = 0
        print("Ranking of candidate entities by heading based similarity is complete.")

    def rank_candidate_entities_by_entity_embeddings_based_similarity(self) -> None:
        list_new = []
        dictionary_new = {}
        list_words = []
        list_new1 = []
        list_total=[]
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        if candidate_entity:
                            list_new.append(candidate_entity.uri)
                            list_new1.append(candidate_entity.uri)
                    list_total.append(list_new1)
                    list_new1 = []
        list_new1 = list(set(list_new))
        transformer = RDF2VecTransformer(
            Word2Vec(epochs=10),
            walkers=[RandomWalker(4, 6, with_reverse=False, n_jobs=4)],
            verbose=1)
        kg = KG(
            "https://dbpedia.org/sparql",
            skip_predicates={"www.w3.org/1999/02/22-rdf-syntax-ns#type"},
            literals=[
                [
                    'http://dbpedia.org/ontology/abstract',
                    'http://dbpedia.org/ontology/flag',
                    'http://dbpedia.org/ontology/thumbnail',
                    'http://dbpedia.org/ontology/wikiPageExternalLink',
                    'http://dbpedia.org/ontology/wikiPageID',
                    'http://dbpedia.org/ontology/wikiPageRevisionID',
                    'http://dbpedia.org/ontology/wikiPageWikiLink',
                    'http://dbpedia.org/property/flagCaption',
                    'http://dbpedia.org/property/float',
                    'http://dbpedia.org/property/footnoteA',
                    'http://dbpedia.org/property/footnoteB',
                    'http://dbpedia.org/property/footnoteC',
                    'http://dbpedia.org/property/source',
                    'http://dbpedia.org/property/width',
                    'http://purl.org/dc/terms/subject',
                    'http://purl.org/linguistics/gold/hypernym',
                    'http://purl.org/voc/vrank#hasRank',
                    'http://www.georss.org/georss/point',
                    'http://www.w3.org/2000/01/rdf-schema#comment',
                    'http://www.w3.org/2000/01/rdf-schema#label',
                    'http://www.w3.org/2000/01/rdf-schema#seeAlso',
                    'http://www.w3.org/2002/07/owl#sameAs',
                    'http://www.w3.org/2003/01/geo/wgs84_pos#geometry',
                    'http://dbpedia.org/ontology/wikiPageRedirects',
                    'http://www.w3.org/2003/01/geo/wgs84_pos#lat',
                    'http://www.w3.org/2003/01/geo/wgs84_pos#long',
                    'http://www.w3.org/2004/02/skos/core#exactMatch',
                    'http://www.w3.org/ns/prov#wasDerivedFrom',
                    'http://xmlns.com/foaf/0.1/depiction',
                    'http://xmlns.com/foaf/0.1/homepage',
                    'http://xmlns.com/foaf/0.1/isPrimaryTopicOf',
                    'http://xmlns.com/foaf/0.1/name',
                    'http://dbpedia.org/property/website',
                    'http://dbpedia.org/property/west',
                    'http://dbpedia.org/property/wordnet_type',
                    'http://www.w3.org/2002/07/owl#differentFrom',
                ]
            ]
        )
        walkers = []
        for i in range(len(list_new1)):
            print("Walks were begun", i + 1)
            walkers1 = transformer.get_walks(kg, [list_new1[i]])
            print("Walks were completed")
            if walkers1:
                walkers.append(walkers1[0][0])
            else:
                walkers.append(list_new1[i])
        print("Fit was begun")
        # # transformer.transform(kg, list_new)
        print("Transform was completed")
        transformer.embedder._model.save("rdf2vec.model")
        modeller = W2V.load("rdf2vec.model")
        for entity in list_new:
            count = modeller.wv.most_similar(entity, topn=100000000)
            list_words.append(count)
        for list_of_words in list_words:
            for entity in list_new:
                for i in range(len(list_of_words)):
                    if entity == list_of_words[i][0]:
                        dictionary_new.setdefault(list_of_words[i][0], []).append(list_of_words[i][1])
        for key_values, precisions in dictionary_new.items():
            maximum = max(dictionary_new[key_values])
            dictionary_new.update([(key_values, (maximum + 1) / 2)])
            for column in self.table_model.columns:
                for cell in column.cells:
                    if cell.candidate_entities is not None:
                        for candidate_entity in cell.candidate_entities:
                            candidate_entity._entity_embeddings_based_similarity = dictionary_new[candidate_entity.uri]
        os.remove("rdf2vec.model")
        print("Ranking of candidate entities by entity embeddings based similarity is complete.")

    def rank_candidate_entities_by_context_based_similarity(self) -> None:
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._context_based_similarity = 0
        print("Ranking of candidate entities by context based similarity is complete.")

    def aggregate_ranked_candidate_entities(self) -> None:
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity.aggregate_scores()
        print("Aggregation of scores for candidate entities is complete.")

    def annotate_cells(self) -> None:
        for column in self.table_model.columns:
            for cell in column.cells:
                cell.annotate_cell()
        print("Annotation of table cell values is completed.")

    def rank_candidate_classes_by_majority_voting(self) -> None:
        for column in self.table_model.columns:
            if column.column_type != ColumnType.LITERAL_COLUMN:
                frequency = Counter()
                dbpedia_classes = {}
                for cell in column.cells:
                    # Get a set of classes from DBpedia for a referent entity
                    response = dbs.get_classes_for_entity(cell.annotation, False)
                    dbpedia_classes.update(response)
                    # Calculate a class occurrence frequency
                    frequency.update(Counter([*response]))
                # Sort by frequency
                result = dict(sorted(dict(frequency).items(), key=lambda item: item[1], reverse=True))
                if result:
                    # Normalize scores based on frequency
                    column._candidate_classes = []
                    for key, value in result.items():
                        score = value / list(result.values())[0] if list(result.values())[0] != 0 else 0
                        class_model = ClassModel(key, dbpedia_classes.get(key)[0], dbpedia_classes.get(key)[1], score)
                        column._candidate_classes += (class_model,)
        print("Ranking of candidate classes by majority voting is complete.")

    def rank_candidate_classes_by_heading_similarity(self) -> None:
        for column in self.table_model.columns:
            if column.column_type != ColumnType.LITERAL_COLUMN:
                # Get a set of candidate classes using the DBpedia SPARQL Endpoint
                candidate_classes = dbs.get_candidate_classes(column.header_name, False)
                if candidate_classes:
                    if column.candidate_classes is None:
                        column._candidate_classes = []
                    for candidate_class in candidate_classes:
                        # Find duplicate candidate class
                        exist_class = False
                        for c in column.candidate_classes:
                            if c.uri == candidate_class[0]:
                                exist_class = True
                        if not exist_class:
                            # Add new candidate classes
                            column._candidate_classes += (ClassModel(candidate_class[0], candidate_class[1], candidate_class[2]),)
                if column.candidate_classes is not None:
                    for candidate_class in column.candidate_classes:
                        # Calculate Levenshtein distance between column header name and class URI
                        candidate_class._heading_similarity = self.get_levenshtein_distance(column.header_name, candidate_class.uri,
                                                                                            column.candidate_classes)
                    # Sort candidate classes by heading similarity
                    column.candidate_classes.sort(key=lambda c: c.heading_similarity, reverse=True)
        print("Ranking of candidate classes by heading similarity is complete.")

    def rank_candidate_classes_by_column_type_prediction(self) -> None:
        for column in self.table_model.columns:
            if column.candidate_classes is not None:
                for candidate_class in column.candidate_classes:
                    candidate_class._column_type_prediction_score = 0
        print("Ranking of candidate classes by column type prediction is complete.")

    def aggregate_ranked_candidate_classes(self) -> None:
        for column in self.table_model.columns:
            if column.candidate_classes is not None:
                for candidate_class in column.candidate_classes:
                    candidate_class.aggregate_scores()
                column.candidate_classes.sort(key=lambda c: c.final_score, reverse=True)  # Sort candidate classes by final score
        print("Aggregation of scores for candidate classes is complete.")

    def annotate_categorical_columns(self) -> None:
        for column in self.table_model.columns:
            if column.column_type != ColumnType.LITERAL_COLUMN:
                column.annotate_column()
        print("Annotation of categorical (named entity) columns of table is completed.")

    def annotate_literal_columns(self) -> None:
        for column in self.table_model.columns:
            if column.column_type == ColumnType.LITERAL_COLUMN:
                xml_schema_data_types = []
                for cell in column.cells:
                    for label in cell.label:
                        # Mapping between NER and XML Schema datatype
                        datatype = DATATYPE_MAPPING.get(label) if DATATYPE_MAPPING.get(label) is not None else XMLSchemaDataType.STRING
                        xml_schema_data_types.append(datatype)
                column._annotation = [dt for dt, dt_count in Counter(xml_schema_data_types).most_common(1)][0]
        print("Annotation of literal columns of table is completed.")
