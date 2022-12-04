import os
from collections import Counter
from typing import Tuple

import tabbyld2.table_annotation.dbpedia_lookup as dbl
from Levenshtein._levenshtein import distance
from concept_mapping import CLASS_MAPPING, DATATYPE_MAPPING, XMLSchemaDataType
from gensim.models.word2vec import Word2Vec
from pyrdf2vec import RDF2VecTransformer
from pyrdf2vec.embedders import Word2Vec
from pyrdf2vec.graphs import KG
from pyrdf2vec.walkers import RandomWalker
from tabbyld2.datamodel.knowledge_graph_model import ClassModel, EntityModel
from tabbyld2.datamodel.tabular_data_model import TableModel
from tabbyld2.preprocessing.atomic_column_classifier import ColumnType
from tabbyld2.table_annotation.abstract import AbstractSemanticTableAnnotator
from tabbyld2.table_annotation.dbpedia_sparql_endpoint import DBPediaConfig, get_candidate_classes, get_candidate_entities, \
    get_classes_for_entity, get_distance_to_class


class SemanticTableAnnotator(AbstractSemanticTableAnnotator):

    def __init__(self, table_model: TableModel = None):
        self._table_model = table_model

    @property
    def table_model(self):
        return self._table_model

    def find_candidate_entities(self, only_subject_column: bool = False):
        for column in self.table_model.columns:
            if (column.column_type == ColumnType.CATEGORICAL_COLUMN and not only_subject_column) or \
                    column.column_type == ColumnType.SUBJECT_COLUMN:
                for cell in column.cells:
                    if cell.cleared_value is not None and cell.candidate_entities is None:
                        # Get a set of candidate entities using the DBpedia SPARQL Endpoint
                        candidate_entities = get_candidate_entities(cell.cleared_value, False)
                        # Get a set of candidate entities using the DBpedia Lookup
                        candidate_entities_from_dbl = dbl.get_candidate_entities(cell.cleared_value, 100, None, False)
                        # Form common dict for candidate entities
                        for entity_uri, item in candidate_entities_from_dbl.items():
                            if entity_uri not in candidate_entities:
                                candidate_entities[entity_uri] = item
                        if candidate_entities:
                            cell.set_candidate_entities([EntityModel(key, item[0], item[1]) for key, item in candidate_entities.items()])
                        # Form a set of candidate entities for cells with same values
                        for cl in column.cells:
                            if cl.cleared_value == cell.cleared_value and cl.candidate_entities is None:
                                cl.set_candidate_entities(cell.candidate_entities)
                    print("The candidate entity lookup for '" + str(cell.cleared_value) + "' cell is complete.")

    @staticmethod
    def get_levenshtein_distance(text_mention: str, candidate: str, candidates: Tuple[EntityModel, ...],
                                 underscore_replacement: bool = True, short_name: bool = True) -> float:
        """
        Calculate the Levenshtein distance (edit distance) between two strings
        :param text_mention: a textual mention of entity or class
        :param candidate: a candidate concept (entity or class)
        :param candidates: a set of candidate concepts (entities or classes)
        :param underscore_replacement: flag to enable or disable replace mode of underscore character with a space
        :param short_name: flag to enable or disable short concept name display mode (without full URI)
        :return: normalized Levenshtein distance in the range [0, ..., 1]
        """
        if underscore_replacement:
            candidate = candidate.replace("_", " ")
        if short_name:
            candidate = candidate.replace(DBPediaConfig.BASE_RESOURCE_URI, "").replace(DBPediaConfig.BASE_ONTOLOGY_URI, "")
        levenshtein_distance = distance(text_mention, candidate)  # Calculate Levenshtein distance
        # Normalize Levenshtein distance
        max_range = len(text_mention)
        for c in candidates:
            cnd = c.uri.replace(DBPediaConfig.BASE_RESOURCE_URI, "").replace(DBPediaConfig.BASE_ONTOLOGY_URI, "") if short_name else c.uri
            if len(cnd) > max_range:
                max_range = len(cnd)
        return 1 - ((levenshtein_distance - 0) / (max_range - 0))

    def rank_candidate_entities_by_string_similarity(self):
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._string_similarity = self.get_levenshtein_distance(
                            cell.cleared_value,
                            candidate_entity.uri,
                            cell.candidate_entities
                        )
        print("Ranking of candidate entities by string similarity is complete.")

    def rank_candidate_entities_by_ner_based_similarity(self):
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        # Define distance to a target class for a candidate entity
                        distance_to_class = get_distance_to_class(candidate_entity.uri, CLASS_MAPPING.get(cell.label))
                        # Define a score based on distance to a target class
                        candidate_entity._ner_based_similarity = 1 if int(distance_to_class) > 0 else 0
        print("Ranking of candidate entities by NER based similarity is complete.")

    def rank_candidate_entities_by_heading_based_similarity(self):
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._heading_based_similarity = 0
        print("Ranking of candidate entities by heading based similarity is complete.")

    def rank_candidate_entities_by_entity_embeddings_based_similarity(self):
        list_new, dictionary_new, list_words, list_new1, list_total = [], {}, [], [], []
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
        transformer = RDF2VecTransformer(Word2Vec(epochs=10), walkers=[RandomWalker(4, 6, with_reverse=False, n_jobs=4)], verbose=1)
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
            walkers.append(walkers1[0][0]) if walkers1 else walkers.append(list_new1[i])
        print("Fit was begun")
        # transformer.transform(kg, list_new)
        print("Transform was completed")
        transformer.embedder._model.save("rdf2vec.model")
        modeller = Word2Vec.load("rdf2vec.model")
        for entity in list_new:
            count = modeller.wv.most_similar(entity, topn=100000000)
            list_words.append(count)
        for list_of_words in list_words:
            for entity in list_new:
                for i in range(len(list_of_words)):
                    if entity == list_of_words[i][0]:
                        dictionary_new.setdefault(list_of_words[i][0], []).append(list_of_words[i][1])
        for key_values in dictionary_new.keys():
            maximum = max(dictionary_new[key_values])
            dictionary_new.update([(key_values, (maximum + 1) / 2)])
            for column in self.table_model.columns:
                for cell in column.cells:
                    if cell.candidate_entities is not None:
                        for candidate_entity in cell.candidate_entities:
                            candidate_entity._entity_embeddings_based_similarity = dictionary_new[candidate_entity.uri]
        os.remove("rdf2vec.model")
        print("Ranking of candidate entities by entity embeddings based similarity is complete.")

    def rank_candidate_entities_by_context_based_similarity(self):
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._context_based_similarity = 0
        print("Ranking of candidate entities by context based similarity is complete.")

    def aggregate_ranked_candidate_entities(self):
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity.aggregate_scores()
        print("Aggregation of scores for candidate entities is complete.")

    def annotate_cells(self):
        for column in self.table_model.columns:
            for cell in column.cells:
                cell.annotate_cell()
        print("Annotation of table cell values is completed.")

    def rank_candidate_classes_by_majority_voting(self):
        for column in self.table_model.columns:
            if column.column_type != ColumnType.LITERAL_COLUMN:
                frequency = Counter()
                dbpedia_classes = {}
                for cell in column.cells:
                    # Get a set of classes from DBpedia for a referent entity
                    response = get_classes_for_entity(cell.annotation, False)
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

    def rank_candidate_classes_by_heading_similarity(self):
        for column in self.table_model.columns:
            if column.column_type != ColumnType.LITERAL_COLUMN:
                # Get a set of candidate classes using the DBpedia SPARQL Endpoint
                candidate_classes = get_candidate_classes(column.header_name, False)
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
                    column.candidate_classes.sort(key=lambda cl: cl.heading_similarity, reverse=True)
        print("Ranking of candidate classes by heading similarity is complete.")

    def rank_candidate_classes_by_column_type_prediction(self):
        for column in self.table_model.columns:
            if column.candidate_classes is not None:
                for candidate_class in column.candidate_classes:
                    candidate_class._column_type_prediction_score = 0
        print("Ranking of candidate classes by column type prediction is complete.")

    def aggregate_ranked_candidate_classes(self):
        for column in self.table_model.columns:
            if column.candidate_classes is not None:
                for candidate_class in column.candidate_classes:
                    candidate_class.aggregate_scores()
                column.candidate_classes.sort(key=lambda c: c.final_score, reverse=True)  # Sort candidate classes by final score
        print("Aggregation of scores for candidate classes is complete.")

    def annotate_categorical_columns(self):
        for column in self.table_model.columns:
            if column.column_type != ColumnType.LITERAL_COLUMN:
                column.annotate_column()
        print("Annotation of categorical (named entity) columns of table is completed.")

    def annotate_literal_columns(self):
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
