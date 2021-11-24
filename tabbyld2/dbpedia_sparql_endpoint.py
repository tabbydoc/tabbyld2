from SPARQLWrapper import SPARQLWrapper, JSON


# Название конечной точки DBpedia
ENDPOINT_NAME = "http://dbpedia.org/sparql"


def get_candidate_entities(entity_mention: str = "", short_name: bool = False):
    """
    Получение набора (списка) сущностей кандидатов на основе SPARQL-запроса к DBpedia.
    :param entity_mention: текстовое упоминание сущности
    :param short_name: режим отображения короткого наименования сущности (без полного URI)
    :return: список найденных сущностей кандидатов
    """
    # Разделение текстового упоминания сущности на слова
    string = ""
    word_list = entity_mention.split()
    for word in word_list:
        if string:
            string += " AND " + word
        else:
            string = word
    # Выполнение SPARQL-запроса к DBpedia
    sparql = SPARQLWrapper(ENDPOINT_NAME)
    sparql.setQuery("""
        SELECT DISTINCT (str(?subject) as ?subject)
        WHERE {
            {
                ?subject a ?type .
                ?subject rdfs:label ?label .
                ?label <bif:contains> "%s" .
            }
            FILTER NOT EXISTS { ?subject dbo:wikiPageRedirects ?r2 } .
            FILTER (!strstarts(str(?subject), "http://dbpedia.org/resource/Category:")) .
            FILTER (!strstarts(str(?subject), "http://dbpedia.org/property/")) .
            FILTER (!strstarts(str(?subject), "http://dbpedia.org/ontology/")) .
            FILTER (strstarts(str(?type), "http://dbpedia.org/ontology/")) .
            FILTER (lang(?label) = "en")
        }
        ORDER BY ASC(strlen(?label))
        LIMIT 100
    """ % string)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # Формирование набора (списка) сущностей кандидатов
    result_list = []
    for result in results["results"]["bindings"]:
        if short_name:
            result_list.append(result["subject"]["value"].replace("http://dbpedia.org/resource/", ""))
        else:
            result_list.append(result["subject"]["value"])

    return result_list


def get_distance_to_class(candidate_entity: str = "", target_classes: str = "", short_name: bool = False):
    """
    Получение дистанции до целевого класса для сущности-кандидата на основе SPARQL-запроса к DBpedia.
    :param candidate_entity: сущность кандидат
    :param target_classes: набор целевых классов
    :param short_name: режим отображения короткого наименования класса (без полного URI)
    :return: дистанция до целевого класса (натуральное число, включая ноль)
    """
    # Выполнение SPARQL-запроса к DBpedia
    sparql = SPARQLWrapper(ENDPOINT_NAME)
    if target_classes == "":
        sparql.setQuery("""
            SELECT COUNT DISTINCT ?type
            WHERE {
                <%s> rdf:type/rdfs:subClassOf* ?type .
                ?type rdfs:subClassOf* ""
            }
        """ % candidate_entity)
    else:
        sparql.setQuery("""
            SELECT COUNT DISTINCT ?type
            WHERE {
                <%s> rdf:type/rdfs:subClassOf* ?type .
                ?type rdfs:subClassOf* ?c .
                FILTER (?c IN (%s))
            }
        """ % (candidate_entity, target_classes if isinstance(target_classes, str) else ", ".join(target_classes)))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # Определение дистанции до целевого класса
    distance_to_class = 0
    for result in results["results"]["bindings"]:
        if short_name:
            distance_to_class = result["callret-0"]["value"].replace("http://dbpedia.org/ontology/", "")
        else:
            distance_to_class = result["callret-0"]["value"]

    return distance_to_class
