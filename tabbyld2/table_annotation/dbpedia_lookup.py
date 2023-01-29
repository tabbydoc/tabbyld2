import json
from typing import Dict, List

import requests
from dbpedia_sparql_endpoint import DBPediaConfig


URL = ""


def init(port=9274):
    """
    Change port to start the DBpedia Lookup service
    :param port: port number (when importing a library, port 9274 is set by default)
    :return: URL with new port
    """
    global URL
    URL = f"http://localhost:{port}/lookup-application/api/search"


def get_candidate_entities(query: str, max_results: int = None, min_relevance: int = None, short_name: bool = False) \
        -> Dict[str, List[str]]:
    """
    Get a set of candidate entities by string query
    :param query: query string
    :param max_results: maximum number of candidate entities returned in a single lookup
    :param min_relevance: minimum query relevance score
    :param short_name: flag to enable or disable short entity name display mode (without full URI)
    :return: a set of found candidate entities
    """
    results = {}
    if query != "":
        parameters = {"query": query, "format": "JSON"}
        if max_results:
            parameters["maxResults"] = max_results
        if min_relevance:
            parameters["minRelevance"] = min_relevance
        try:
            response = requests.get(url=URL, params=parameters)
            if response.status_code == 200:
                json_response = json.loads(response.text)
                for doc in json_response["docs"]:
                    key = doc["resource"][0].replace(DBPediaConfig.BASE_RESOURCE_URI, "") if short_name else doc["resource"][0]
                    redirect = []
                    if "redirectlabel" in doc:
                        redirect = [DBPediaConfig.BASE_RESOURCE_URI + rl.replace(" ", "_") for rl in doc["redirectlabel"]]
                    results[key] = [doc["label"][0] if "label" in doc else "", "", redirect]
            else:
                raise requests.exceptions.ConnectionError(f"{response.status_code}")
        except requests.exceptions.RequestException:
            print("Unexpected error in DBpedia Lookup!")
    return results


init()
