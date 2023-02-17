from collections import Counter
from typing import Tuple

import tabbyld2.table_annotation.dbpedia_lookup as dbl
from Levenshtein._levenshtein import distance
from gensim.models.word2vec import Word2Vec
from tabbyld2.datamodel.knowledge_graph_model import ClassModel, EntityModel
from tabbyld2.datamodel.tabular_data_model import TableModel
from tabbyld2.preprocessing.atomic_column_classifier import ColumnType
from tabbyld2.table_annotation.abstract import AbstractSemanticTableAnnotator
from tabbyld2.table_annotation.concept_mapping import CLASS_MAPPING, DATATYPE_MAPPING, OntologyClass, XMLSchemaDataType
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
                        # Get a set of candidate entities using the DBpedia Lookup
                        candidate_entities_from_dbl = dbl.get_candidate_entities(cell.cleared_value, 100, None)
                        # Get a set of candidate entities using the DBpedia SPARQL Endpoint
                        candidate_entities = get_candidate_entities(cell.cleared_value, False if candidate_entities_from_dbl else True)
                        # Form common dict for candidate entities
                        for entity_uri, item in candidate_entities_from_dbl.items():
                            if entity_uri not in candidate_entities:
                                candidate_entities[entity_uri] = item
                        if candidate_entities:
                            cell.set_candidate_entities([EntityModel(uri, lb, cm, rd) for uri, (lb, cm, rd) in candidate_entities.items()])
                        # Form a set of candidate entities for cells with same values
                        for cl in column.cells:
                            if cl.cleared_value == cell.cleared_value and cl.candidate_entities is None:
                                cl.set_candidate_entities(cell.candidate_entities)
                        print("The candidate entity lookup for '" + str(cell.cleared_value) + "' cell is complete.")

    @staticmethod
    def _normalize(current_value: int, max_range: int, min_range: int = 0) -> float:
        """
        Normalize value by using MinMax method
        :param current_value: current value for normalization
        :param max_range: maximum value
        :param min_range: minimum value
        :return: normalized value
        """
        try:
            return (current_value - min_range) / (max_range - min_range)
        except ZeroDivisionError:
            return 0

    def get_levenshtein_distance(self, text_mention: str, candidate: str, candidates: Tuple[EntityModel, ...],
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
        return 1 - self._normalize(levenshtein_distance, max_range)

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
        list_new = []
        list_new1 = []
        list_total = []
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        if candidate_entity:
                            list_new.append(candidate_entity.uri)
                            list_new1.append(candidate_entity.uri)
                    list_total.append(list_new1)
                    list_new1 = []
        dictionary_sym = {}

        def sym(entity1, entity2):
            try:
                count = modeller.wv.similarity(entity1, entity2)
            except:
                count = 0
            dictionary_sym.setdefault(entity1, []).append(float(count))
            dictionary_sym.setdefault(entity2, []).append(float(count))

        print("Model is loading")
        modeller = Word2Vec.load("model")
        print("Model loading completed")
        count_list_candidates = 0
        print("Similarity begin")
        dictionary_list_sym = {}
        end = len(list_total)
        end_end = len(list_new) - len(list_total[end - 1])
        begin = len(list_total[0])
        for i in range(0, end_end):
            if list_new[i] not in list_total[count_list_candidates]:
                if count_list_candidates != 0:
                    begin += len(list_total[count_list_candidates])
                count_list_candidates += 1
            for j in range(begin, len(list_new)):
                if list_new[j] not in list_total[count_list_candidates]:
                    sym(list_new[i], list_new[j])
        count_list_candidates = 0
        temp_list = []

        for key_values in dictionary_sym.keys():
            if key_values not in list_total[count_list_candidates]:
                count_list_candidates += 1
            if count_list_candidates >= len(list_total):
                count_list_candidates -= 1
            len_list = 0
            for j in range(len(list_total)):
                if j != count_list_candidates:
                    begin = len_list
                    len_list += len(list_total[j])
                    if len_list > len(dictionary_sym[key_values]):
                        len_list -= len(list_total[j])
                    for i in range(begin, len_list):
                        temp_list.append(dictionary_sym[key_values][i])
                    if begin != len_list:
                        dictionary_list_sym.setdefault(key_values, []).append(temp_list)
                        temp_list = []
        for key_values in dictionary_list_sym.keys():
            temp_list = []
            for item in dictionary_list_sym[key_values]:
                temp_list.append(float(max(item)))
            dictionary_list_sym[key_values] = temp_list
        ans_list = []
        ans_temp = []
        for i in range(len(list_total)):
            for j in range(len(list_total[i])):
                ans_temp.append(dictionary_list_sym[list_total[i][j]])
            ans_list.append(ans_temp)
            ans_temp = []
        dict_ans = {}
        for i in range(len(list_total)):
            if len(list_total[i]) == 1:
                dict_ans.setdefault(list_total[i][0], []).append(max(ans_list[i][0]))
            else:
                for j in range(len(list_total[i])):
                    ans_list[i][j] = sum(ans_list[i][j])
                    dict_ans.setdefault(list_total[i][j], []).append(ans_list[i][j])
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._entity_embeddings_based_similarity = dict_ans[candidate_entity.uri][0]
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
                dbpedia_classes, response = {}, {}
                for cell in column.cells:
                    if cell.annotation is not None:
                        # Get a set of classes from DBpedia for a referent entity
                        if cell.annotation.uri not in response:
                            response[cell.annotation.uri] = get_classes_for_entity(cell.annotation.uri, False)
                        dbpedia_classes.update(response[cell.annotation.uri])
                        frequency.update(Counter([*response[cell.annotation.uri]]))  # Calculate a class occurrence frequency
                result = dict(sorted(dict(frequency).items(), key=lambda item: item[1], reverse=True))  # Sort by frequency
                if result:
                    # Normalize scores based on frequency
                    candidate_classes = []
                    for key, value in result.items():
                        try:
                            score = value / list(result.values())[0]
                        except ZeroDivisionError:
                            score = 0
                        candidate_classes.append(ClassModel(key, dbpedia_classes.get(key)[0], dbpedia_classes.get(key)[1], score))
                    column.set_candidate_classes(candidate_classes)
        print("Ranking of candidate classes by majority voting is complete.")

    def rank_candidate_classes_by_heading_similarity(self):
        for column in self.table_model.columns:
            if column.column_type != ColumnType.LITERAL_COLUMN:
                # Get a set of candidate classes using the DBpedia SPARQL Endpoint
                candidate_classes_from_dbp = get_candidate_classes(column.header_name)
                if candidate_classes_from_dbp:
                    if column.candidate_classes is None:
                        column._candidate_classes = []
                    for class_uri, (class_label, class_comment) in candidate_classes_from_dbp.items():
                        # Find duplicate candidate class
                        exist_class = False
                        for c in column.candidate_classes:
                            if c.uri == class_uri:
                                exist_class = True
                        if not exist_class:
                            column._candidate_classes += (ClassModel(class_uri, class_label, class_comment),)  # Add new candidate class
                if column.candidate_classes is not None:
                    for candidate_class in column.candidate_classes:
                        candidate_class.set_heading_similarity(
                            self.get_levenshtein_distance(column.header_name, candidate_class.uri, column.candidate_classes)
                        )
                    # Sort candidate classes by heading similarity
                    column.candidate_classes.sort(key=lambda cl: cl.heading_similarity, reverse=True)
        print("Ranking of candidate classes by heading similarity is complete.")

    def rank_candidate_classes_by_column_type_prediction(self):
        for column in self.table_model.columns:
            if column.candidate_classes is not None:
                for candidate_class in column.candidate_classes:
                    candidate_class.set_column_type_prediction_score(0)
        print("Ranking of candidate classes by column type prediction is complete.")

    def rank_candidate_classes_by_ner_based_similarity(self, include_none: bool = True):
        for column in self.table_model.columns:
            if column.column_type != ColumnType.LITERAL_COLUMN:
                labels = []
                for cell in column.cells:
                    for value in cell.label if isinstance(cell.label, list) else [cell.label]:
                        ontology_classes = CLASS_MAPPING.get(value, OntologyClass.THING)
                        if not include_none and ontology_classes is OntologyClass.THING:
                            continue
                        labels.extend(ontology_classes if isinstance(ontology_classes, list) else [ontology_classes])
                ranks = Counter(labels).most_common()
                if column.candidate_classes is None:
                    column.set_candidate_classes([
                        ClassModel(label.value, ner_based_similarity=self._normalize(count, ranks[0][1])) for label, count in ranks
                    ])
                else:
                    for candidate_class in column.candidate_classes:
                        new_candidate_classes = {label.value: self._normalize(count, ranks[0][1]) for label, count in ranks}
                        if candidate_class.uri in new_candidate_classes:
                            candidate_class.set_ner_based_similarity(new_candidate_classes.get(candidate_class.uri))
        print("Ranking of candidate classes by NER based similarity is complete.")

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
                column.set_annotation([dt for dt, dt_count in Counter(xml_schema_data_types).most_common(1)][0])
        print("Annotation of literal columns of table is completed.")
