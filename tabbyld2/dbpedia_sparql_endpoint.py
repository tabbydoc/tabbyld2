import re
from typing import List
from urllib.error import URLError
from SPARQLWrapper import SPARQLWrapper, JSON
import tabbyld2.cleaner as cln


# DBpedia endpoint name
ENDPOINT_NAME = "http://dbpedia.org/sparql"


def get_candidate_entities(entity_mention: str = "", short_name: bool = False) -> List[List]:
    """
    Get a set of candidate entities based on the direct SPARQL query to DBpedia.
    :param entity_mention: a textual entity mention
    :param short_name: flag to enable or disable short entity name display mode (without full URI)
    :return: a set of candidate entities
    """
    # Split a textual entity mention into words
    string = ""
    for word in re.split(r"[\\/,.'* ]+", entity_mention.replace("&", "and")):
        if word and not cln.check_letter_and_digit_existence(word):
            string += " AND '" + word + "'" if string else "'" + word + "'"

    print("Searching for " + string)
    result_list = []
    if string != "":
        no_processing_query = True
        while no_processing_query:
            try:
                # Execute SPARQL query to DBpedia
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
                        result_list.append([result["subject"]["value"], result["label"]["value"],
                                            result["comment"]["value"]])
                no_processing_query = False
            except URLError:
                no_processing_query = True
                print("Connection error to DBpedia SPARQL Endpoint! Reconnection is carried out.")

    return result_list


def get_distance_to_class(entity: str = "", target_classes: str = None) -> int:
    """
    Get a distance to a target class of an entity based on the direct SPARQL query to DBpedia.
    :param entity: an entity from DBpedia
    :param target_classes: a set of target classes
    :return: a distance to a target class (non-negative integer including zero)
    """
    # Execute SPARQL query to DBpedia
    sparql = SPARQLWrapper(ENDPOINT_NAME)
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


def get_classes_for_entity(entity: str = "", short_name: bool = False) -> List:
    """
    Get a set of classes for an entity based on the direct SPARQL query to DBpedia.
    :param entity: an entity from DBpedia
    :param short_name: flag to enable or disable short entity name display mode (without full URI)
    :return: a set of found classes
    """
    result_list = []
    # Execute SPARQL query to DBpedia
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
