import json
from typing import List

import requests


URL = ""


def init(port=9274):
    """
    Change port to start the DBpedia Lookup service.
    :param port: port number (when importing a library, port 9274 is set by default)
    :return: URL with new port
    """
    global URL
    URL = f"http://localhost:{port}/lookup-application/api/search"


def get_candidate_entities(query: str, max_results: int = None, min_relevance: int = None, short_name: bool = False) \
        -> List[List[str]]:
    """
    Get a set of candidate entities by string query.
    :param query: query string
    :param max_results: maximum number of candidate entities returned in a single lookup
    :param min_relevance: minimum query relevance score
    :param short_name: flag to enable or disable short entity name display mode (without full URI)
    :return: a set of found candidate entities
    """
    result_list = []
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
                    if short_name:
                        result_list.append([doc["resource"][0].replace("http://dbpedia.org/resource/", ""),
                                            doc["label"][0] if "label" in doc else "",
                                            doc["comment"][0] if "comment" in doc else ""])
                    else:
                        result_list.append([doc["resource"][0], doc["label"][0] if "label" in doc else "",
                                            doc["comment"][0] if "comment" in doc else ""])
                return result_list
            # else:
            #     raise requests.exceptions.ConnectionError(f"{response.status_code}")
        except requests.exceptions.RequestException as e:
            return result_list
    return result_list


init()
