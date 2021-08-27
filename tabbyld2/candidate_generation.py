import stl.dbpedia_lookup as dbl
import stl.graphql_interface as gql


def generate_candidate_classes(class_mention):
    """
    Генерация классов кандидатов на основе текстового упоминания класса.
    :param class_mention: текстовое упоминание класса
    :return: словарь классов кандидатов для упоминания класса
    """
    result_list = dict()
    # Получение типов концептов (классов) из БЗ Talisman
    candidate_classes = gql.get_concept_types()
    if candidate_classes:
        item = []
        for candidate_class in candidate_classes:
            item.append(candidate_class["name"])
        result_list[class_mention] = item
    else:
        result_list[class_mention] = []

    return result_list


def generate_candidate_entities(entity_mention):
    """
    Генерация сущностей кандидатов на основе текстового упоминания сущности.
    :param entity_mention: текстовое упоминание сущности
    :return: словарь сущностей кандидатов для упоминания сущности
    """
    result_list = dict()
    # Получение сущностей кандидатов от сервиса DBpedia Lookup
    candidate_entities = dbl.get_entities(entity_mention, 10, None, True)
    if candidate_entities:
        result_list[entity_mention] = candidate_entities
    else:
        result_list[entity_mention] = []

    return result_list


def generate_candidate_properties(class_mention):
    """
    Генерация свойств кандидатов.
    :param class_mention: текстовое упоминание класса
    :return: словарь свойств кандидатов
    """
    result_list = dict()
    # Получение типов связей (отношений между классами) из БЗ Talisman
    candidate_properties = gql.get_concept_link_types()
    if candidate_properties:
        result_list[class_mention] = candidate_properties
    else:
        result_list[class_mention] = []

    return result_list
