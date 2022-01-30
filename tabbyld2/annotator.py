import os
from abc import ABC
from collections import Counter
from Levenshtein._levenshtein import distance
from pyrdf2vec.graphs import KG
from pyrdf2vec import RDF2VecTransformer
from pyrdf2vec.embedders import Word2Vec
from pyrdf2vec.walkers import RandomWalker
from gensim.models.word2vec import Word2Vec as W2V
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


class AbstractSemanticTableAnnotator(ABC):
    __slots__ = ()


class SemanticTableAnnotator(AbstractSemanticTableAnnotator):
    def __init__(self, table_model: TableModel = None):
        self._table_model = table_model

    @property
    def table_model(self):
        return self._table_model

    def find_candidate_entities(self):
        """
        Поиск сущностей кандидатов на основе текстового упоминания сущности.
        """
        for column in self.table_model.columns:
            if column.column_type == ColumnType.CATEGORICAL_COLUMN or column.column_type == ColumnType.SUBJECT_COLUMN:
                for cell in column.cells:
                    # Получение сущностей кандидатов на основе конечной точки DBpedia SPARQL Endpoint
                    candidate_entities_from_dbs = dbs.get_candidate_entities(cell.cleared_value, False)
                    # Формирование словаря моделей сущностей кандидатов
                    if candidate_entities_from_dbs:
                        cell._candidate_entities = tuple()
                        for candidate_entity in candidate_entities_from_dbs:
                            entity = EntityModel(candidate_entity[0], candidate_entity[1], candidate_entity[2],
                                                 0, 0, 0, 0, 0, 0)
                            cell._candidate_entities = cell.candidate_entities + (entity,)
                    # Получение сущностей кандидатов от сервиса DBpedia Lookup
                    candidate_entities_from_dbl = dbl.get_candidate_entities(cell.cleared_value, 100, None, False)
                    # Формирование словаря моделей сущностей кандидатов
                    if candidate_entities_from_dbl:
                        if cell._candidate_entities is None:
                            cell._candidate_entities = tuple()
                        for candidate_entity_from_dbl in candidate_entities_from_dbl:
                            exist_entity = False
                            for candidate_entity_from_dbs in candidate_entities_from_dbs:
                                if candidate_entity_from_dbl[0] == candidate_entity_from_dbs[0]:
                                    exist_entity = True
                            if not exist_entity:
                                entity = EntityModel(candidate_entity_from_dbl[0], candidate_entity_from_dbl[1],
                                                     candidate_entity_from_dbl[2], 0, 0, 0, 0, 0, 0)
                                cell._candidate_entities = cell.candidate_entities + (entity,)
                    print("The candidate entity lookup for '" + str(cell.cleared_value) + "' cell is complete.")

    @staticmethod
    def get_levenshtein_distance(entity_mention: str = None, candidate_entity: str = None,
                                 underscore_replacement: bool = False, short_name: bool = False):
        """
        Вычисление расстояния Левенштейна (редактирования) между двумя строками.
        :param entity_mention: текстовое упоминание сущности
        :param candidate_entity: сущность кандидат
        :param underscore_replacement: режим замены символа нижнего подчеркивания на пробел
        :param short_name: режим отображения короткого наименования сущности (без полного URI)
        :return: нормализованное расстояние Левенштейна в диапазоне [0, ..., 1]
        """
        # Замена символа нижнего подчеркивания на пробел
        if underscore_replacement:
            candidate_entity = candidate_entity.replace("_", " ")
        # Удаление URI-адреса в имени сущности
        if short_name:
            candidate_entity = candidate_entity.replace("http://dbpedia.org/resource/", "")
        # Вычисление абсолютного расстояния Левенштейна
        levenshtein_distance = distance(entity_mention, candidate_entity)
        # Нижняя граница
        min_range = 0
        # Определение верхней границы
        if len(entity_mention) > len(candidate_entity):
            max_range = len(entity_mention)
        else:
            max_range = len(candidate_entity)
        # Нормализация абсолютного расстояния Левенштейна
        normalized_levenshtein_distance = 1 - ((levenshtein_distance - min_range) / (max_range - min_range))

        return normalized_levenshtein_distance

    def rank_candidate_entities_by_string_similarity(self):
        """
        Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов,
        включая сущностный столбец, по схоству строк.
        """
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._string_similarity = self.get_levenshtein_distance(cell.cleared_value,
                                                                                            candidate_entity.uri,
                                                                                            True, True)
        print("Ranking of candidate entities by string similarity is complete.")

    def rank_candidate_entities_by_ner_based_similarity(self):
        """
        Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов,
        включая сущностный столбец, по сходству на основе NER-классов.
        """
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        # Поиск целевого класса DBpedia на основе NER-класса
                        target_classes = ""
                        if cell.label == NamedEntityLabel.LOCATION:
                            target_classes = [OntologyClass.PARK, OntologyClass.MINE, OntologyClass.GARDEN,
                                              OntologyClass.WINE_REGION, OntologyClass.NATURAL_PLACE,
                                              OntologyClass.PROTECTED_AREA, OntologyClass.WORLD_HERITAGE_SITE,
                                              OntologyClass.SITE_OF_SPECIAL_SCIENTIFIC_INTEREST]
                        if cell.label == NamedEntityLabel.GPE:
                            target_classes = OntologyClass.POPULATED_PLACE
                        if cell.label == NamedEntityLabel.NORP:
                            target_classes = OntologyClass.ETHNIC_GROUP
                        if cell.label == NamedEntityLabel.PERSON:
                            target_classes = OntologyClass.PERSON
                        if cell.label == NamedEntityLabel.PRODUCT:
                            target_classes = [OntologyClass.DEVICE, OntologyClass.FOOD,
                                              OntologyClass.MEAN_OF_TRANSPORTATION]
                        if cell.label == NamedEntityLabel.FACILITY:
                            target_classes = OntologyClass.ARCHITECTURAL_STRUCTURE
                        if cell.label == NamedEntityLabel.ORGANIZATION:
                            target_classes = OntologyClass.ORGANISATION
                        if cell.label == NamedEntityLabel.EVENT:
                            target_classes = OntologyClass.EVENT
                        if cell.label == NamedEntityLabel.ART_WORK:
                            target_classes = OntologyClass.WORK
                        if cell.label == NamedEntityLabel.LAW:
                            target_classes = [OntologyClass.LAW, OntologyClass.LEGAL_CASE]
                        # Определение дистанции до целевого класса для сущности-кандидата
                        distance_to_class = dbs.get_distance_to_class(candidate_entity.uri, target_classes)
                        # Определение оценки на основе дистанции до целевого класса
                        candidate_entity._ner_based_similarity = (1 if int(distance_to_class) > 0 else 0)
        print("Ranking of candidate entities by NER based similarity is complete.")

    def rank_candidate_entities_by_heading_based_similarity(self):
        """
        Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов,
        включая сущностный столбец, по сходству на основе заголовка столбца.
        """
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._heading_based_similarity = 0
        print("Ranking of candidate entities by heading based similarity is complete.")

    def rank_candidate_entities_by_entity_embeddings_based_similarity(self):
        """
        Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов, включая сущностный столбец,
        по сходству на основе семантической близости между сущностями кандидатами.
        """
        # # Вычисление оценок для сущностей из набора кандидатов по сходству на основе
        # # семантической близости между сущностями кандидатами
        # list_new = []
        # dictionary_new = {}
        # list_words = []
        # for key, items in table_with_candidate_entities.items():
        #     if items:
        #         for entity_mention, candidate_entities in items.items():
        #             if candidate_entities:
        #                 for i in range(len(candidate_entities)):
        #                     list_new.append(candidate_entities[i])
        # knowledge_graph = KG(
        #     "https://dbpedia.org/sparql",
        #     skip_predicates={"www.w3.org/1999/02/22-rdf-syntax-ns#type"},
        #     literals=[
        #         [
        #             "http://dbpedia.org/ontology/wikiPageWikiLink",
        #             "http://www.w3.org/2004/02/skos/core#prefLabel",
        #         ],
        #         ["http://dbpedia.org/ontology/humanDevelopmentIndex"],
        #     ],
        # )
        # transformer = RDF2VecTransformer(
        #     Word2Vec(epochs=10),
        #     walkers=[RandomWalker(4, 10, with_reverse=False, n_jobs=2)],
        #     # verbose=1
        # )
        # transformer.fit_transform(knowledge_graph, list_new)
        # transformer.embedder._model.save("rdf2vec.model")
        # modeller = W2V.load("rdf2vec.model")
        # for entity in list_new:
        #     count = modeller.wv.most_similar(entity, topn=100000000)
        #     list_words.append(count)
        # for list_of_words in list_words:
        #     for entity in list_new:
        #         for i in range(len(list_of_words)):
        #             if entity == list_of_words[i][0]:
        #                 dictionary_new.setdefault(list_of_words[i][0], []).append(list_of_words[i][1])
        # for key_values, precisions in dictionary_new.items():
        #     maximum = max(dictionary_new[key_values])
        #     dictionary_new.update([(key_values, (maximum + 1) / 2)])
        # for key, items in table_with_candidate_entities.items():
        #     if items:
        #         for keys_entities, item_items in items.items():
        #             if item_items:
        #                 dictionary = {}
        #                 for i in range(len(item_items)):
        #                     dictionary[item_items[i]] = dict()
        #                     dictionary[item_items[i]] = dictionary_new[items[keys_entities][i]]
        #                 items[keys_entities] = dictionary
        #                 for key_values, item_values in items[keys_entities].items():
        #                     items[keys_entities][key_values] = items[keys_entities][key_values] * EES_WEIGHT_FACTOR
        #
        #                 items[keys_entities] = dict(
        #                     sorted(items[keys_entities].items(), key=lambda item: item[1], reverse=True))
        # os.remove("rdf2vec.model")
        print("Ranking of candidate entities by entity embeddings based similarity is complete.")

    def rank_candidate_entities_by_context_based_similarity(self):
        """
        Ранжирование сущностей кандидатов для значений ячеек категориальных столбцов,
        включая сущностный столбец, по сходству на основе контекста.
        """
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity._context_based_similarity = 0
        print("Ranking of candidate entities by context based similarity is complete.")

    def aggregate_ranked_candidate_entities(self):
        """
        Агрегирование оценок (рангов) для сущностей кандидатов всех значений ячеек, полученных на основе пяти эвристик.
        """
        for column in self.table_model.columns:
            for cell in column.cells:
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        candidate_entity.aggregate_scores()
        print("Aggregation of scores for candidate entities is complete.")

    def annotate_cells(self):
        """
        Аннотирование всех значений ячеек таблицы.
        """
        for column in self.table_model.columns:
            for cell in column.cells:
                cell.annotate_cell()
        print("Annotation of table cell values is completed.")

    def rank_candidate_classes_by_majority_voting(self):
        """
        Ранжирование классов кандидатов для категориальных столбцов, включая сущностный столбец,
        на основе голосования большинством.
        """
        for column in self.table_model.columns:
            if column.column_type == ColumnType.CATEGORICAL_COLUMN or column.column_type == ColumnType.SUBJECT_COLUMN:
                result = dict()
                for cell in column.cells:
                    # Получение набора классов из DBpedia для референтной сущности
                    dbpedia_classes = dbs.get_classes(cell.annotation, False)
                    # Определение частоты появления класса
                    for dbpedia_class in dbpedia_classes:
                        if dbpedia_class not in result:
                            result[dbpedia_class] = 1
                        else:
                            result[dbpedia_class] += 1
                # Сортировка по частоте
                result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
                if result:
                    column._candidate_classes = tuple()
                    # Нормализация оценок на основе частоты
                    result_list = list(result.values())
                    max_range = result_list[0]
                    min_range = result_list[-1]
                    for key, value in result.items():
                        if max_range - min_range != 0:
                            score = (value - min_range) / (max_range - min_range)
                        else:
                            score = 0
                        class_model = ClassModel(key, None, None, score)
                        column._candidate_classes = column.candidate_classes + (class_model,)
        print("Ranking of candidate classes by majority voting is complete.")

    def rank_candidate_classes_by_heading_similarity(self):
        """
        Ранжирование классов кандидатов для категориальных столбцов, включая сущностный столбец,
        на основе по сходству заголовка столбца.
        """
        for column in self.table_model.columns:
            if column.candidate_classes is not None:
                for candidate_class in column.candidate_classes:
                    candidate_class._heading_similarity = 0
        print("Ranking of candidate classes by heading similarity is complete.")

    def rank_candidate_classes_by_column_type_prediction(self):
        """
        Ранжирование классов кандидатов для категориальных столбцов, включая сущностный столбец,
        на основе прогнозирования класса.
        """
        for column in self.table_model.columns:
            if column.candidate_classes is not None:
                for candidate_class in column.candidate_classes:
                    candidate_class._column_type_prediction_score = 0
        print("Ranking of candidate classes by column type prediction is complete.")

    def aggregate_ranked_candidate_classes(self):
        """
        Агрегирование оценок (рангов) для классов кандидатов всех категориальных столбцов, включая сущностный столбец,
        полученных на основе трех методов ранжирования.
        """
        for column in self.table_model.columns:
            if column.candidate_classes is not None:
                for candidate_class in column.candidate_classes:
                    candidate_class.aggregate_scores()
        print("Aggregation of scores for candidate classes is complete.")

    def annotate_categorical_columns(self):
        """
        Аннотирование всех категориальных столбцов таблицы, включая сущностный столбец.
        """
        for column in self.table_model.columns:
            if column.column_type == ColumnType.CATEGORICAL_COLUMN or column.column_type == ColumnType.SUBJECT_COLUMN:
                column.annotate_column()
        print("Annotation of categorical (named entity) columns of table is completed.")

    def annotate_literal_columns(self):
        """
        Аннотирование всех литеральных столбцов таблицы на основе распознанных именованных сущностей в ячейках.
        """
        for column in self.table_model.columns:
            if column.column_type == ColumnType.LITERAL_COLUMN:
                xml_schema_data_types = []
                for cell in column.cells:
                    datatype = XMLSchemaDataType.STRING
                    if cell.label == LiteralLabel.DATE:
                        datatype = XMLSchemaDataType.DATE
                    if cell.label == LiteralLabel.TIME:
                        datatype = XMLSchemaDataType.TIME
                    if cell.label == LiteralLabel.PERCENT or cell.label == LiteralLabel.MONEY or \
                            cell.label == LiteralLabel.QUANTITY or cell.label == LiteralLabel.POSITIVE_INTEGER:
                        datatype = XMLSchemaDataType.NON_NEGATIVE_INTEGER
                    if cell.label == LiteralLabel.ORDINAL:
                        datatype = XMLSchemaDataType.POSITIVE_INTEGER
                    if cell.label == LiteralLabel.CARDINAL or cell.label == LiteralLabel.MAIL or \
                            cell.label == LiteralLabel.BANK_CARD or cell.label == LiteralLabel.PHONE:
                        datatype = XMLSchemaDataType.DECIMAL
                    if cell.label == LiteralLabel.NEGATIVE_INTEGER:
                        datatype = XMLSchemaDataType.NEGATIVE_INTEGER
                    if cell.label == LiteralLabel.FLOAT:
                        datatype = XMLSchemaDataType.FLOAT
                    if cell.label == LiteralLabel.BOOLEAN:
                        datatype = XMLSchemaDataType.BOOLEAN
                    if cell.label == LiteralLabel.BOOLEAN:
                        datatype = XMLSchemaDataType.BOOLEAN
                    if cell.label == LiteralLabel.URL:
                        datatype = XMLSchemaDataType.URL
                    xml_schema_data_types.append(datatype)
                column._annotation = [dt for dt, dt_count in Counter(xml_schema_data_types).most_common(1)][0]
        print("Annotation of literal columns of table is completed.")
