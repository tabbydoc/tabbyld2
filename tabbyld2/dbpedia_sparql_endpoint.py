from SPARQLWrapper import SPARQLWrapper, JSON


def get_entities(entity_mention: str = "", short_name: bool = False):
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
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
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
