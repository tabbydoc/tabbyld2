import re
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
    result_list = []
    # Разделение текстового упоминания сущности на слова
    string = ""
    text = entity_mention.replace("&", "and")
    word_list = re.split("[,' ]+", text)
    for word in word_list:
        if string:
            string += " AND '" + word + "'"
        else:
            string = "'" + word + "'"
    if string != "":
        # Выполнение SPARQL-запроса к DBpedia
        sparql = SPARQLWrapper(ENDPOINT_NAME)
        sparql.setQuery("""
            SELECT DISTINCT (str(?subject) as ?subject) (str(?label) as ?label) (str(?comment) as ?comment)
            WHERE {
                {
                    ?subject rdfs:comment ?comment .
                    ?subject a ?type .
                    ?subject rdfs:label ?label .
                    ?label <bif:contains> "%s" .
                }
                FILTER NOT EXISTS { ?subject dbo:wikiPageRedirects ?r2 } .
                FILTER (!strstarts(str(?subject), "http://dbpedia.org/resource/Category:")) .
                FILTER (!strstarts(str(?subject), "http://dbpedia.org/property/")) .
                FILTER (!strstarts(str(?subject), "http://dbpedia.org/ontology/")) .
                FILTER (strstarts(str(?type), "http://dbpedia.org/ontology/")) .
                FILTER (lang(?label) = "en") .
                FILTER (lang(?comment) = "en")
            }
            ORDER BY ASC(strlen(?label))
            LIMIT 100
        """ % string)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            if short_name:
                result_list.append([result["subject"]["value"].replace("http://dbpedia.org/resource/", ""),
                                    result["label"]["value"], result["comment"]["value"]])
            else:
                result_list.append([result["subject"]["value"], result["label"]["value"], result["comment"]["value"]])

    return result_list


def get_distance_to_class(entity: str = "", target_classes: str = ""):
    """
    Получение дистанции до целевого класса для сущности из DBpedia на основе SPARQL-запроса.
    :param entity: сущность из DBpedia
    :param target_classes: набор целевых классов
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
        """ % entity)
    else:
        sparql.setQuery("""
            SELECT COUNT DISTINCT ?type
            WHERE {
                <%s> rdf:type/rdfs:subClassOf* ?type .
                ?type rdfs:subClassOf* ?c .
                FILTER (?c IN (%s))
            }
        """ % (entity, target_classes if isinstance(target_classes, str) else ", ".join(target_classes)))
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    # Определение дистанции до целевого класса
    distance_to_class = 0
    for result in results["results"]["bindings"]:
        distance_to_class = result["callret-0"]["value"]

    return distance_to_class


def get_classes(entity: str = "", short_name: bool = False):
    """
    Получение набора (списка) классов для сущности из DBpedia на основе SPARQL-запроса.
    :param entity: сущность из DBpedia
    :param short_name: режим отображения короткого наименования класса (без полного URI)
    :return: список найденных классов
    """
    result_list = []
    # Выполнение SPARQL-запроса к DBpedia
    sparql = SPARQLWrapper(ENDPOINT_NAME)
    sparql.setQuery("""
        SELECT ?type
        WHERE {
            <%s> a ?type .
            FILTER (strstarts(str(?type), "http://dbpedia.org/ontology/"))
        }
    """ % entity)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        if short_name:
            result_list.append(result["type"]["value"].replace("http://dbpedia.org/ontology/", ""))
        else:
            result_list.append(result["type"]["value"])

    return result_list
