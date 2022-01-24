from Levenshtein._levenshtein import distance
import tabbyld2.dbpedia_sparql_endpoint as dbs
from gensim.models import Word2Vec
import tabbyld2.column_classifier as cc



# Названия классов в DBpedia, соответствующие NER-классам
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

# Весовые коэффициенты для балансировки важности оценок, полученных на основе применения 5 эвристик определения сходства
SS_WEIGHT_FACTOR = 1  # Сходства строк
NS_WEIGHT_FACTOR = 1  # Сходства на основе NER-классов
HS_WEIGHT_FACTOR = 1  # Сходство на основе заголовка
EES_WEIGHT_FACTOR = 1  # Сходство на основе семантической близости сущностей кандидатов
CS_WEIGHT_FACTOR = 1  # Сходство на основе контекста


def get_levenshtein_distance(entity_mention, candidate_entity, underscore_replacement: bool = False,
                             short_name: bool = False):
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


def get_string_similarity(entity_mention, candidate_entities):
    """
    Вычисление оценок для сущностей из набора кандидатов по сходству строк для значения ячейки.
    :param entity_mention: текстовое упоминание сущности
    :param candidate_entities: набор сущностей кандидатов
    :return: ранжированный список сущностей кандидатов
    """
    result = dict()
    for candidate_entity in candidate_entities:
        result[candidate_entity] = get_levenshtein_distance(entity_mention, candidate_entity, True, True) * \
                                   SS_WEIGHT_FACTOR
    # Сортировка по оценкам
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

    return result


def get_ner_based_similarity(ner_class, candidate_entities):
    """
    Вычисление оценок для сущностей из набора кандидатов по сходству на основе NER-классов для значения ячейки.
    :param ner_class: NER-класс, которому соответствует значение ячейки
    :param candidate_entities: набор сущностей кандидатов
    :return: ранжированный список сущностей кандидатов
    """
    # Поиск целевого класса DBpedia на основе NER-класса
    target_classes = ""
    if ner_class == cc.LOCATION:
        target_classes = [PARK, MINE, GARDEN, WINE_REGION, NATURAL_PLACE, PROTECTED_AREA,
                          WORLD_HERITAGE_SITE, SITE_OF_SPECIAL_SCIENTIFIC_INTEREST]
    if ner_class == cc.GPE:
        target_classes = POPULATED_PLACE
    if ner_class == cc.NORP:
        target_classes = ETHNIC_GROUP
    if ner_class == cc.PERSON:
        target_classes = PERSON
    if ner_class == cc.PRODUCT:
        target_classes = [DEVICE, FOOD, MEAN_OF_TRANSPORTATION]
    if ner_class == cc.FACILITY:
        target_classes = ARCHITECTURAL_STRUCTURE
    if ner_class == cc.ORGANIZATION:
        target_classes = ORGANISATION
    if ner_class == cc.EVENT:
        target_classes = EVENT
    if ner_class == cc.ART_WORK:
        target_classes = WORK
    if ner_class == cc.LAW:
        target_classes = [LAW, LEGAL_CASE]
    result = dict()
    # Обход сущностей в наборе кандидатов
    for candidate_entity in candidate_entities:
        # Определение дистанции до целевого класса для сущности-кандидата
        distance_to_class = dbs.get_distance_to_class(candidate_entity, target_classes)
        # Определение оценки на основе дистанции до целевого класса
        result[candidate_entity] = (1 * NS_WEIGHT_FACTOR if int(distance_to_class) > 0 else 0)
    # Сортировка по оценкам
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

    return result


def get_heading_based_similarity(heading_name, candidate_entities):
    """
    Вычисление оценок для сущностей из набора кандидатов по сходству на основе заголовка столбца для значения ячейки.
    :param heading_name: название заголовка столбца
    :param candidate_entities: набор сущностей кандидатов
    :return: ранжированный список сущностей кандидатов
    """
    result = dict()
    for candidate_entity in candidate_entities:
        result[candidate_entity] = 0 * HS_WEIGHT_FACTOR
    # Сортировка по оценкам
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

    return result


def get_entity_embedding_based_semantic_similarity(table_with_candidate_entities):
    list1 = []
    dictionary_entities = {}
    total_result = {}
    for key, items in table_with_candidate_entities.items():
        if items:
            for entity_mention, candidate_entities in items.items():
                dictionary_entities.update(dict.fromkeys(candidate_entities,
                                                         [list_entities for key_entities, list_entities in items.items()
                                                          if
                                                          key_entities != entity_mention]))

                list1.append(candidate_entities)
    for keys_entities, entities in dictionary_entities.items():

        entities.append([keys_entities])
        modeller = Word2Vec(entities, vector_size=100, window=5, min_count=1, workers=4)
        modeller.save("word2vec.model")
        sims_entity = modeller.wv.most_similar(keys_entities, topn=100000)  # get other similar words
        for tuple_entities in sims_entity:
            total_result.setdefault(tuple_entities[0], []).append(tuple_entities[1])
        entities.pop()
    for key_values, precisions in total_result.items():
        maximum = max(total_result[key_values])
        total_result.update([(key_values, (maximum + 1) / 2)])
    for key, items in table_with_candidate_entities.items():
        if items:
            for keys_entities, item_items in items.items():
                if item_items:
                    dictionary = {}
                    for i in range(len(item_items)):
                        dictionary[item_items[i]] = dict()
                        dictionary[item_items[i]] = total_result[items[keys_entities][i]]
                    items[keys_entities] = dictionary
                    for key_values, item_values in items[keys_entities].items():
                        items[keys_entities][key_values] = items[keys_entities][key_values] * EES_WEIGHT_FACTOR

                    items[keys_entities] = dict(sorted(items[keys_entities].items(), key=lambda item: item[1], reverse=True))

    #result[candidate_entity] = 0 * EES_WEIGHT_FACTOR
    # Сортировка по оценкам
    #result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))
    return table_with_candidate_entities


def get_context_based_similarity(cell_context, candidate_entities):
    """
    Вычисление оценок для сущностей из набора кандидатов по сходству на основе контекста для значения ячейки.
    :param cell_context: контекст для ячейки
    :param candidate_entities: набор сущностей кандидатов
    :return: ранжированный список сущностей кандидатов
    """
    result = dict()
    for candidate_entity in candidate_entities:
        result[candidate_entity] = 0 * CS_WEIGHT_FACTOR
    # Сортировка по оценкам
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

    return result
