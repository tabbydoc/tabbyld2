import tabbyld2.dbpedia_lookup as dbl
import tabbyld2.column_classifier as cc
import tabbyld2.dbpedia_sparql_endpoint as dbs


def union_candidate_entity_lists(candidate_entities_from_sparql_endpoint, candidate_entities_from_dbl):
    """
    Объединение двух наборов сущностей кандидатов, полученных от конечной точки DBpedia SPARQL Endpoint и
    сервиса DBpedia Lookup.
    :param candidate_entities_from_sparql_endpoint: набор сущностей кандидатов, полученный от DBpedia SPARQL Endpoint
    :param candidate_entities_from_dbl: набор сущностей кандидатов, полученный от сервиса DBpedia Lookup
    :return: объединенный отсортированный список сущностей кандидатов без дубликатов
    """
    ts = set()
    rm_duplicate = lambda l: [x for x in l if not (x in ts or ts.add(x))]
    candidate_entities = rm_duplicate(candidate_entities_from_sparql_endpoint) + [i for i in rm_duplicate(
        candidate_entities_from_dbl) if i not in candidate_entities_from_sparql_endpoint]

    return candidate_entities


def generate_candidate_entities(entity_mention):
    """
    Генерация сущностей кандидатов на основе текстового упоминания сущности.
    :param entity_mention: текстовое упоминание сущности
    :return: словарь сущностей кандидатов для упоминания сущности
    """
    result_list = dict()
    # Получение сущностей кандидатов на основе конечной точки DBpedia SPARQL Endpoint
    candidate_entities_from_sparql_endpoint = dbs.get_candidate_entities(entity_mention, False)
    # Получение сущностей кандидатов от сервиса DBpedia Lookup
    candidate_entities_from_dbl = dbl.get_candidate_entities(entity_mention, 100, None, False)
    # Получение объединенного набора (списка) сущностей кандидатов
    candidate_entities = union_candidate_entity_lists(candidate_entities_from_sparql_endpoint,
                                                      candidate_entities_from_dbl)
    if candidate_entities:
        result_list[entity_mention] = candidate_entities
    else:
        result_list[entity_mention] = []

    return result_list


def get_candidate_entities_for_table(source_table, classified_table):
    """
    Получение сущностей кандидатов для всех ячеек категориальных столбцов, включая сущностный (тематический) столбец.
    :param source_table: исходный словарь (таблица) состоящий из объектов: ключ и упоминание сущности (значение ячейки)
    :param classified_table: словарь (таблица) с типизированными столбцами
    :return: словарь (таблица) с найденными сущностями кандидатами
    """
    result_list = dict()
    # Обход строк в исходной таблице
    for row in source_table:
        for key, entity_mention in row.items():
            # Обход строк в данных с классификацией столбцов
            for col_key, type_column in classified_table.items():
                if key == col_key:
                    if type_column == cc.SUBJECT_COLUMN or type_column == cc.CATEGORICAL_COLUMN:
                        print("Поиск сущностей кандидатов для ячейки '" + str(entity_mention) + "'")
                        # Генерация сущностей кандидатов на основе текстового упоминания сущности в ячейке
                        candidate_entities = generate_candidate_entities(entity_mention)
                        # Формирование словаря (таблицы) с найденными сущностями кандидатами
                        if key in result_list:
                            result_list[key].append(candidate_entities)
                        else:
                            result_list[key] = [candidate_entities]
                    else:
                        item = dict()
                        item[entity_mention] = []
                        if key in result_list:
                            result_list[key].append(item)
                        else:
                            result_list[key] = [item]

    return result_list


def generate_candidate_classes(class_mention):
    """
    Генерация классов кандидатов на основе текстового упоминания класса.
    :param class_mention: текстовое упоминание класса
    :return: словарь классов кандидатов для упоминания класса
    """
    result_list = dict()
    candidate_classes = []
    if candidate_classes:
        result_list[class_mention] = candidate_classes
    else:
        result_list[class_mention] = []

    return result_list


def generate_candidate_properties(class_mention):
    """
    Генерация свойств кандидатов.
    :param class_mention: текстовое упоминание класса
    :return: словарь свойств кандидатов
    """
    result_list = dict()
    candidate_properties = []
    if candidate_properties:
        result_list[class_mention] = candidate_properties
    else:
        result_list[class_mention] = []

    return result_list
