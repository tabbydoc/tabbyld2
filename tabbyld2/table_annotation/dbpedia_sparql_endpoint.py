import re
from enum import Enum
from typing import Any, Dict, List, Tuple
from urllib.error import URLError

from SPARQLWrapper import JSON, SPARQLWrapper
from tabbyld2.preprocessing.cleaner import check_letter_and_digit_existence


class DBPediaConfig(str, Enum):
    ENDPOINT_NAME = "http://dbpedia.org/sparql"
    BASE_RESOURCE_URI = "http://dbpedia.org/resource/"
    BASE_ONTOLOGY_URI = "http://dbpedia.org/ontology/"


def get_redirects(entity: str) -> Tuple[str, ...]:
    """
    Get entities that are redirects to this entity
    :param entity: a target entity
    :return: a list of URI for redirect entities
    """
    sparql = SPARQLWrapper(DBPediaConfig.ENDPOINT_NAME)
    sparql.setQuery("""
        SELECT DISTINCT (str(?redirect) as ?redirect)
        WHERE {
            ?redirect dbo:wikiPageRedirects <%s> .
        }
    """ % entity)
    sparql.setReturnFormat(JSON)
    response = sparql.query().convert()
    return tuple(result["redirect"]["value"] for result in response["results"]["bindings"] if "redirect" in result)


if __name__ == "__main__":
    foo = get_redirects("http://dbpedia.org/resource/CNN-News18")
    print(foo)


def get_variable_for_query(ngrams: List[Tuple[Any, ...]]) -> str:
    """
    Get a textual variable with 'AND' and 'OR' separators for SPARQL query
    :param ngrams: N-grams of an entity mention
    :return: a variable for SPARQL query
    """
    variable = ""
    for ngram in ngrams:
        values = ""
        for value in ngram:
            if value and check_letter_and_digit_existence(value):
                values += " AND '" + value + "'" if values else "'" + value + "'"
        variable += " OR (" + values + ")" if variable else "(" + values + ")"
    return variable


def generate_ngrams(text: str, n: int) -> List[Tuple[Any, ...]]:
    """
    Split a source text into words and generate N-grams based on words
    :param text: a source text
    :param n: a value for N-grams
    :return: a list of N-grams
    """
    return list(zip(*[re.split(r"[\\/,.'* ]+", text.replace("&", "and"))[i:] for i in range(n)]))


def get_candidate_entities(entity_mention: str = "", short_name: bool = False) -> Dict[str, List[str]]:
    """
    Get a set of candidate entities based on the direct SPARQL query to DBpedia
    :param entity_mention: a textual entity mention
    :param short_name: flag to enable or disable short entity name display mode (without full URI)
    :return: a dict of candidate entities
    """
    results, processing_query, number = {}, False, len(re.split(r"[\\/,.'* ]+", entity_mention))
    while not processing_query:
        variable_query = get_variable_for_query(generate_ngrams(entity_mention, number))
        if variable_query:
            print("Searching entities for " + variable_query)
            connection_error = True
            while connection_error:
                try:
                    # Execute SPARQL query to DBpedia
                    sparql = SPARQLWrapper(DBPediaConfig.ENDPOINT_NAME)
                    sparql.setQuery("""
                        SELECT DISTINCT (str(?subject) as ?subject) (str(?label) as ?label) (str(?comment) as ?comment) (str(?rd) as ?rd)
                        WHERE {
                            {
                                ?subject rdfs:comment ?comment .
                                ?subject a ?type .
                                ?subject rdfs:label ?label .
                                ?label bif:contains "%s" .
                                OPTIONAL
                                {
                                    ?rd dbo:wikiPageRedirects ?subject .
                                }
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
                    """ % variable_query)
                    sparql.setReturnFormat(JSON)
                    response = sparql.query().convert()
                    redirects = []
                    for rs in response["results"]["bindings"]:
                        uri = rs["subject"]["value"].replace(DBPediaConfig.BASE_RESOURCE_URI, "") if short_name else rs["subject"]["value"]
                        if uri in results:
                            redirects.append(rs["rd"]["value"])
                        else:
                            redirects = [rs["rd"]["value"]] if "rd" in rs else []
                        results[uri] = [rs["label"]["value"], rs["comment"]["value"], redirects]
                    connection_error = False
                except URLError:
                    connection_error = True
                    print("Connection error to DBpedia SPARQL Endpoint! Reconnection is carried out.")
        if results or number == 0:
            processing_query = True
        else:
            processing_query = False
            number -= 1
    return results


def get_distance_to_class(entity: str = "", target_classes: str = None) -> int:
    """
    Get a distance to a target class of an entity based on the direct SPARQL query to DBpedia
    :param entity: an entity from DBpedia
    :param target_classes: a set of target classes
    :return: a distance to a target class (non-negative integer including zero)
    """
    # Execute SPARQL query to DBpedia
    sparql = SPARQLWrapper(DBPediaConfig.ENDPOINT_NAME)
    if target_classes is None:
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
    # Calculate a distance to a target class
    distance_to_class = 0
    for result in results["results"]["bindings"]:
        distance_to_class = result["callret-0"]["value"]
    return distance_to_class


def get_classes_for_entity(entity: str = "", short_name: bool = False) -> Dict[str, List]:
    """
    Get a set of classes for an entity based on the direct SPARQL query to DBpedia
    :param entity: an entity from DBpedia
    :param short_name: flag to enable or disable short entity name display mode (without full URI)
    :return: a set of found classes
    """
    result_list = {}
    # Execute SPARQL query to DBpedia
    sparql = SPARQLWrapper(DBPediaConfig.ENDPOINT_NAME)
    sparql.setQuery("""
        SELECT DISTINCT (str(?type) as ?type) (str(?label) as ?label) (str(?comment) as ?comment)
        WHERE {
            <%s> a ?type .
            ?type rdfs:label ?label .
            OPTIONAL {
                ?type rdfs:comment ?comment .
                FILTER (lang(?comment) = "en") .
            } .
            FILTER (strstarts(str(?type), "http://dbpedia.org/ontology/")) .
            FILTER (lang(?label) = "en")
        }
    """ % entity)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        result_list[result["type"]["value"].replace(DBPediaConfig.BASE_ONTOLOGY_URI, "") if short_name else
                    result["type"]["value"]] = [result["label"]["value"] if "label" in result else None,
                                                result["comment"]["value"] if "comment" in result else None]
    return result_list


def get_candidate_classes(class_mention: str = "", short_name: bool = False) -> List[List]:
    """
    Get a set of candidate classes based on the direct SPARQL query to DBpedia
    :param class_mention: a textual class mention
    :param short_name: flag to enable or disable short entity name display mode (without full URI)
    :return: a set of candidate classes
    """
    # Split a textual class mention into words
    string = ""
    for word in re.split(r"[\\/,.'* ]+", class_mention.replace("&", "and")):
        if word and check_letter_and_digit_existence(word):
            string += " AND '" + word + "'" if string else "'" + word + "'"
    print("Searching classes for " + string)
    result_list = []
    if string != "":
        no_processing_query = True
        while no_processing_query:
            try:
                # Execute SPARQL query to DBpedia
                sparql = SPARQLWrapper(DBPediaConfig.ENDPOINT_NAME)
                sparql.setQuery("""
                    SELECT DISTINCT (str(?subject) as ?subject) (str(?label) as ?label) (str(?comment) as ?comment)
                    WHERE {
                        {
                            ?subject rdf:type owl:Class .
                            ?subject rdfs:label ?label .
                            ?label <bif:contains> "%s" .
                            OPTIONAL {
                                ?subject rdfs:comment ?comment .
                                FILTER (lang(?comment) = "en") .
                            } .
                        }
                        FILTER NOT EXISTS { ?subject dbo:wikiPageRedirects ?r2 } .
                        FILTER (!strstarts(str(?subject), "http://dbpedia.org/resource/Category:")) .
                        FILTER (!strstarts(str(?subject), "http://dbpedia.org/property/")) .
                        FILTER (!strstarts(str(?subject), "http://dbpedia.org/resource/")) .
                        FILTER (lang(?label) = "en")
                    }
                    ORDER BY ASC(strlen(?label))
                    LIMIT 10
                """ % string)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                for result in results["results"]["bindings"]:
                    if short_name:
                        result_list.append([result["subject"]["value"].replace(DBPediaConfig.BASE_ONTOLOGY_URI, ""),
                                            result["label"]["value"],
                                            result["comment"]["value"] if "comment" in result else None])
                    else:
                        result_list.append([result["subject"]["value"], result["label"]["value"],
                                            result["comment"]["value"] if "comment" in result else None])
                no_processing_query = False
            except URLError:
                no_processing_query = True
                print("Connection error to DBpedia SPARQL Endpoint! Reconnection is carried out.")
    return result_list


def get_subjects_for_entity(entity: str, short_name: bool = False) -> Dict[str, List[str]]:
    results, no_processing_query = {}, True
    while no_processing_query:
        try:
            # Execute SPARQL query to DBpedia
            sparql = SPARQLWrapper(DBPediaConfig.ENDPOINT_NAME)
            sparql.setQuery("""
                SELECT DISTINCT (str(?subject) as ?subject) (str(?label) as ?label) (str(?comment) as ?comment)
                WHERE {
                    {
                        ?subject ?property <%s> .
                        ?subject rdfs:comment ?comment .
                        ?subject a ?type .
                        ?subject rdfs:label ?label .
                    }
                    FILTER NOT EXISTS { ?subject dbo:wikiPageRedirects ?r2 } .
                    FILTER (!strstarts(str(?subject), "http://dbpedia.org/resource/Category:")) .
                    FILTER (!strstarts(str(?subject), "http://dbpedia.org/property/")) .
                    FILTER (!strstarts(str(?subject), "http://dbpedia.org/ontology/")) .
                    FILTER (!strstarts(str(?property), "http://dbpedia.org/ontology/")) .
                    FILTER (strstarts(str(?type), "http://dbpedia.org/ontology/")) .
                    FILTER (lang(?label) = "en") .
                    FILTER (lang(?comment) = "en")
                }
                ORDER BY ASC(strlen(?label))
            """ % entity)
            sparql.setReturnFormat(JSON)
            response = sparql.query().convert()
            for item in response["results"]["bindings"]:
                key = item["subject"]["value"].replace(DBPediaConfig.BASE_RESOURCE_URI, "") if short_name else item["subject"]["value"]
                results[key] = [item["label"]["value"], item["comment"]["value"]]
            no_processing_query = False
        except URLError:
            no_processing_query = True
            print("Connection error to DBpedia SPARQL Endpoint! Reconnection is carried out.")
    return results


def get_objects_for_entity(entity: str, short_name: bool = False) -> Dict[str, List[str]]:
    results, no_processing_query = {}, True
    while no_processing_query:
        try:
            # Execute SPARQL query to DBpedia
            sparql = SPARQLWrapper(DBPediaConfig.ENDPOINT_NAME)
            sparql.setQuery("""
                SELECT DISTINCT (str(?object) as ?object) (str(?label) as ?label) (str(?comment) as ?comment)
                WHERE {
                    {
                        <%s> ?property ?object .
                        ?object rdfs:comment ?comment .
                        ?object a ?type .
                        ?object rdfs:label ?label .
                    }
                    FILTER NOT EXISTS { ?object dbo:wikiPageRedirects ?r2 } .
                    FILTER (!strstarts(str(?object), "http://dbpedia.org/resource/Category:")) .
                    FILTER (!strstarts(str(?object), "http://dbpedia.org/property/")) .
                    FILTER (!strstarts(str(?object), "http://dbpedia.org/ontology/")) .
                    FILTER (!strstarts(str(?property), "http://dbpedia.org/ontology/")) .
                    FILTER (strstarts(str(?type), "http://dbpedia.org/ontology/")) .
                    FILTER (lang(?label) = "en") .
                    FILTER (lang(?comment) = "en")
                }
                ORDER BY ASC(strlen(?label))
            """ % entity)
            sparql.setReturnFormat(JSON)
            response = sparql.query().convert()
            for item in response["results"]["bindings"]:
                key = item["object"]["value"].replace(DBPediaConfig.BASE_RESOURCE_URI, "") if short_name else item["object"]["value"]
                results[key] = [item["label"]["value"], item["comment"]["value"]]
            no_processing_query = False
        except URLError:
            no_processing_query = True
            print("Connection error to DBpedia SPARQL Endpoint! Reconnection is carried out.")
    return results
